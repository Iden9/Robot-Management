from app import db
from datetime import datetime

class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='权限ID')
    name = db.Column(db.String(100), nullable=False, comment='权限名称')
    code = db.Column(db.String(100), unique=True, nullable=False, comment='权限编码')
    description = db.Column(db.Text, comment='权限描述')
    module = db.Column(db.String(50), comment='所属模块')
    permission_type = db.Column(db.Enum('menu', 'button', 'api'), default='button', comment='权限类型')
    resource_path = db.Column(db.String(200), comment='资源路径')
    method = db.Column(db.String(10), comment='请求方法')
    is_system = db.Column(db.Boolean, default=False, comment='是否为系统内置权限')
    status = db.Column(db.Boolean, default=True, comment='状态')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='创建人')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    creator = db.relationship('User', backref='created_permissions', lazy=True)
    role_permissions = db.relationship('RolePermission', backref='permission', lazy=True, cascade='all, delete-orphan')
    
    def save(self):
        """保存权限"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除权限"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将权限对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'module': self.module,
            'permission_type': self.permission_type,
            'resource_path': self.resource_path,
            'method': self.method,
            'is_system': self.is_system,
            'status': self.status,
            'sort_order': self.sort_order,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'role_count': len(self.role_permissions)
        }
        
    def __repr__(self):
        return f'<Permission {self.name}>'
    
    @classmethod
    def get_by_id(cls, permission_id):
        """根据ID获取权限"""
        return cls.query.get(permission_id)
    
    @classmethod
    def get_by_code(cls, code):
        """根据编码获取权限"""
        return cls.query.filter_by(code=code).first()
    
    @classmethod
    def get_by_name(cls, name):
        """根据名称获取权限"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_all_active(cls):
        """获取所有启用的权限"""
        return cls.query.filter_by(status=True).order_by(
            cls.module.asc(), cls.sort_order.asc(), cls.created_at.desc()
        ).all()
    
    @classmethod
    def get_all_ordered(cls):
        """获取所有权限，按模块和排序排序"""
        return cls.query.order_by(
            cls.module.asc(), cls.sort_order.asc(), cls.created_at.desc()
        ).all()
    
    @classmethod
    def get_by_module(cls, module, status=None):
        """根据模块获取权限"""
        query = cls.query.filter_by(module=module)
        if status is not None:
            query = query.filter_by(status=status)
        return query.order_by(cls.sort_order.asc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_by_type(cls, permission_type, status=None):
        """根据类型获取权限"""
        query = cls.query.filter_by(permission_type=permission_type)
        if status is not None:
            query = query.filter_by(status=status)
        return query.order_by(
            cls.module.asc(), cls.sort_order.asc(), cls.created_at.desc()
        ).all()
    
    @classmethod
    def get_grouped_by_module(cls, status=None):
        """按模块分组获取权限"""
        query = cls.query
        if status is not None:
            query = query.filter_by(status=status)
        
        permissions = query.order_by(
            cls.module.asc(), cls.sort_order.asc(), cls.created_at.desc()
        ).all()
        
        grouped = {}
        for permission in permissions:
            module = permission.module or '其他'
            if module not in grouped:
                grouped[module] = []
            grouped[module].append(permission)
        
        return grouped
    
    @classmethod
    def check_resource_permission(cls, resource_path, method='GET'):
        """检查资源权限"""
        return cls.query.filter_by(
            resource_path=resource_path,
            method=method.upper(),
            status=True
        ).first()
    
    def get_roles(self):
        """获取拥有此权限的角色"""
        from app.models.role import Role, RolePermission
        return db.session.query(Role).join(
            RolePermission, Role.id == RolePermission.role_id
        ).filter(RolePermission.permission_id == self.id).all()
    
    def is_assigned_to_role(self, role_id):
        """检查权限是否已分配给指定角色"""
        from app.models.role import RolePermission
        return RolePermission.query.filter_by(
            role_id=role_id,
            permission_id=self.id
        ).first() is not None