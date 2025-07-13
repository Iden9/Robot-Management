from app import db
from datetime import datetime

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色ID')
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='角色编码')
    description = db.Column(db.Text, comment='角色描述')
    is_system = db.Column(db.Boolean, default=False, comment='是否为系统内置角色')
    status = db.Column(db.Boolean, default=True, comment='状态')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='创建人')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_roles', lazy=True)
    users = db.relationship('User', foreign_keys='User.role_id', backref='role_obj', lazy=True)
    role_permissions = db.relationship('RolePermission', backref='role', lazy=True, cascade='all, delete-orphan')
    
    def save(self):
        """保存角色"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除角色"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将角色对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_system': self.is_system,
            'status': self.status,
            'sort_order': self.sort_order,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'permission_count': len(self.role_permissions),
            'user_count': len(self.users)
        }
        
    def __repr__(self):
        return f'<Role {self.name}>'
    
    @classmethod
    def get_by_id(cls, role_id):
        """根据ID获取角色"""
        return cls.query.get(role_id)
    
    @classmethod
    def get_by_code(cls, code):
        """根据编码获取角色"""
        return cls.query.filter_by(code=code).first()
    
    @classmethod
    def get_by_name(cls, name):
        """根据名称获取角色"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_all_active(cls):
        """获取所有启用的角色"""
        return cls.query.filter_by(status=True).order_by(cls.sort_order.asc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_all_ordered(cls):
        """获取所有角色，按排序和创建时间排序"""
        return cls.query.order_by(cls.sort_order.asc(), cls.created_at.desc()).all()
    
    def get_permissions(self):
        """获取角色的所有权限"""
        from app.models.permission import Permission
        return db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id == self.id).all()
    
    def has_permission(self, permission_code):
        """检查角色是否拥有指定权限"""
        from app.models.permission import Permission
        return db.session.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.role_id == self.id,
            Permission.code == permission_code
        ).first() is not None
    
    def assign_permission(self, permission_id):
        """为角色分配权限"""
        existing = RolePermission.query.filter_by(
            role_id=self.id,
            permission_id=permission_id
        ).first()
        
        if not existing:
            role_permission = RolePermission(
                role_id=self.id,
                permission_id=permission_id
            )
            role_permission.save()
    
    def remove_permission(self, permission_id):
        """移除角色权限"""
        role_permission = RolePermission.query.filter_by(
            role_id=self.id,
            permission_id=permission_id
        ).first()
        
        if role_permission:
            role_permission.delete()

class RolePermission(db.Model):
    """角色权限关联表"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='ID')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, comment='角色ID')
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, comment='权限ID')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    
    # 联合唯一索引
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),)
    
    def save(self):
        """保存角色权限关联"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除角色权限关联"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }