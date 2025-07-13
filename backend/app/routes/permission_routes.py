from flask import request, jsonify, Blueprint
from app.models import User, OperationLog
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.result import Result
from app.auth import require_auth, require_role, require_permission
from app import db
from sqlalchemy import or_
import datetime

# 创建权限管理蓝图
permission_bp = Blueprint('permission', __name__)

@permission_bp.route('', methods=['GET'])
@require_permission('permission:list')
def get_permission_list(current_user):
    """获取权限列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword')
        module = request.args.get('module')
        permission_type = request.args.get('permission_type')
        status = request.args.get('status')
        
        query = Permission.query
        
        # 状态过滤
        if status is not None:
            query = query.filter_by(status=bool(int(status)))
        
        # 模块过滤
        if module:
            query = query.filter_by(module=module)
        
        # 类型过滤
        if permission_type:
            query = query.filter_by(permission_type=permission_type)
        
        # 关键词搜索
        if keyword:
            query = query.filter(or_(
                Permission.name.contains(keyword),
                Permission.code.contains(keyword),
                Permission.description.contains(keyword)
            ))
        
        # 分页
        pagination = query.order_by(
            Permission.module.asc(), 
            Permission.sort_order.asc(), 
            Permission.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取权限列表成功",
            data={
                'permissions': [permission.to_dict() for permission in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取权限列表失败: {str(e)}").to_dict())

@permission_bp.route('/grouped', methods=['GET'])
@require_permission('permission:list')
def get_permission_grouped(current_user):
    """获取按模块分组的权限列表"""
    try:
        status = request.args.get('status')
        status_filter = None if status is None else bool(int(status))
        
        grouped_permissions = Permission.get_grouped_by_module(status_filter)
        
        # 转换为前端需要的格式
        result = []
        for module, permissions in grouped_permissions.items():
            result.append({
                'module': module,
                'permissions': [p.to_dict() for p in permissions]
            })
        
        return jsonify(Result.success(
            message="获取分组权限列表成功",
            data=result
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取分组权限列表失败: {str(e)}").to_dict())

@permission_bp.route('/<int:permission_id>', methods=['GET'])
@require_permission('permission:detail')
def get_permission(current_user, permission_id):
    """获取单个权限信息"""
    try:
        permission = Permission.get_by_id(permission_id)
        if not permission:
            return jsonify(Result.error(message="权限不存在", code=404).to_dict())
        
        permission_dict = permission.to_dict()
        # 获取使用该权限的角色
        roles = permission.get_roles()
        permission_dict['roles'] = [{'id': r.id, 'name': r.name} for r in roles]
        
        return jsonify(Result.success(
            message="获取权限信息成功",
            data=permission_dict
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取权限信息失败: {str(e)}").to_dict())

@permission_bp.route('', methods=['POST'])
@require_permission('permission:create')
def create_permission(current_user):
    """创建权限"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查权限名称是否已存在
        if Permission.get_by_name(data['name']):
            return jsonify(Result.error(message="权限名称已存在", code=400).to_dict())
        
        # 检查权限编码是否已存在
        if Permission.get_by_code(data['code']):
            return jsonify(Result.error(message="权限编码已存在", code=400).to_dict())
        
        # 创建新权限
        permission = Permission(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            module=data.get('module'),
            permission_type=data.get('permission_type', 'button'),
            resource_path=data.get('resource_path'),
            method=data.get('method'),
            status=data.get('status', True),
            sort_order=data.get('sort_order', 0),
            created_by=current_user.id
        )
        permission.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="创建权限",
            details=f"权限名称: {permission.name}, 权限编码: {permission.code}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="权限创建成功",
            data=permission.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"权限创建失败: {str(e)}").to_dict())

