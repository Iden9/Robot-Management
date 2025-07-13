#!/usr/bin/env python3
"""
RBAC系统初始化脚本
初始化默认角色、权限和菜单数据
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.role import Role, RolePermission
from app.models.permission import Permission
from app.models.menu import Menu

def init_permissions():
    """初始化权限数据"""
    permissions_data = [
        # 用户管理
        {'name': '用户查看', 'code': 'user:list', 'module': '用户管理', 'permission_type': 'api', 'resource_path': '/api/users', 'method': 'GET'},
        {'name': '用户详情', 'code': 'user:detail', 'module': '用户管理', 'permission_type': 'api', 'resource_path': '/api/users/*', 'method': 'GET'},
        {'name': '用户创建', 'code': 'user:create', 'module': '用户管理', 'permission_type': 'api', 'resource_path': '/api/users', 'method': 'POST'},
        {'name': '用户编辑', 'code': 'user:update', 'module': '用户管理', 'permission_type': 'api', 'resource_path': '/api/users/*', 'method': 'PUT'},
        {'name': '用户删除', 'code': 'user:delete', 'module': '用户管理', 'permission_type': 'api', 'resource_path': '/api/users/*', 'method': 'DELETE'},
        {'name': '重置密码', 'code': 'user:reset_password', 'module': '用户管理', 'permission_type': 'button'},
        
        # 设备管理
        {'name': '设备查看', 'code': 'equipment:list', 'module': '设备管理', 'permission_type': 'api', 'resource_path': '/api/equipment', 'method': 'GET'},
        {'name': '设备详情', 'code': 'equipment:detail', 'module': '设备管理', 'permission_type': 'api', 'resource_path': '/api/equipment/*', 'method': 'GET'},
        {'name': '设备创建', 'code': 'equipment:create', 'module': '设备管理', 'permission_type': 'api', 'resource_path': '/api/equipment', 'method': 'POST'},
        {'name': '设备编辑', 'code': 'equipment:update', 'module': '设备管理', 'permission_type': 'api', 'resource_path': '/api/equipment/*', 'method': 'PUT'},
        {'name': '设备删除', 'code': 'equipment:delete', 'module': '设备管理', 'permission_type': 'api', 'resource_path': '/api/equipment/*', 'method': 'DELETE'},
        {'name': '设备控制', 'code': 'equipment:control', 'module': '设备管理', 'permission_type': 'button'},
        
        # 课件管理
        {'name': '课件查看', 'code': 'courseware:list', 'module': '课件管理', 'permission_type': 'api', 'resource_path': '/api/courseware', 'method': 'GET'},
        {'name': '课件详情', 'code': 'courseware:detail', 'module': '课件管理', 'permission_type': 'api', 'resource_path': '/api/courseware/*', 'method': 'GET'},
        {'name': '课件上传', 'code': 'courseware:upload', 'module': '课件管理', 'permission_type': 'api', 'resource_path': '/api/courseware/upload', 'method': 'POST'},
        {'name': '课件编辑', 'code': 'courseware:update', 'module': '课件管理', 'permission_type': 'api', 'resource_path': '/api/courseware/*', 'method': 'PUT'},
        {'name': '课件删除', 'code': 'courseware:delete', 'module': '课件管理', 'permission_type': 'api', 'resource_path': '/api/courseware/*', 'method': 'DELETE'},
        
        # 导航管理
        {'name': '导航查看', 'code': 'navigation:list', 'module': '导航管理', 'permission_type': 'api', 'resource_path': '/api/navigation', 'method': 'GET'},
        {'name': '导航设置', 'code': 'navigation:update', 'module': '导航管理', 'permission_type': 'api', 'resource_path': '/api/navigation/*', 'method': 'PUT'},
        
        # 系统管理
        {'name': '系统看板', 'code': 'dashboard:view', 'module': '系统管理', 'permission_type': 'menu', 'resource_path': '/dashboard'},
        {'name': '系统设置', 'code': 'system:settings', 'module': '系统管理', 'permission_type': 'api', 'resource_path': '/api/system/*', 'method': 'GET'},
        {'name': '系统配置', 'code': 'system:config', 'module': '系统管理', 'permission_type': 'api', 'resource_path': '/api/system/*', 'method': 'PUT'},
        
        # 日志管理
        {'name': '日志查看', 'code': 'log:list', 'module': '日志管理', 'permission_type': 'api', 'resource_path': '/api/logs', 'method': 'GET'},
        {'name': '日志详情', 'code': 'log:detail', 'module': '日志管理', 'permission_type': 'api', 'resource_path': '/api/logs/*', 'method': 'GET'},
        
        # 角色管理
        {'name': '角色查看', 'code': 'role:list', 'module': '角色管理', 'permission_type': 'api', 'resource_path': '/api/roles', 'method': 'GET'},
        {'name': '角色详情', 'code': 'role:detail', 'module': '角色管理', 'permission_type': 'api', 'resource_path': '/api/roles/*', 'method': 'GET'},
        {'name': '角色创建', 'code': 'role:create', 'module': '角色管理', 'permission_type': 'api', 'resource_path': '/api/roles', 'method': 'POST'},
        {'name': '角色编辑', 'code': 'role:update', 'module': '角色管理', 'permission_type': 'api', 'resource_path': '/api/roles/*', 'method': 'PUT'},
        {'name': '角色删除', 'code': 'role:delete', 'module': '角色管理', 'permission_type': 'api', 'resource_path': '/api/roles/*', 'method': 'DELETE'},
        {'name': '角色权限分配', 'code': 'role:permission', 'module': '角色管理', 'permission_type': 'button'},
        {'name': '角色批量操作', 'code': 'role:batch', 'module': '角色管理', 'permission_type': 'button'},
        
        # 权限管理
        {'name': '权限查看', 'code': 'permission:list', 'module': '权限管理', 'permission_type': 'api', 'resource_path': '/api/permissions', 'method': 'GET'},
        {'name': '权限详情', 'code': 'permission:detail', 'module': '权限管理', 'permission_type': 'api', 'resource_path': '/api/permissions/*', 'method': 'GET'},
        {'name': '权限创建', 'code': 'permission:create', 'module': '权限管理', 'permission_type': 'api', 'resource_path': '/api/permissions', 'method': 'POST'},
        {'name': '权限编辑', 'code': 'permission:update', 'module': '权限管理', 'permission_type': 'api', 'resource_path': '/api/permissions/*', 'method': 'PUT'},
        {'name': '权限删除', 'code': 'permission:delete', 'module': '权限管理', 'permission_type': 'api', 'resource_path': '/api/permissions/*', 'method': 'DELETE'},
        {'name': '权限批量操作', 'code': 'permission:batch', 'module': '权限管理', 'permission_type': 'button'},
        
        # 菜单管理
        {'name': '菜单查看', 'code': 'menu:list', 'module': '菜单管理', 'permission_type': 'api', 'resource_path': '/api/menus', 'method': 'GET'},
        {'name': '菜单详情', 'code': 'menu:detail', 'module': '菜单管理', 'permission_type': 'api', 'resource_path': '/api/menus/*', 'method': 'GET'},
        {'name': '菜单创建', 'code': 'menu:create', 'module': '菜单管理', 'permission_type': 'api', 'resource_path': '/api/menus', 'method': 'POST'},
        {'name': '菜单编辑', 'code': 'menu:update', 'module': '菜单管理', 'permission_type': 'api', 'resource_path': '/api/menus/*', 'method': 'PUT'},
        {'name': '菜单删除', 'code': 'menu:delete', 'module': '菜单管理', 'permission_type': 'api', 'resource_path': '/api/menus/*', 'method': 'DELETE'},
        {'name': '菜单批量操作', 'code': 'menu:batch', 'module': '菜单管理', 'permission_type': 'button'},
        
        # 教育模块
        {'name': '教育内容查看', 'code': 'education:view', 'module': '教育模块', 'permission_type': 'menu', 'resource_path': '/education'},
    ]
    
    created_permissions = []
    for perm_data in permissions_data:
        existing = Permission.get_by_code(perm_data['code'])
        if not existing:
            permission = Permission(**perm_data, is_system=True, status=True, sort_order=len(created_permissions))
            permission.save()
            created_permissions.append(permission)
            print(f"✓ 创建权限: {permission.name} ({permission.code})")
        else:
            created_permissions.append(existing)
    
    return created_permissions

def init_roles(permissions):
    """初始化角色数据"""
    # 创建权限映射
    permission_map = {p.code: p for p in permissions}
    
    roles_data = [
        {
            'name': '系统管理员',
            'code': 'admin',
            'description': '拥有系统所有权限',
            'permissions': list(permission_map.keys())  # 所有权限
        },
        {
            'name': '操作员',
            'code': 'operator',
            'description': '可操作设备和管理课件',
            'permissions': [
                'equipment:list', 'equipment:detail', 'equipment:control',
                'courseware:list', 'courseware:detail', 'courseware:upload', 'courseware:update', 'courseware:delete',
                'navigation:list', 'navigation:update',
                'education:view',
                'log:list', 'log:detail'
            ]
        },
        {
            'name': '查看者',
            'code': 'viewer',
            'description': '只能查看相关信息',
            'permissions': [
                'equipment:list', 'equipment:detail',
                'courseware:list', 'courseware:detail',
                'navigation:list',
                'education:view',
                'log:list'
            ]
        }
    ]
    
    created_roles = []
    for role_data in roles_data:
        existing = Role.get_by_code(role_data['code'])
        if not existing:
            role = Role(
                name=role_data['name'],
                code=role_data['code'],
                description=role_data['description'],
                is_system=True,
                status=True
            )
            role.save()
            
            # 分配权限
            for perm_code in role_data['permissions']:
                if perm_code in permission_map:
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=permission_map[perm_code].id
                    )
                    role_permission.save()
            
            created_roles.append(role)
            print(f"✓ 创建角色: {role.name} ({role.code}) - {len(role_data['permissions'])} 个权限")
        else:
            created_roles.append(existing)
    
    return created_roles

def init_menus():
    """初始化菜单数据"""
    menus_data = [
        # 系统管理目录
        {
            'name': 'system',
            'title': '系统管理',
            'path': '/system',
            'component': 'Layout',
            'icon': 'system',
            'menu_type': 'directory',
            'sort_order': 1,
            'permission_code': 'dashboard:view'
        },
        # 系统看板
        {
            'name': 'dashboard',
            'title': '系统看板',
            'path': '/dashboard',
            'component': 'SystemDashboard',
            'icon': 'dashboard',
            'menu_type': 'menu',
            'sort_order': 1,
            'permission_code': 'dashboard:view',
            'parent_name': 'system'
        },
        
        # 设备管理目录
        {
            'name': 'equipment-management',
            'title': '设备管理',
            'path': '/equipment',
            'component': 'Layout',
            'icon': 'equipment',
            'menu_type': 'directory',
            'sort_order': 2
        },
        # 设备列表
        {
            'name': 'equipment-list',
            'title': '设备列表',
            'path': '/equipment/list',
            'component': 'EquipmentManagement',
            'icon': 'list',
            'menu_type': 'menu',
            'sort_order': 1,
            'permission_code': 'equipment:list',
            'parent_name': 'equipment-management'
        },
        # 机器人控制
        {
            'name': 'robot-control',
            'title': '机器人控制',
            'path': '/equipment/control',
            'component': 'RobotControl',
            'icon': 'control',
            'menu_type': 'menu',
            'sort_order': 2,
            'permission_code': 'equipment:control',
            'parent_name': 'equipment-management'
        },
        
        # 课件管理目录
        {
            'name': 'courseware-management',
            'title': '课件管理',
            'path': '/courseware',
            'component': 'Layout',
            'icon': 'courseware',
            'menu_type': 'directory',
            'sort_order': 3
        },
        # 课件列表
        {
            'name': 'courseware-list',
            'title': '课件列表',
            'path': '/courseware/list',
            'component': 'CoursewareManagement',
            'icon': 'list',
            'menu_type': 'menu',
            'sort_order': 1,
            'permission_code': 'courseware:list',
            'parent_name': 'courseware-management'
        },
        
        # 导航管理
        {
            'name': 'navigation',
            'title': '导航管理',
            'path': '/navigation',
            'component': 'SelfGuidedNavigation',
            'icon': 'navigation',
            'menu_type': 'menu',
            'sort_order': 4,
            'permission_code': 'navigation:list'
        },
        
        # 教育模块
        {
            'name': 'education',
            'title': '教育模块',
            'path': '/education',
            'component': 'EducationModule',
            'icon': 'education',
            'menu_type': 'menu',
            'sort_order': 5,
            'permission_code': 'education:view'
        },
        
        # 用户管理
        {
            'name': 'user-management',
            'title': '账号管理',
            'path': '/users',
            'component': 'AccountManagement',
            'icon': 'user',
            'menu_type': 'menu',
            'sort_order': 6,
            'permission_code': 'user:list'
        },
        
        # 权限管理目录
        {
            'name': 'permission-management',
            'title': '权限管理',
            'path': '/permission',
            'component': 'Layout',
            'icon': 'permission',
            'menu_type': 'directory',
            'sort_order': 7
        },
        # 角色管理
        {
            'name': 'role-management',
            'title': '角色管理',
            'path': '/permission/roles',
            'component': 'RoleManagement',
            'icon': 'role',
            'menu_type': 'menu',
            'sort_order': 1,
            'permission_code': 'role:list',
            'parent_name': 'permission-management'
        },
        # 菜单管理
        {
            'name': 'menu-management',
            'title': '菜单管理',
            'path': '/permission/menus',
            'component': 'MenuManagement',
            'icon': 'menu',
            'menu_type': 'menu',
            'sort_order': 2,
            'permission_code': 'menu:list',
            'parent_name': 'permission-management'
        },
        # 权限管理
        {
            'name': 'permission-list',
            'title': '权限管理',
            'path': '/permission/permissions',
            'component': 'PermissionManagement',
            'icon': 'permission-list',
            'menu_type': 'menu',
            'sort_order': 3,
            'permission_code': 'permission:list',
            'parent_name': 'permission-management'
        },
        
        # 日志管理
        {
            'name': 'log-management',
            'title': '日志管理',
            'path': '/logs',
            'component': 'LogManagement',
            'icon': 'log',
            'menu_type': 'menu',
            'sort_order': 8,
            'permission_code': 'log:list'
        }
    ]
    
    # 第一轮：创建所有菜单（不设置parent_id）
    menu_map = {}
    for menu_data in menus_data:
        parent_name = menu_data.pop('parent_name', None)
        existing = Menu.get_by_name(menu_data['name'])
        if not existing:
            menu = Menu(**menu_data, status=True)
            menu.save()
            menu_map[menu.name] = {'menu': menu, 'parent_name': parent_name}
            print(f"✓ 创建菜单: {menu.title} ({menu.name})")
        else:
            menu_map[existing.name] = {'menu': existing, 'parent_name': parent_name}
    
    # 第二轮：设置父子关系
    for menu_name, menu_info in menu_map.items():
        menu = menu_info['menu']
        parent_name = menu_info['parent_name']
        if parent_name and parent_name in menu_map:
            parent_menu = menu_map[parent_name]['menu']
            menu.parent_id = parent_menu.id
            menu.save()
            print(f"✓ 设置菜单关系: {menu.title} -> {parent_menu.title}")
    
    return list(menu_map.values())

def update_users_with_roles(roles):
    """更新现有用户的角色ID"""
    role_map = {role.code: role for role in roles}
    
    # 更新现有用户
    users = User.query.all()
    for user in users:
        old_role = user.role
        if old_role in role_map:
            user.role_id = role_map[old_role].id
            user.save()
            print(f"✓ 更新用户 {user.username} 角色: {old_role} -> {role_map[old_role].name}")

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化RBAC系统...")
        
        # 创建数据库表
        db.create_all()
        print("✓ 数据库表创建完成")
        
        # 初始化权限
        print("\n1. 初始化权限...")
        permissions = init_permissions()
        
        # 初始化角色
        print("\n2. 初始化角色...")
        roles = init_roles(permissions)
        
        # 初始化菜单
        print("\n3. 初始化菜单...")
        menus = init_menus()
        
        # 更新用户角色
        print("\n4. 更新用户角色...")
        update_users_with_roles(roles)
        
        print("\n✓ RBAC系统初始化完成！")
        print("\n角色说明:")
        print("  - 系统管理员(admin): 拥有所有权限")
        print("  - 操作员(operator): 可操作设备和管理课件")
        print("  - 查看者(viewer): 只能查看相关信息")

if __name__ == '__main__':
    main()