from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码哈希')
    real_name = db.Column(db.String(100), nullable=False, comment='真实姓名')
    email = db.Column(db.String(100), unique=True, comment='邮箱地址')
    phone = db.Column(db.String(20), comment='手机号码')
    role = db.Column(db.Enum('admin', 'operator', 'viewer'), nullable=False, default='viewer', comment='用户角色')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='SET NULL'), comment='角色ID')
    status = db.Column(db.Boolean, default=True, comment='用户状态: 1-启用, 0-禁用')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    login_count = db.Column(db.Integer, default=0, comment='登录次数')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 完成save
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    # 完成delete
    def delete(self):
        from app.models.user_session import UserSession
        
        # 先删除所有相关的会话
        UserSession.query.filter_by(user_id=self.id).delete()
        
        # 删除用户
        db.session.delete(self)
        db.session.commit()
        
    def set_password(self, password):
        """设置密码"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)
    
    def update_login_info(self):
        """更新登录信息"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.save()
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'role_id': self.role_id,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def get_by_username(cls, username):
        """根据用户名获取用户"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_id(cls, user_id):
        """根据ID获取用户"""
        return cls.query.get(user_id)

    @classmethod
    def get_active_users(cls):
        """获取所有启用的用户"""
        return cls.query.filter_by(status=True).all()

    @classmethod
    def get_by_role(cls, role):
        """根据角色获取用户"""
        return cls.query.filter_by(role=role).all()
    
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, username, password, real_name, email=None, phone=None, role='viewer'):
        """创建新用户"""
        user = cls(
            username=username,
            real_name=real_name,
            email=email,
            phone=phone,
            role=role
        )
        user.set_password(password)
        user.save()
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """用户认证"""
        user = cls.get_by_username(username)
        if user and user.status and user.check_password(password):
            user.update_login_info()
            return user
        return None
    
    def is_admin(self):
        """是否管理员"""
        return self.role == 'admin'
    
    def is_operator(self):
        """是否操作员"""
        return self.role == 'operator'
    
    def is_viewer(self):
        """是否查看者"""
        return self.role == 'viewer'
    
    def can_edit_user(self, target_user):
        """是否能编辑目标用户"""
        if not self.is_admin():
            return False
        # 管理员不能编辑其他管理员（除了自己）
        if target_user.is_admin() and target_user.id != self.id:
            return False
        return True
    
    def can_delete_user(self, target_user):
        """是否能删除目标用户"""
        if not self.is_admin():
            return False
        # 不能删除自己
        if target_user.id == self.id:
            return False
        # 不能删除其他管理员
        if target_user.is_admin():
            return False
        return True
    
    @classmethod
    def get_all(cls):
        """获取所有用户"""
        return cls.query.all()
    
    @classmethod
    def get_total_count(cls):
        """获取用户总数"""
        return cls.query.count()
    
    @classmethod
    def search_by_keyword(cls, keyword):
        """根据关键词搜索用户"""
        from sqlalchemy import or_
        return cls.query.filter(or_(
            cls.username.contains(keyword),
            cls.real_name.contains(keyword),
            cls.email.contains(keyword) if cls.email else False,
            cls.phone.contains(keyword) if cls.phone else False
        )).all()
    
    def get_permissions(self):
        """获取用户权限列表"""
        # 如果用户有具体的角色ID，使用RBAC权限
        if self.role_id:
            from app.models.role import Role
            from app.models.permission import Permission
            from app.models.role import RolePermission
            
            role = Role.get_by_id(self.role_id)
            if role:
                permissions = db.session.query(Permission).join(
                    RolePermission, Permission.id == RolePermission.permission_id
                ).filter(RolePermission.role_id == role.id, Permission.status == True).all()
                return [p.code for p in permissions]
        
        # 兼容旧的角色系统
        if self.role == 'admin':
            return ['read', 'write', 'delete', 'manage']
        elif self.role == 'operator':
            return ['read', 'write']
        else:
            return ['read']
    
    def has_permission(self, permission_code):
        """检查用户是否有指定权限"""
        user_permissions = self.get_permissions()
        return permission_code in user_permissions
    
    def get_menus(self):
        """获取用户可访问的菜单"""
        from app.models.menu import Menu
        user_permissions = self.get_permissions()
        return Menu.get_user_menus(user_permissions)
    
    def get_role_obj(self):
        """获取用户的角色对象"""
        if self.role_id:
            from app.models.role import Role
            return Role.get_by_id(self.role_id)
        return None