from flask import request, jsonify, Blueprint
from app.models import User, OperationLog
from app.models.role import Role, RolePermission
from app.models.permission import Permission
from app.models.result import Result
from app.auth import require_auth, require_role, require_permission
from app import db
from sqlalchemy import or_
import datetime

# 创建角色管理蓝图
role_bp = Blueprint('role', __name__)

@role_bp.route('', methods=['GET'])
@require_permission('role:list')
def get_role_list(current_user):
    """获取角色列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword')
        status = request.args.get('status')
        
        query = Role.query
        
        # 状态过滤
        if status is not None:
            query = query.filter_by(status=bool(int(status)))
        
        # 关键词搜索
        if keyword:
            query = query.filter(or_(
                Role.name.contains(keyword),
                Role.code.contains(keyword),
                Role.description.contains(keyword)
            ))
        
        # 分页
        pagination = query.order_by(Role.sort_order.asc(), Role.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        roles_data = []
        for role in pagination.items:
            role_dict = role.to_dict()
            # 获取权限信息
            permissions = role.get_permissions()
            role_dict['permissions'] = [p.to_dict() for p in permissions]
            roles_data.append(role_dict)
        
        return jsonify(Result.success(
            message="获取角色列表成功",
            data={
                'roles': roles_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取角色列表失败: {str(e)}").to_dict())

@role_bp.route('/<int:role_id>', methods=['GET'])
@require_permission('role:detail')
def get_role(current_user, role_id):
    """获取单个角色信息"""
    try:
        role = Role.get_by_id(role_id)
        if not role:
            return jsonify(Result.error(message="角色不存在", code=404).to_dict())
        
        role_dict = role.to_dict()
        # 获取权限信息
        permissions = role.get_permissions()
        role_dict['permissions'] = [p.to_dict() for p in permissions]
        
        return jsonify(Result.success(
            message="获取角色信息成功",
            data=role_dict
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取角色信息失败: {str(e)}").to_dict())

@role_bp.route('', methods=['POST'])
@require_permission('role:create')
def create_role(current_user):
    """创建角色"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查角色名称是否已存在
        if Role.get_by_name(data['name']):
            return jsonify(Result.error(message="角色名称已存在", code=400).to_dict())
        
        # 检查角色编码是否已存在
        if Role.get_by_code(data['code']):
            return jsonify(Result.error(message="角色编码已存在", code=400).to_dict())
        
        # 创建新角色
        role = Role(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            status=data.get('status', True),
            sort_order=data.get('sort_order', 0),
            created_by=current_user.id
        )
        role.save()
        
        # 分配权限
        permission_ids = data.get('permission_ids', [])
        for permission_id in permission_ids:
            role.assign_permission(permission_id)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="创建角色",
            details=f"角色名称: {role.name}, 角色编码: {role.code}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="角色创建成功",
            data=role.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"角色创建失败: {str(e)}").to_dict())

@role_bp.route('/<int:role_id>', methods=['PUT'])
@require_permission('role:update')
def update_role(current_user, role_id):
    """更新角色"""
    try:
        role = Role.get_by_id(role_id)
        if not role:
            return jsonify(Result.error(message="角色不存在", code=404).to_dict())
        
        # 检查是否为系统内置角色
        if role.is_system:
            return jsonify(Result.error(message="系统内置角色不允许修改", code=403).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = Role.get_by_name(data['name'])
            if existing and existing.id != role.id:
                return jsonify(Result.error(message="角色名称已存在", code=400).to_dict())
            role.name = data['name']
        
        if 'code' in data:
            # 检查新编码是否已存在
            existing = Role.get_by_code(data['code'])
            if existing and existing.id != role.id:
                return jsonify(Result.error(message="角色编码已存在", code=400).to_dict())
            role.code = data['code']
        
        if 'description' in data:
            role.description = data['description']
        
        if 'status' in data:
            role.status = data['status']
        
        if 'sort_order' in data:
            role.sort_order = data['sort_order']
        
        role.updated_at = datetime.datetime.utcnow()
        role.save()
        
        # 更新权限
        if 'permission_ids' in data:
            # 删除现有权限
            RolePermission.query.filter_by(role_id=role.id).delete()
            
            # 分配新权限
            permission_ids = data['permission_ids']
            for permission_id in permission_ids:
                role.assign_permission(permission_id)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="更新角色",
            details=f"角色名称: {role.name}, 角色编码: {role.code}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="角色更新成功",
            data=role.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"角色更新失败: {str(e)}").to_dict())

