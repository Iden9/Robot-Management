from app import db
from datetime import datetime

class Menu(db.Model):
    """菜单模型"""
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='菜单ID')
    name = db.Column(db.String(100), nullable=False, comment='菜单名称')
    title = db.Column(db.String(100), nullable=False, comment='菜单标题')
    path = db.Column(db.String(200), comment='路由路径')
    component = db.Column(db.String(200), comment='组件路径')
    icon = db.Column(db.String(100), comment='菜单图标')
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE'), comment='父菜单ID')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    menu_type = db.Column(db.Enum('directory', 'menu', 'button'), default='menu', comment='菜单类型')
    is_hidden = db.Column(db.Boolean, default=False, comment='是否隐藏')
    is_keepalive = db.Column(db.Boolean, default=True, comment='是否缓存')
    is_affix = db.Column(db.Boolean, default=False, comment='是否固定标签')
    redirect = db.Column(db.String(200), comment='重定向路径')
    permission_code = db.Column(db.String(100), comment='权限编码')
    status = db.Column(db.Boolean, default=True, comment='状态')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='创建人')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    parent = db.relationship('Menu', remote_side=[id], backref='children')
    creator = db.relationship('User', backref='created_menus', lazy=True)
    
    def save(self):
        """保存菜单"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除菜单"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self, include_children=False):
        """将菜单对象转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'path': self.path,
            'component': self.component,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'menu_type': self.menu_type,
            'is_hidden': self.is_hidden,
            'is_keepalive': self.is_keepalive,
            'is_affix': self.is_affix,
            'redirect': self.redirect,
            'permission_code': self.permission_code,
            'status': self.status,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'level': self.get_level(),
            'has_children': len(self.children) > 0
        }
        
        if include_children:
            data['children'] = [child.to_dict(True) for child in self.get_sorted_children()]
            
        return data
        
    def to_route_dict(self):
        """转换为前端路由格式"""
        route = {
            'name': self.name,
            'path': self.path,
            'meta': {
                'title': self.title,
                'icon': self.icon,
                'hidden': self.is_hidden,
                'keepAlive': self.is_keepalive,
                'affix': self.is_affix,
                'permission': self.permission_code
            }
        }
        
        if self.component:
            route['component'] = self.component
            
        if self.redirect:
            route['redirect'] = self.redirect
            
        children = self.get_sorted_children()
        if children:
            route['children'] = [child.to_route_dict() for child in children if child.status]
            
        return route
        
    def __repr__(self):
        return f'<Menu {self.title}>'
    
    @classmethod
    def get_by_id(cls, menu_id):
        """根据ID获取菜单"""
        return cls.query.get(menu_id)
    
    @classmethod
    def get_by_path(cls, path):
        """根据路径获取菜单"""
        return cls.query.filter_by(path=path).first()
    
    @classmethod
    def get_by_name(cls, name):
        """根据名称获取菜单"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_root_menus(cls, status=None):
        """获取根菜单列表"""
        query = cls.query.filter_by(parent_id=None)
        if status is not None:
            query = query.filter_by(status=status)
        return query.order_by(cls.sort_order.asc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_tree_structure(cls, status=None):
        """获取菜单树结构"""
        root_menus = cls.get_root_menus(status)
        return [menu.to_dict(include_children=True) for menu in root_menus]
    
    @classmethod
    def get_routes_structure(cls):
        """获取前端路由结构"""
        root_menus = cls.get_root_menus(status=True)
        return [menu.to_route_dict() for menu in root_menus]
    
    def get_level(self):
        """获取菜单层级"""
        level = 1
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    
    def get_sorted_children(self):
        """获取排序后的子菜单"""
        return sorted([child for child in self.children if child.status], 
                     key=lambda x: (x.sort_order, x.created_at))
    
    def get_all_children(self):
        """获取所有子菜单（递归）"""
        all_children = []
        for child in self.children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children
    
    def get_parent_path(self):
        """获取父级路径"""
        if not self.parent:
            return []
        parent_path = self.parent.get_parent_path()
        parent_path.append(self.parent.id)
        return parent_path
    
    def can_delete(self):
        """检查是否可以删除"""
        return len(self.children) == 0
    
    @classmethod
    def get_user_menus(cls, user_permissions):
        """根据用户权限获取菜单"""
        # 获取所有启用的菜单
        all_menus = cls.query.filter_by(status=True).all()
        
        # 过滤用户有权限的菜单
        accessible_menus = []
        for menu in all_menus:
            if not menu.permission_code or menu.permission_code in user_permissions:
                accessible_menus.append(menu)
        
        # 构建树结构
        menu_dict = {menu.id: menu for menu in accessible_menus}
        root_menus = []
        
        for menu in accessible_menus:
            if menu.parent_id is None:
                root_menus.append(menu)
            else:
                parent = menu_dict.get(menu.parent_id)
                if parent and not hasattr(parent, '_filtered_children'):
                    parent._filtered_children = []
                if parent:
                    parent._filtered_children.append(menu)
        
        return root_menus