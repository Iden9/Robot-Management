from flask import request, jsonify, Blueprint
from werkzeug.security import generate_password_hash
from app.models import User, OperationLog, UserSession
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_
import datetime

# 创建用户蓝图
user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
@require_auth
def get_users(current_user):
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = User.query
        
        # 搜索过滤
        if search:
            query = query.filter(or_(
                User.username.contains(search),
                User.real_name.contains(search),
                User.email.contains(search),
                User.phone.contains(search)
            ))
        
        # 角色过滤
        if role:
            query = query.filter_by(role=role)
        
        # 状态过滤
        if status is not None:
            query = query.filter_by(status=bool(int(status)))
        
        # 按创建时间排序
        query = query.order_by(User.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 获取用户在线状态
        users_data = []
        for user in pagination.items:
            user_dict = user.to_dict()
            # 检查是否有活跃会话
            active_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            user_dict['is_online'] = len(active_sessions) > 0
            user_dict['active_sessions'] = len(active_sessions)
            users_data.append(user_dict)
        
        return jsonify(Result.success(
            message="获取用户列表成功",
            data={
                'users': users_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户列表失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(current_user, user_id):
    """获取单个用户信息"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取用户信息成功",
            data=user.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户信息失败: {str(e)}").to_dict())

@user_bp.route('', methods=['POST'])
@require_role(['admin'])
def create_user(current_user):
    """创建用户"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['username', 'password', 'real_name', 'role']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查用户名是否已存在
        if User.get_by_username(data['username']):
            return jsonify(Result.error(message="用户名已存在", code=400).to_dict())
        
        # 创建新用户
        user = User(
            username=data['username'],
            real_name=data['real_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            role=data['role'],
            status=data.get('status', True)
        )
        user.set_password(data['password'])
        user.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"创建用户: {user.username}",
            details=f"用户ID: {user.id}, 角色: {user.role}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="用户创建成功",
            data=user.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"用户创建失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>', methods=['PUT'])
@require_role(['admin'])
def update_user(current_user, user_id):
    """更新用户信息"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'real_name' in data:
            user.real_name = data['real_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data:
            user.role = data['role']
        if 'role_id' in data:
            user.role_id = data['role_id']
        if 'status' in data:
            user.status = data['status']
        
        user.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"更新用户: {user.username}",
            details=f"用户ID: {user.id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="用户更新成功",
            data=user.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"用户更新失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_user(current_user, user_id):
    """删除用户"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        # 不能删除自己
        if user.id == current_user.id:
            return jsonify(Result.error(message="不能删除自己", code=400).to_dict())
        
        username = user.username
        user.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"删除用户: {username}",
            details=f"用户ID: {user_id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="用户删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"用户删除失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@require_role(['admin'])
def reset_password(current_user, user_id):
    """重置用户密码"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        data = request.get_json()
        new_password = data.get('new_password', '123456')  # 默认密码
        
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"重置密码: {user.username}",
            details=f"用户ID: {user.id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="密码重置成功",
            data={"new_password": new_password}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"密码重置失败: {str(e)}").to_dict())

@user_bp.route('/search', methods=['GET'])
@require_auth
def search_users(current_user):
    """搜索用户"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空", code=400).to_dict())
        
        users = User.search_by_keyword(keyword)
        
        return jsonify(Result.success(
            message="搜索用户成功",
            data=[user.to_dict() for user in users]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"搜索用户失败: {str(e)}").to_dict())

@user_bp.route('/statistics', methods=['GET'])
@require_role(['admin'])
def get_user_statistics(current_user):
    """获取用户统计信息"""
    try:
        # 用户角色统计
        role_stats = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
        
        # 用户状态统计
        status_stats = db.session.query(User.status, db.func.count(User.id)).group_by(User.status).all()
        
        # 最近注册用户
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        # 在线用户统计
        online_count = 0
        for user in User.get_all():
            active_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            if active_sessions:
                online_count += 1
        
        return jsonify(Result.success(
            message="获取用户统计成功",
            data={
                "total_users": User.get_total_count(),
                "role_distribution": dict(role_stats),
                "status_distribution": dict(status_stats),
                "online_users": online_count,
                "recent_users": [user.to_dict() for user in recent_users]
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户统计失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>/sessions', methods=['GET'])
@require_role(['admin'])
def get_user_sessions(current_user, user_id):
    """获取指定用户的会话列表"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        sessions = UserSession.get_user_sessions(user_id, active_only=False)
        
        return jsonify(Result.success(
            message="获取用户会话成功",
            data=[session.to_dict() for session in sessions]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户会话失败: {str(e)}").to_dict())

@user_bp.route('/<int:user_id>/force-logout', methods=['POST'])
@require_role(['admin'])
def force_logout_user(current_user, user_id):
    """强制用户下线"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        # 使所有用户会话失效
        count = UserSession.invalidate_user_sessions(user_id)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='config',
            action=f"强制下线用户: {user.username}",
            target_type='user',
            target_id=str(user_id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"已强制用户下线，终止了 {count} 个会话",
            data={"terminated_sessions": count}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"强制下线失败: {str(e)}").to_dict())

@user_bp.route('/batch-delete', methods=['POST'])
@require_role(['admin'])
def batch_delete_users(current_user):
    """批量删除用户"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify(Result.error(message="请选择要删除的用户", code=400).to_dict())
        
        # 不能删除自己
        if current_user.id in user_ids:
            return jsonify(Result.error(message="不能删除自己", code=400).to_dict())
        
        deleted_count = 0
        deleted_users = []
        
        for user_id in user_ids:
            user = User.get_by_id(user_id)
            if user:
                deleted_users.append(user.username)
                user.delete()
                deleted_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='delete',
            action=f"批量删除用户: {', '.join(deleted_users)}",
            details=f"删除了 {deleted_count} 个用户",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"批量删除成功，共删除 {deleted_count} 个用户",
            data={"deleted_count": deleted_count, "deleted_users": deleted_users}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"批量删除失败: {str(e)}").to_dict())