@role_bp.route('/<int:role_id>', methods=['DELETE'])
@require_permission('role:delete')
def delete_role(current_user, role_id):
    """删除角色"""
    try:
        role = Role.get_by_id(role_id)
        if not role:
            return jsonify(Result.error(message="角色不存在", code=404).to_dict())
        
        # 检查是否为系统内置角色
        if role.is_system:
            return jsonify(Result.error(message="系统内置角色不允许删除", code=403).to_dict())
        
        # 检查是否有用户使用此角色
        user_count = User.query.filter_by(role_id=role_id).count()
        if user_count > 0:
            return jsonify(Result.error(message=f"该角色下还有 {user_count} 个用户，不能删除", code=400).to_dict())
        
        role_name = role.name
        role.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="删除角色",
            details=f"角色名称: {role_name}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="角色删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"角色删除失败: {str(e)}").to_dict())

@role_bp.route('/all', methods=['GET'])
@require_auth
def get_all_roles(current_user):
    """获取所有启用的角色（用于下拉选择）"""
    try:
        roles = Role.get_all_active()
        roles_data = [{'id': role.id, 'name': role.name, 'code': role.code} for role in roles]
        
        return jsonify(Result.success(
            message="获取角色列表成功",
            data=roles_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取角色列表失败: {str(e)}").to_dict())

@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@require_permission('role:detail')
def get_role_permissions(current_user, role_id):
    """获取角色权限"""
    try:
        role = Role.get_by_id(role_id)
        if not role:
            return jsonify(Result.error(message="角色不存在", code=404).to_dict())
        
        permissions = role.get_permissions()
        permissions_data = [p.to_dict() for p in permissions]
        
        return jsonify(Result.success(
            message="获取角色权限成功",
            data=permissions_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取角色权限失败: {str(e)}").to_dict())

@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@require_permission('role:permission')
def assign_role_permissions(current_user, role_id):
    """分配角色权限"""
    try:
        role = Role.get_by_id(role_id)
        if not role:
            return jsonify(Result.error(message="角色不存在", code=404).to_dict())
        
        # 检查是否为系统内置角色
        if role.is_system:
            return jsonify(Result.error(message="系统内置角色不允许修改权限", code=403).to_dict())
        
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        
        # 删除现有权限
        RolePermission.query.filter_by(role_id=role.id).delete()
        
        # 分配新权限
        for permission_id in permission_ids:
            permission = Permission.get_by_id(permission_id)
            if permission:
                role.assign_permission(permission_id)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="分配角色权限",
            details=f"角色: {role.name}, 权限数量: {len(permission_ids)}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="权限分配成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"权限分配失败: {str(e)}").to_dict())

@role_bp.route('/batch-operation', methods=['POST'])
@require_permission('role:batch')
def batch_role_operation(current_user):
    """批量角色操作"""
    try:
        data = request.get_json()
        role_ids = data.get('role_ids', [])
        operation = data.get('operation')
        
        if not role_ids or not operation:
            return jsonify(Result.error(message="角色ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for role_id in role_ids:
            try:
                role = Role.get_by_id(role_id)
                if not role:
                    results.append({"role_id": role_id, "status": "failed", "message": "角色不存在"})
                    failed_count += 1
                    continue
                
                if role.is_system:
                    results.append({"role_id": role_id, "status": "failed", "message": "系统内置角色不允许操作"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    # 检查是否有用户使用此角色
                    user_count = User.query.filter_by(role_id=role_id).count()
                    if user_count > 0:
                        results.append({"role_id": role_id, "status": "failed", "message": f"该角色下还有 {user_count} 个用户"})
                        failed_count += 1
                        continue
                    role.delete()
                elif operation == 'enable':
                    role.status = True
                    role.save()
                elif operation == 'disable':
                    role.status = False
                    role.save()
                else:
                    results.append({"role_id": role_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"role_id": role_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"role_id": role_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="批量角色操作",
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