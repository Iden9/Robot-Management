from app import db
from datetime import datetime
import json

class SystemSettings(db.Model):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='设置ID')
    category = db.Column(db.String(50), nullable=False, comment='设置分类')
    setting_key = db.Column(db.String(100), nullable=False, comment='设置键名')
    setting_value = db.Column(db.Text, comment='设置值')
    value_type = db.Column(db.Enum('string', 'integer', 'float', 'boolean', 'json'), default='string', comment='值类型')
    description = db.Column(db.String(255), comment='设置描述')
    is_encrypted = db.Column(db.Boolean, default=False, comment='是否加密存储')
    is_system = db.Column(db.Boolean, default=False, comment='是否系统设置(不可删除)')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='更新用户ID')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    updater = db.relationship('User', backref='updated_settings', lazy=True)
    
    def save(self):
        """保存设置"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除设置"""
        if not self.is_system:
            db.session.delete(self)
            db.session.commit()
            return True
        return False
        
    def get_value(self):
        """获取设置值（根据类型转换）"""
        if self.setting_value is None:
            return None
            
        if self.value_type == 'integer':
            return int(self.setting_value)
        elif self.value_type == 'float':
            return float(self.setting_value)
        elif self.value_type == 'boolean':
            return self.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'json':
            return json.loads(self.setting_value)
        else:
            return self.setting_value
    
    def set_value(self, value):
        """设置值（根据类型转换）"""
        if value is None:
            self.setting_value = None
        elif self.value_type == 'json':
            self.setting_value = json.dumps(value, ensure_ascii=False)
        else:
            self.setting_value = str(value)
    
    def to_dict(self):
        """将设置对象转换为字典"""
        return {
            'id': self.id,
            'category': self.category,
            'setting_key': self.setting_key,
            'setting_value': self.get_value(),
            'value_type': self.value_type,
            'description': self.description,
            'is_encrypted': self.is_encrypted,
            'is_system': self.is_system,
            'updated_by': self.updated_by,
            'updater_name': self.updater.real_name if self.updater else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<SystemSettings {self.category}.{self.setting_key}>'
    
    @classmethod
    def get_by_key(cls, category, setting_key):
        """根据分类和键名获取设置"""
        return cls.query.filter_by(category=category, setting_key=setting_key).first()
    
    @classmethod
    def get_by_category(cls, category):
        """根据分类获取设置"""
        return cls.query.filter_by(category=category).all()
    
    @classmethod
    def get_value_by_key(cls, category, setting_key, default=None):
        """获取设置值"""
        setting = cls.get_by_key(category, setting_key)
        return setting.get_value() if setting else default
    
    @classmethod
    def set_value_by_key(cls, category, setting_key, value, value_type='string', description=None, user_id=None):
        """设置值"""
        setting = cls.get_by_key(category, setting_key)
        if setting:
            setting.set_value(value)
            setting.updated_by = user_id
        else:
            setting = cls(
                category=category,
                setting_key=setting_key,
                value_type=value_type,
                description=description,
                updated_by=user_id
            )
            setting.set_value(value)
        setting.save()
        return setting
    
    @classmethod
    def get_server_settings(cls):
        """获取服务器设置"""
        settings = cls.get_by_category('server')
        return {s.setting_key: s.get_value() for s in settings}
    
    @classmethod
    def get_notification_settings(cls):
        """获取通知设置"""
        settings = cls.get_by_category('notification')
        return {s.setting_key: s.get_value() for s in settings}
    
    @classmethod
    def get_security_settings(cls):
        """获取安全设置"""
        settings = cls.get_by_category('security')
        return {s.setting_key: s.get_value() for s in settings}
    
    @classmethod
    def get_data_settings(cls):
        """获取数据设置"""
        settings = cls.get_by_category('data')
        return {s.setting_key: s.get_value() for s in settings}