@permission_bp.route('/<int:permission_id>', methods=['PUT'])
@require_permission('permission:update')
def update_permission(current_user, permission_id):
    """更新权限"""
    try:
        permission = Permission.get_by_id(permission_id)
        if not permission:
            return jsonify(Result.error(message="权限不存在", code=404).to_dict())
        
        # 检查是否为系统内置权限
        if permission.is_system:
            return jsonify(Result.error(message="系统内置权限不允许修改", code=403).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = Permission.get_by_name(data['name'])
            if existing and existing.id != permission.id:
                return jsonify(Result.error(message="权限名称已存在", code=400).to_dict())
            permission.name = data['name']
        
        if 'code' in data:
            # 检查新编码是否已存在
            existing = Permission.get_by_code(data['code'])
            if existing and existing.id != permission.id:
                return jsonify(Result.error(message="权限编码已存在", code=400).to_dict())
            permission.code = data['code']
        
        if 'description' in data:
            permission.description = data['description']
        
        if 'module' in data:
            permission.module = data['module']
        
        if 'permission_type' in data:
            permission.permission_type = data['permission_type']
        
        if 'resource_path' in data:
            permission.resource_path = data['resource_path']
        
        if 'method' in data:
            permission.method = data['method']
        
        if 'status' in data:
            permission.status = data['status']
        
        if 'sort_order' in data:
            permission.sort_order = data['sort_order']
        
        permission.updated_at = datetime.datetime.utcnow()
        permission.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="更新权限",
            details=f"权限名称: {permission.name}, 权限编码: {permission.code}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="权限更新成功",
            data=permission.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"权限更新失败: {str(e)}").to_dict())

@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@require_permission('permission:delete')
def delete_permission(current_user, permission_id):
    """删除权限"""
    try:
        permission = Permission.get_by_id(permission_id)
        if not permission:
            return jsonify(Result.error(message="权限不存在", code=404).to_dict())
        
        # 检查是否为系统内置权限
        if permission.is_system:
            return jsonify(Result.error(message="系统内置权限不允许删除", code=403).to_dict())
        
        # 检查是否有角色使用此权限
        role_count = RolePermission.query.filter_by(permission_id=permission_id).count()
        if role_count > 0:
            return jsonify(Result.error(message=f"该权限被 {role_count} 个角色使用，不能删除", code=400).to_dict())
        
        permission_name = permission.name
        permission.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="删除权限",
            details=f"权限名称: {permission_name}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="权限删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"权限删除失败: {str(e)}").to_dict())

@permission_bp.route('/all', methods=['GET'])
@require_auth
def get_all_permissions(current_user):
    """获取所有启用的权限（用于分配权限）"""
    try:
        permissions = Permission.get_all_active()
        grouped_permissions = Permission.get_grouped_by_module(status=True)
        
        # 转换为树结构
        result = []
        for module, permissions in grouped_permissions.items():
            result.append({
                'module': module,
                'permissions': [{'id': p.id, 'name': p.name, 'code': p.code, 'permission_type': p.permission_type} for p in permissions]
            })
        
        return jsonify(Result.success(
            message="获取权限列表成功",
            data=result
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取权限列表失败: {str(e)}").to_dict())

@permission_bp.route('/modules', methods=['GET'])
@require_auth
def get_permission_modules(current_user):
    """获取权限模块列表"""
    try:
        modules = db.session.query(Permission.module).filter(
            Permission.module.isnot(None),
            Permission.status == True
        ).distinct().all()
        
        module_list = [module[0] for module in modules if module[0]]
        
        return jsonify(Result.success(
            message="获取权限模块成功",
            data=module_list
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取权限模块失败: {str(e)}").to_dict())

@permission_bp.route('/batch-operation', methods=['POST'])
@require_permission('permission:batch')
def batch_permission_operation(current_user):
    """批量权限操作"""
    try:
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        operation = data.get('operation')
        
        if not permission_ids or not operation:
            return jsonify(Result.error(message="权限ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for permission_id in permission_ids:
            try:
                permission = Permission.get_by_id(permission_id)
                if not permission:
                    results.append({"permission_id": permission_id, "status": "failed", "message": "权限不存在"})
                    failed_count += 1
                    continue
                
                if permission.is_system:
                    results.append({"permission_id": permission_id, "status": "failed", "message": "系统内置权限不允许操作"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    # 检查是否有角色使用此权限
                    role_count = RolePermission.query.filter_by(permission_id=permission_id).count()
                    if role_count > 0:
                        results.append({"permission_id": permission_id, "status": "failed", "message": f"该权限被 {role_count} 个角色使用"})
                        failed_count += 1
                        continue
                    permission.delete()
                elif operation == 'enable':
                    permission.status = True
                    permission.save()
                elif operation == 'disable':
                    permission.status = False
                    permission.save()
                else:
                    results.append({"permission_id": permission_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"permission_id": permission_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"permission_id": permission_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="批量权限操作",
            details=f"操作: {operation}, 成功: {success_count}, 失败: {failed_count}",
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