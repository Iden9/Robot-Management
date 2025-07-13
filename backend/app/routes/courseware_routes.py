from flask import request, jsonify, Blueprint, send_file
from app.models import Courseware, OperationLog, CoursewareCategory, CoursewareUsage
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename
import os
import datetime
import uuid
import mimetypes

# 创建课件蓝图
courseware_bp = Blueprint('courseware', __name__)

# 文件上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'courseware')
ALLOWED_EXTENSIONS = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.mp4', '.mp3', '.jpg', '.png', '.jpeg', '.gif', '.zip', '.rar']
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

def get_file_size(file):
    """获取文件大小"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

@courseware_bp.route('/upload', methods=['POST'])
@require_role(['admin', 'operator'])
def upload_courseware(current_user):
    """上传课件文件"""
    try:
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            return jsonify(Result.error(message="请选择要上传的文件", code=400).to_dict())
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify(Result.error(message="请选择要上传的文件", code=400).to_dict())
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify(Result.error(message="不支持的文件类型", code=400).to_dict())
        
        # 检查文件大小
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify(Result.error(message="文件大小超出限制（最大100MB）", code=400).to_dict())
        
        # 获取其他表单数据
        title = request.form.get('title')
        description = request.form.get('description', '')
        category_id = request.form.get('category_id')
        tags = request.form.get('tags', '')
        
        # 如果没有提供标题，使用文件名
        if not title:
            title = os.path.splitext(file.filename)[0]
        
        # 检查标题是否已存在
        if Courseware.get_by_title(title):
            return jsonify(Result.error(message="课件标题已存在", code=400).to_dict())
        
        # 验证分类ID
        if category_id:
            category = CoursewareCategory.get_by_id(int(category_id))
            if not category:
                return jsonify(Result.error(message="课件分类不存在", code=400).to_dict())
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 构建完整的文件路径
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 获取文件MIME类型
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # 创建课件记录
        courseware = Courseware(
            title=title,
            file_path=file_path,
            file_name=filename,
            file_type=file_ext[1:],  # 去掉点号
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            category_id=int(category_id) if category_id else None,
            tags=tags,
            status='published',  # 修改为正确的枚举值
            uploaded_by=current_user.id
        )
        courseware.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware.id,
            operation=f"上传课件: {title}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="课件上传成功",
            data=courseware.to_dict()
        ).to_dict())
        
    except Exception as e:
        # 如果保存文件失败，清理已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify(Result.error(message=f"课件上传失败: {str(e)}").to_dict())

@courseware_bp.route('', methods=['GET'])
@require_auth
def get_courseware_list(current_user):
    """获取课件列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        file_type = request.args.get('file_type')
        keyword = request.args.get('keyword')
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        
        query = Courseware.query
        
        # 文件类型过滤
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        # 分类过滤
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 关键词搜索
        if keyword:
            query = query.filter(or_(
                Courseware.title.contains(keyword),
                Courseware.description.contains(keyword)
            ))
        
        # 分页
        pagination = query.order_by(Courseware.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 获取详细信息
        courseware_data = []
        for cw in pagination.items:
            cw_dict = cw.to_dict()
            # 获取分类信息
            if cw.category:
                cw_dict['category'] = cw.category.to_dict()
            # 获取使用统计
            usage_count = CoursewareUsage.query.filter_by(courseware_id=cw.id).count()
            cw_dict['usage_count'] = usage_count
            courseware_data.append(cw_dict)
        
        return jsonify(Result.success(
            message="获取课件列表成功",
            data={
                'courseware': courseware_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取课件列表失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>', methods=['GET'])
@require_auth
def get_courseware(current_user, courseware_id):
    """获取单个课件信息"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取课件信息成功",
            data=courseware.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取课件信息失败: {str(e)}").to_dict())

@courseware_bp.route('', methods=['POST'])
@require_role(['admin', 'operator'])
def create_courseware(current_user):
    """创建课件"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['title', 'file_path', 'file_type', 'file_size']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查标题是否已存在
        if Courseware.get_by_title(data['title']):
            return jsonify(Result.error(message="课件标题已存在", code=400).to_dict())
        
        # 验证分类ID
        if data.get('category_id'):
            category = CoursewareCategory.get_by_id(data['category_id'])
            if not category:
                return jsonify(Result.error(message="课件分类不存在", code=400).to_dict())
        
        # 创建新课件
        courseware = Courseware(
            title=data['title'],
            file_path=data['file_path'],
            file_type=data['file_type'],
            file_size=data['file_size'],
            description=data.get('description'),
            category_id=data.get('category_id'),
            tags=data.get('tags'),
            status=data.get('status', 'published'),  # 修改默认值
            uploaded_by=current_user.id
        )
        courseware.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware.id,
            operation="上传课件",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="课件创建成功",
            data=courseware.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"课件创建失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_courseware(current_user, courseware_id):
    """更新课件信息"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'title' in data:
            # 检查新标题是否已存在
            existing = Courseware.get_by_title(data['title'])
            if existing and existing.id != courseware.id:
                return jsonify(Result.error(message="课件标题已存在", code=400).to_dict())
            courseware.title = data['title']
        
        if 'description' in data:
            courseware.description = data['description']
        
        if 'category_id' in data:
            if data['category_id']:
                category = CoursewareCategory.get_by_id(data['category_id'])
                if not category:
                    return jsonify(Result.error(message="课件分类不存在", code=400).to_dict())
            courseware.category_id = data['category_id']
        
        if 'tags' in data:
            courseware.tags = data['tags']
        
        if 'status' in data:
            courseware.status = data['status']
        
        courseware.updated_at = datetime.datetime.utcnow()
        courseware.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware.id,
            operation="更新课件信息",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="课件更新成功",
            data=courseware.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"课件更新失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_courseware(current_user, courseware_id):
    """删除课件"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        # 检查权限：只有管理员或课件上传者可以删除
        if current_user.role != 'admin' and courseware.uploaded_by != current_user.id:
            return jsonify(Result.error(message="没有权限删除此课件", code=403).to_dict())
        
        title = courseware.title
        courseware.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware_id,
            operation=f"删除课件: {title}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="课件删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"课件删除失败: {str(e)}").to_dict())

@courseware_bp.route('/types', methods=['GET'])
@require_auth
def get_file_types(current_user):
    """获取课件文件类型统计"""
    try:
        from sqlalchemy import func
        from app import db
        
        result = db.session.query(
            Courseware.file_type,
            func.count(Courseware.id).label('count')
        ).group_by(Courseware.file_type).all()
        
        file_types = [{'type': row[0], 'count': row[1]} for row in result]
        
        return jsonify(Result.success(
            message="获取文件类型统计成功",
            data=file_types
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取文件类型统计失败: {str(e)}").to_dict())

@courseware_bp.route('/search', methods=['GET'])
@require_auth
def search_courseware(current_user):
    """搜索课件"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空", code=400).to_dict())
        
        courseware_list = Courseware.search_by_title(keyword)
        
        return jsonify(Result.success(
            message="搜索课件成功",
            data=[cw.to_dict() for cw in courseware_list]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"搜索课件失败: {str(e)}").to_dict())

# 课件分类管理
@courseware_bp.route('/categories', methods=['GET'])
@require_auth
def get_courseware_categories(current_user):
    """获取课件分类列表"""
    try:
        categories = CoursewareCategory.get_all()
        categories_data = []
        
        for category in categories:
            category_dict = category.to_dict()
            # 获取该分类下的课件数量
            courseware_count = Courseware.query.filter_by(category_id=category.id).count()
            category_dict['courseware_count'] = courseware_count
            categories_data.append(category_dict)
        
        return jsonify(Result.success(
            message="获取分类列表成功",
            data=categories_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取分类列表失败: {str(e)}").to_dict())

@courseware_bp.route('/categories', methods=['POST'])
@require_role(['admin', 'operator'])
def create_courseware_category(current_user):
    """创建课件分类"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data or not data.get('name'):
            return jsonify(Result.error(message="分类名称不能为空", code=400).to_dict())
        
        # 检查分类名称是否已存在
        if CoursewareCategory.get_by_name(data['name']):
            return jsonify(Result.error(message="分类名称已存在", code=400).to_dict())
        
        # 创建新分类
        category = CoursewareCategory(
            name=data['name'],
            description=data.get('description'),
            color=data.get('color'),
            icon=data.get('icon'),
            created_by=current_user.id
        )
        category.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='create',
            action=f"创建课件分类: {category.name}",
            target_type='courseware_category',
            target_id=str(category.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="分类创建成功",
            data=category.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"分类创建失败: {str(e)}").to_dict())

@courseware_bp.route('/categories/<int:category_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_courseware_category(current_user, category_id):
    """更新课件分类"""
    try:
        category = CoursewareCategory.get_by_id(category_id)
        if not category:
            return jsonify(Result.error(message="分类不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = CoursewareCategory.get_by_name(data['name'])
            if existing and existing.id != category.id:
                return jsonify(Result.error(message="分类名称已存在", code=400).to_dict())
            category.name = data['name']
        
        if 'description' in data:
            category.description = data['description']
        
        if 'color' in data:
            category.color = data['color']
        
        if 'icon' in data:
            category.icon = data['icon']
        
        category.updated_at = datetime.datetime.utcnow()
        category.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='update',
            action=f"更新课件分类: {category.name}",
            target_type='courseware_category',
            target_id=str(category.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="分类更新成功",
            data=category.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"分类更新失败: {str(e)}").to_dict())

@courseware_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_courseware_category(current_user, category_id):
    """删除课件分类"""
    try:
        category = CoursewareCategory.get_by_id(category_id)
        if not category:
            return jsonify(Result.error(message="分类不存在", code=404).to_dict())
        
        # 检查是否有课件使用此分类
        courseware_count = Courseware.query.filter_by(category_id=category_id).count()
        if courseware_count > 0:
            return jsonify(Result.error(message=f"该分类下还有 {courseware_count} 个课件，不能删除", code=400).to_dict())
        
        category_name = category.name
        category.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='delete',
            action=f"删除课件分类: {category_name}",
            target_type='courseware_category',
            target_id=str(category_id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="分类删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"分类删除失败: {str(e)}").to_dict())

# 课件使用统计
@courseware_bp.route('/<int:courseware_id>/usage', methods=['POST'])
@require_auth
def record_courseware_usage(current_user, courseware_id):
    """记录课件使用"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        data = request.get_json()
        equipment_id = data.get('equipment_id', 'WEB-CLIENT')  # 默认设备ID为网页客户端
        action = data.get('action', 'view')  # view, download, play
        duration = data.get('duration', 0)  # 使用时长（秒）
        
        # 记录使用记录
        usage = CoursewareUsage(
            courseware_id=courseware_id,
            user_id=current_user.id,
            equipment_id=equipment_id,
            action=action,
            duration=duration,
            ip_address=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        )
        usage.save()
        
        # 更新课件使用统计
        courseware.view_count = (courseware.view_count or 0) + 1
        if action == 'download':
            courseware.download_count = (courseware.download_count or 0) + 1
        courseware.save()
        
        return jsonify(Result.success(
            message="使用记录已保存",
            data=usage.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"记录使用失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>/usage', methods=['GET'])
@require_auth
def get_courseware_usage(current_user, courseware_id):
    """获取课件使用统计"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        action = request.args.get('action')
        
        query = CoursewareUsage.query.filter_by(courseware_id=courseware_id)
        
        if action:
            query = query.filter_by(action=action)
        
        pagination = query.order_by(CoursewareUsage.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 统计数据
        total_views = CoursewareUsage.query.filter_by(
            courseware_id=courseware_id, 
            action='view'
        ).count()
        total_downloads = CoursewareUsage.query.filter_by(
            courseware_id=courseware_id, 
            action='download'
        ).count()
        unique_users = db.session.query(CoursewareUsage.user_id).filter_by(
            courseware_id=courseware_id
        ).distinct().count()
        
        return jsonify(Result.success(
            message="获取使用统计成功",
            data={
                'usage_records': [usage.to_dict() for usage in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'statistics': {
                    'total_views': total_views,
                    'total_downloads': total_downloads,
                    'unique_users': unique_users
                }
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取使用统计失败: {str(e)}").to_dict())

# 文件下载
@courseware_bp.route('/<int:courseware_id>/download', methods=['GET'])
@require_auth
def download_courseware(current_user, courseware_id):
    """下载课件文件"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        # 检查文件是否存在
        if not os.path.exists(courseware.file_path):
            return jsonify(Result.error(message="文件不存在", code=404).to_dict())
        
        # 记录下载使用
        equipment_id = request.args.get('equipment_id', 'WEB-CLIENT')  # 默认设备ID为网页客户端
        usage = CoursewareUsage(
            courseware_id=courseware_id,
            user_id=current_user.id,
            equipment_id=equipment_id,
            action='download',
            ip_address=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        )
        usage.save()
        
        # 更新下载统计
        courseware.download_count = (courseware.download_count or 0) + 1
        courseware.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware_id,
            operation="下载课件",
            ip_address=client_ip
        )
        
        return send_file(
            courseware.file_path,
            as_attachment=True,
            download_name=courseware.title + '.' + courseware.file_type
        )
        
    except Exception as e:
        return jsonify(Result.error(message=f"文件下载失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>/preview', methods=['GET'])
def preview_courseware(courseware_id):
    """预览课件文件"""
    try:
        # 身份验证 - 支持从URL参数或Header中获取token
        from app.auth import verify_token
        
        # 优先从Header获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # 如果Header中没有，尝试从URL参数获取
        if not token:
            token = request.args.get('token', '')
        
        if not token:
            return jsonify(Result.error(message="需要认证", code=401).to_dict())
        
        current_user = verify_token(token)
        if not current_user:
            return jsonify(Result.error(message="无效的Token", code=401).to_dict())
        
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        # 检查文件是否存在
        if not os.path.exists(courseware.file_path):
            return jsonify(Result.error(message="文件不存在", code=404).to_dict())
        
        # 记录预览使用
        equipment_id = request.args.get('equipment_id', 'WEB-CLIENT')  # 默认设备ID为网页客户端
        usage = CoursewareUsage(
            courseware_id=courseware_id,
            user_id=current_user.id,
            equipment_id=equipment_id,
            action='view',
            ip_address=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        )
        usage.save()
        
        # 更新查看统计
        courseware.view_count = (courseware.view_count or 0) + 1
        courseware.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_courseware_operation(
            user_id=current_user.id,
            courseware_id=courseware_id,
            operation="预览课件",
            ip_address=client_ip
        )
        
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(courseware.file_path)
        if not mime_type:
            # 根据文件扩展名设置MIME类型
            file_ext = os.path.splitext(courseware.file_path)[1].lower()
            mime_types_map = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.mp4': 'video/mp4',
                '.mp3': 'audio/mpeg',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            mime_type = mime_types_map.get(file_ext, 'application/octet-stream')
        
        # 对于可以在浏览器中直接预览的文件类型，设置为内联显示
        previewable_types = [
            'application/pdf',
            'image/jpeg',
            'image/png', 
            'image/gif',
            'video/mp4',
            'audio/mpeg'
        ]
        
        if mime_type in previewable_types:
            # 直接返回文件用于预览
            return send_file(
                courseware.file_path,
                mimetype=mime_type,
                as_attachment=False,  # 关键：不作为附件，允许浏览器内联预览
                download_name=courseware.title + '.' + courseware.file_type
            )
        else:
            # 对于不支持直接预览的文件，返回预览信息
            file_size = os.path.getsize(courseware.file_path)
            return jsonify(Result.success(
                message="获取预览信息成功",
                data={
                    "preview_type": "info",
                    "file_name": courseware.title,
                    "file_type": courseware.file_type,
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "message": "该文件类型不支持在线预览，请下载后查看",
                    "download_url": f"/api/courseware/{courseware_id}/download"
                }
            ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"文件预览失败: {str(e)}").to_dict())

@courseware_bp.route('/<int:courseware_id>/preview-info', methods=['GET'])
@require_auth
def get_courseware_preview_info(current_user, courseware_id):
    """获取课件预览信息（不返回文件本身）"""
    try:
        courseware = Courseware.get_by_id(courseware_id)
        if not courseware:
            return jsonify(Result.error(message="课件不存在", code=404).to_dict())
        
        # 检查文件是否存在
        if not os.path.exists(courseware.file_path):
            return jsonify(Result.error(message="文件不存在", code=404).to_dict())
        
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(courseware.file_path)
        if not mime_type:
            # 根据文件扩展名设置MIME类型
            file_ext = os.path.splitext(courseware.file_path)[1].lower()
            mime_types_map = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.mp4': 'video/mp4',
                '.mp3': 'audio/mpeg',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            mime_type = mime_types_map.get(file_ext, 'application/octet-stream')
        
        # 对于可以在浏览器中直接预览的文件类型
        previewable_types = [
            'application/pdf',
            'image/jpeg',
            'image/png', 
            'image/gif',
            'video/mp4',
            'audio/mpeg'
        ]
        
        if mime_type in previewable_types:
            # 返回可预览标识，前端会直接构建预览URL
            return jsonify(Result.success(
                message="文件支持在线预览",
                data={
                    "preview_type": "direct",
                    "file_type": courseware.file_type,
                    "mime_type": mime_type,
                    "preview_url": f"/api/courseware/{courseware_id}/preview"
                }
            ).to_dict())
        else:
            # 对于不支持直接预览的文件，返回预览信息
            file_size = os.path.getsize(courseware.file_path)
            return jsonify(Result.success(
                message="获取预览信息成功",
                data={
                    "preview_type": "info",
                    "file_name": courseware.title,
                    "file_type": courseware.file_type,
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "message": "该文件类型不支持在线预览，请下载后查看",
                    "download_url": f"/api/courseware/{courseware_id}/download"
                }
            ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取预览信息失败: {str(e)}").to_dict())

# 批量操作
@courseware_bp.route('/batch-operation', methods=['POST'])
@require_role(['admin', 'operator'])
def batch_courseware_operation(current_user):
    """批量课件操作"""
    try:
        data = request.get_json()
        courseware_ids = data.get('courseware_ids', [])
        operation = data.get('operation')
        
        if not courseware_ids or not operation:
            return jsonify(Result.error(message="课件ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for courseware_id in courseware_ids:
            try:
                courseware = Courseware.get_by_id(courseware_id)
                if not courseware:
                    results.append({"courseware_id": courseware_id, "status": "failed", "message": "课件不存在"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    courseware.delete()
                elif operation == 'activate':
                    courseware.status = 'published'  # 修改为正确的枚举值
                    courseware.save()
                elif operation == 'deactivate':
                    courseware.status = 'archived'  # 修改为正确的枚举值
                    courseware.save()
                elif operation == 'change_category':
                    category_id = data.get('category_id')
                    if category_id:
                        category = CoursewareCategory.get_by_id(category_id)
                        if not category:
                            results.append({"courseware_id": courseware_id, "status": "failed", "message": "分类不存在"})
                            failed_count += 1
                            continue
                        courseware.category_id = category_id
                        courseware.save()
                else:
                    results.append({"courseware_id": courseware_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"courseware_id": courseware_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"courseware_id": courseware_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='config',
            action=f"批量课件操作: {operation}",
            details=f"成功: {success_count}, 失败: {failed_count}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"批量操作完成，成功: {success_count}, 失败: {failed_count}",
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"批量操作失败: {str(e)}").to_dict())
