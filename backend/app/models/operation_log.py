from app import db
from datetime import datetime, timedelta
import json

class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='用户ID')
    action = db.Column(db.String(255), nullable=False, comment='操作描述')
    details = db.Column(db.Text, comment='操作详情')
    ip_address = db.Column(db.String(50), comment='IP地址')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    
    # 关系定义
    user = db.relationship('User', backref='operation_logs', lazy=True)
    
    def save(self):
        """保存操作日志"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除操作日志"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将操作日志对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'real_name': self.user.real_name if self.user else None,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
    def __repr__(self):
        return f'<OperationLog {self.action} by {self.user.username if self.user else "Unknown"}>'
    
    @classmethod
    def get_by_id(cls, log_id):
        """根据ID获取操作日志"""
        return cls.query.get(log_id)
    
    @classmethod
    def get_by_user(cls, user_id):
        """根据用户ID获取操作日志"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_action(cls, action):
        """根据操作类型获取日志"""
        return cls.query.filter_by(action=action).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_logs(cls, limit=100):
        """获取最近的操作日志"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_date_range(cls, start_date, end_date):
        """根据日期范围获取日志"""
        return cls.query.filter(
            cls.created_at >= start_date,
            cls.created_at <= end_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_logs(cls, keyword):
        """搜索操作日志"""
        return cls.query.filter(
            db.or_(
                cls.action.contains(keyword),
                cls.details.contains(keyword)
            )
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_log(cls, user_id, action, details=None, ip_address=None):
        """创建操作日志"""
        log = cls(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        log.save()
        return log
    
    @classmethod
    def log_user_login(cls, user_id, ip_address=None):
        """记录用户登录日志"""
        return cls.create_log(
            user_id=user_id,
            action='用户登录',
            ip_address=ip_address
        )
    
    @classmethod
    def log_user_logout(cls, user_id, ip_address=None):
        """记录用户登出日志"""
        return cls.create_log(
            user_id=user_id,
            action='用户登出',
            ip_address=ip_address
        )
    
    @classmethod
    def log_operation(cls, user_id, action, details=None, ip_address=None):
        """记录操作日志"""
        return cls.create_log(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
    
    @classmethod
    def log_equipment_operation(cls, user_id, equipment_id, operation, ip_address=None):
        """记录设备操作日志"""
        details = f"设备ID: {equipment_id}"
        return cls.create_log(
            user_id=user_id,
            action=operation,
            details=details,
            ip_address=ip_address
        )
    
    @classmethod
    def log_courseware_operation(cls, user_id, courseware_id, operation, ip_address=None):
        """记录课件操作日志"""
        details = f"课件ID: {courseware_id}"
        return cls.create_log(
            user_id=user_id,
            action=operation,
            details=details,
            ip_address=ip_address
        )
