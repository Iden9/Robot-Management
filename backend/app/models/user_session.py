from app import db
from datetime import datetime, timedelta
import json
import uuid

class UserSession(db.Model):
    """用户会话模型"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(128), primary_key=True, comment='会话ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    ip_address = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='用户代理')
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='登录时间')
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='最后活动时间')
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    session_data = db.Column(db.Text, comment='会话数据(JSON)')
    
    # 关系定义
    user = db.relationship('User', backref='sessions', lazy=True)
    
    def __init__(self, user_id, ip_address=None, user_agent=None, expires_in_hours=24):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        self.session_data = '{}'
    
    def save(self):
        """保存会话"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除会话"""
        db.session.delete(self)
        db.session.commit()
        
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.utcnow()
        self.save()
    
    def extend_session(self, hours=24):
        """延长会话"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.save()
    
    def set_data(self, key, value):
        """设置会话数据"""
        data = self.get_all_data()
        data[key] = value
        self.session_data = json.dumps(data, ensure_ascii=False)
        self.save()
    
    def get_data(self, key, default=None):
        """获取会话数据"""
        data = self.get_all_data()
        return data.get(key, default)
    
    def get_all_data(self):
        """获取所有会话数据"""
        try:
            return json.loads(self.session_data) if self.session_data else {}
        except json.JSONDecodeError:
            return {}
    
    def is_expired(self):
        """是否已过期"""
        return datetime.utcnow() > self.expires_at
    
    def invalidate(self):
        """使会话失效"""
        self.is_active = False
        self.save()
    
    def to_dict(self):
        """将会话对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'session_data': self.get_all_data()
        }
        
    def __repr__(self):
        return f'<UserSession {self.id[:8]}... for user {self.user_id}>'
    
    @classmethod
    def get_by_id(cls, session_id):
        """根据ID获取会话"""
        return cls.query.get(session_id)
    
    @classmethod
    def get_active_session(cls, session_id):
        """获取活跃会话"""
        session = cls.get_by_id(session_id)
        if session and session.is_active and not session.is_expired():
            return session
        return None
    
    @classmethod
    def get_user_sessions(cls, user_id, active_only=True):
        """获取用户的所有会话"""
        query = cls.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.last_activity.desc()).all()
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """清理过期会话"""
        expired_sessions = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.delete()
        
        return len(expired_sessions)
    
    @classmethod
    def invalidate_user_sessions(cls, user_id, exclude_session_id=None):
        """使用户的所有会话失效"""
        query = cls.query.filter_by(user_id=user_id, is_active=True)
        if exclude_session_id:
            query = query.filter(cls.id != exclude_session_id)
        
        sessions = query.all()
        for session in sessions:
            session.invalidate()
        
        return len(sessions)
    
    @classmethod
    def create_session(cls, user_id, ip_address=None, user_agent=None, expires_in_hours=24):
        """创建新会话"""
        session = cls(user_id, ip_address, user_agent, expires_in_hours)
        session.save()
        return session