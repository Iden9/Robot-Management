from app import db
from datetime import datetime

class EducationSettings(db.Model):
    """教育培训设置模型"""
    __tablename__ = 'education_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='设置ID')
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, comment='设备ID')
    screen_sync_mode = db.Column(db.Enum('auto', 'manual', 'off'), default='auto', comment='屏幕同步模式')
    ai_platform = db.Column(db.String(50), default='xunfei', comment='AI平台')
    subject = db.Column(db.String(50), comment='学科')
    voice_type = db.Column(db.String(50), default='male', comment='语音类型')
    robot_action = db.Column(db.String(50), default='standard', comment='机器人动作')
    hand_recognition = db.Column(db.Boolean, default=True, comment='手势识别')
    interactive_qa = db.Column(db.Boolean, default=True, comment='互动问答')
    navigation_mode = db.Column(db.String(50), default='default', comment='导航模式')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='更新者ID')
    
    # 关系定义
    updater = db.relationship('User', backref='education_settings_updates', lazy=True)
    
    def save(self):
        """保存教育设置"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除教育设置"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将教育设置对象转换为字典"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'screen_sync_mode': self.screen_sync_mode,
            'ai_platform': self.ai_platform,
            'subject': self.subject,
            'voice_type': self.voice_type,
            'robot_action': self.robot_action,
            'hand_recognition': self.hand_recognition,
            'interactive_qa': self.interactive_qa,
            'navigation_mode': self.navigation_mode,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'updater_name': self.updater.real_name if self.updater else None
        }
        
    def __repr__(self):
        return f'<EducationSettings {self.id}>'
    
    @classmethod
    def get_by_id(cls, setting_id):
        """根据ID获取教育设置"""
        return cls.query.get(setting_id)
    
    @classmethod
    def get_by_equipment(cls, equipment_id):
        """根据设备ID获取教育设置"""
        return cls.query.filter_by(equipment_id=equipment_id).first()
    
    @classmethod
    def get_all(cls):
        """获取所有教育设置"""
        return cls.query.all()
    
    @classmethod
    def create_setting(cls, equipment_id, **kwargs):
        """创建教育设置"""
        setting = cls(
            equipment_id=equipment_id,
            **kwargs
        )
        setting.save()
        return setting
    
    def update_setting(self, **kwargs):
        """更新教育设置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self