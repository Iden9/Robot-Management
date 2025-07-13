from flask import request, jsonify, Blueprint
from app.models import User, OperationLog
from app.models.menu import Menu
from app.models.result import Result
from app.auth import require_auth, require_role, require_permission
from app import db
from sqlalchemy import or_
import datetime

# 创建菜单管理蓝图
menu_bp = Blueprint('menu', __name__)

@menu_bp.route('', methods=['GET'])
@require_auth
def get_menu_list(current_user):
    """获取菜单列表"""
    try:
        menu_type = request.args.get('type', 'tree')  # tree: 树结构, list: 列表结构
        status = request.args.get('status')
        
        if menu_type == 'tree':
            status_filter = None if status is None else bool(int(status))
            menus = Menu.get_tree_structure(status_filter)
        else:
            query = Menu.query
            if status is not None:
                query = query.filter_by(status=bool(int(status)))
            menus = query.order_by(Menu.sort_order.asc(), Menu.created_at.desc()).all()
            menus = [menu.to_dict() for menu in menus]
        
        return jsonify(Result.success(
            message="获取菜单列表成功",
            data=menus
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取菜单列表失败: {str(e)}").to_dict())

@menu_bp.route('/routes', methods=['GET'])
@require_auth
def get_menu_routes(current_user):
    """获取用户可访问的路由菜单"""
    try:
        # 获取用户权限
        user_permissions = current_user.get_permissions()
        
        # 获取用户可访问的菜单
        accessible_menus = Menu.get_user_menus(user_permissions)
        
        # 转换为路由格式
        routes = []
        for menu in accessible_menus:
            route = menu.to_route_dict()
            if hasattr(menu, '_filtered_children'):
                route['children'] = [child.to_route_dict() for child in menu._filtered_children]
            routes.append(route)
        
        return jsonify(Result.success(
            message="获取用户菜单成功",
            data=routes
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户菜单失败: {str(e)}").to_dict())

@menu_bp.route('/<int:menu_id>', methods=['GET'])
@require_permission('menu:detail')
def get_menu(current_user, menu_id):
    """获取单个菜单信息"""
    try:
        menu = Menu.get_by_id(menu_id)
        if not menu:
            return jsonify(Result.error(message="菜单不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取菜单信息成功",
            data=menu.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取菜单信息失败: {str(e)}").to_dict())

@menu_bp.route('', methods=['POST'])
@require_permission('menu:create')
def create_menu(current_user):
    """创建菜单"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['name', 'title']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查菜单名称是否已存在
        if Menu.get_by_name(data['name']):
            return jsonify(Result.error(message="菜单名称已存在", code=400).to_dict())
        
        # 检查路径是否已存在
        if data.get('path') and Menu.get_by_path(data['path']):
            return jsonify(Result.error(message="菜单路径已存在", code=400).to_dict())
        
        # 验证父菜单
        parent_id = data.get('parent_id')
        if parent_id:
            parent_menu = Menu.get_by_id(parent_id)
            if not parent_menu:
                return jsonify(Result.error(message="父菜单不存在", code=400).to_dict())
        
        # 创建新菜单
        menu = Menu(
            name=data['name'],
            title=data['title'],
            path=data.get('path'),
            component=data.get('component'),
            icon=data.get('icon'),
            parent_id=parent_id,
            sort_order=data.get('sort_order', 0),
            menu_type=data.get('menu_type', 'menu'),
            is_hidden=data.get('is_hidden', False),
            is_keepalive=data.get('is_keepalive', True),
            is_affix=data.get('is_affix', False),
            redirect=data.get('redirect'),
            permission_code=data.get('permission_code'),
            status=data.get('status', True),
            created_by=current_user.id
        )
        menu.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="创建菜单",
            details=f"菜单名称: {menu.title}, 菜单路径: {menu.path}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="菜单创建成功",
            data=menu.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"菜单创建失败: {str(e)}").to_dict())

@menu_bp.route('/<int:menu_id>', methods=['PUT'])
@require_permission('menu:update')
def update_menu(current_user, menu_id):
    """更新菜单"""
    try:
        menu = Menu.get_by_id(menu_id)
        if not menu:
            return jsonify(Result.error(message="菜单不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = Menu.get_by_name(data['name'])
            if existing and existing.id != menu.id:
                return jsonify(Result.error(message="菜单名称已存在", code=400).to_dict())
            menu.name = data['name']
        
        if 'title' in data:
            menu.title = data['title']
        
        if 'path' in data:
            # 检查新路径是否已存在
            if data['path']:
                existing = Menu.get_by_path(data['path'])
                if existing and existing.id != menu.id:
                    return jsonify(Result.error(message="菜单路径已存在", code=400).to_dict())
            menu.path = data['path']
        
        if 'component' in data:
            menu.component = data['component']
        
        if 'icon' in data:
            menu.icon = data['icon']
        
        if 'parent_id' in data:
            parent_id = data['parent_id']
            if parent_id:
                # 验证父菜单存在
                parent_menu = Menu.get_by_id(parent_id)
                if not parent_menu:
                    return jsonify(Result.error(message="父菜单不存在", code=400).to_dict())
                
                # 防止循环引用
                if parent_id == menu.id:
                    return jsonify(Result.error(message="不能将自己设为父菜单", code=400).to_dict())
                
                # 检查是否会形成循环
                current_parent = parent_menu
                while current_parent:
                    if current_parent.id == menu.id:
                        return jsonify(Result.error(message="不能形成循环引用", code=400).to_dict())
                    current_parent = current_parent.parent
            
            menu.parent_id = parent_id
        
        if 'sort_order' in data:
            menu.sort_order = data['sort_order']
        
        if 'menu_type' in data:
            menu.menu_type = data['menu_type']
        
        if 'is_hidden' in data:
            menu.is_hidden = data['is_hidden']
        
        if 'is_keepalive' in data:
            menu.is_keepalive = data['is_keepalive']
        
        if 'is_affix' in data:
            menu.is_affix = data['is_affix']
        
        if 'redirect' in data:
            menu.redirect = data['redirect']
        
        if 'permission_code' in data:
            menu.permission_code = data['permission_code']
        
        if 'status' in data:
            menu.status = data['status']
        
        menu.updated_at = datetime.datetime.utcnow()
        menu.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="更新菜单",
            details=f"菜单名称: {menu.title}, 菜单路径: {menu.path}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="菜单更新成功",
            data=menu.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"菜单更新失败: {str(e)}").to_dict())

@menu_bp.route('/<int:menu_id>', methods=['DELETE'])
@require_permission('menu:delete')
def delete_menu(current_user, menu_id):
    """删除菜单"""
    try:
        menu = Menu.get_by_id(menu_id)
        if not menu:
            return jsonify(Result.error(message="菜单不存在", code=404).to_dict())
        
        # 检查是否有子菜单
        if not menu.can_delete():
            return jsonify(Result.error(message="该菜单下还有子菜单，不能删除", code=400).to_dict())
        
        menu_title = menu.title
        menu.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="删除菜单",
            details=f"菜单名称: {menu_title}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="菜单删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"菜单删除失败: {str(e)}").to_dict())

@menu_bp.route('/parent-options', methods=['GET'])
@require_permission('menu:list')
def get_parent_menu_options(current_user):
    """获取父菜单选项（用于下拉选择）"""
    try:
        exclude_id = request.args.get('exclude_id', type=int)
        
        # 获取所有可作为父菜单的菜单（目录和菜单类型）
        query = Menu.query.filter(
            Menu.menu_type.in_(['directory', 'menu']),
            Menu.status == True
        )
        
        if exclude_id:
            # 排除指定菜单及其所有子菜单
            exclude_menu = Menu.get_by_id(exclude_id)
            if exclude_menu:
                exclude_ids = [exclude_id]
                exclude_ids.extend([child.id for child in exclude_menu.get_all_children()])
                query = query.filter(~Menu.id.in_(exclude_ids))
        
        menus = query.order_by(Menu.sort_order.asc(), Menu.created_at.desc()).all()
        
        # 构建树结构选项
        options = []
        for menu in menus:
            if menu.parent_id is None:  # 根菜单
                option = {
                    'id': menu.id,
                    'title': menu.title,
                    'level': 1,
                    'children': []
                }
                # 递归添加子菜单
                self._build_menu_options(option, menus, 1)
                options.append(option)
        
        return jsonify(Result.success(
            message="获取父菜单选项成功",
            data=options
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取父菜单选项失败: {str(e)}").to_dict())

def _build_menu_options(parent_option, all_menus, level):
    """递归构建菜单选项"""
    for menu in all_menus:
        if menu.parent_id == parent_option['id']:
            child_option = {
                'id': menu.id,
                'title': '　' * level + '├─ ' + menu.title,
                'level': level + 1,
                'children': []
            }
            _build_menu_options(child_option, all_menus, level + 1)
            parent_option['children'].append(child_option)

@menu_bp.route('/batch-operation', methods=['POST'])
@require_permission('menu:batch')
def batch_menu_operation(current_user):
    """批量菜单操作"""
    try:
        data = request.get_json()
        menu_ids = data.get('menu_ids', [])
        operation = data.get('operation')
        
        if not menu_ids or not operation:
            return jsonify(Result.error(message="菜单ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for menu_id in menu_ids:
            try:
                menu = Menu.get_by_id(menu_id)
                if not menu:
                    results.append({"menu_id": menu_id, "status": "failed", "message": "菜单不存在"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    if not menu.can_delete():
                        results.append({"menu_id": menu_id, "status": "failed", "message": "该菜单下还有子菜单"})
                        failed_count += 1
                        continue
                    menu.delete()
                elif operation == 'enable':
                    menu.status = True
                    menu.save()
                elif operation == 'disable':
                    menu.status = False
                    menu.save()
                elif operation == 'show':
                    menu.is_hidden = False
                    menu.save()
                elif operation == 'hide':
                    menu.is_hidden = True
                    menu.save()
                else:
                    results.append({"menu_id": menu_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"menu_id": menu_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"menu_id": menu_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="批量菜单操作",
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