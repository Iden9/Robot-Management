from app import db
from datetime import datetime

class NavigationSettings(db.Model):
    """导览设置模型"""
    __tablename__ = 'navigation_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='设置ID')
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, comment='设备ID')
    scene_type = db.Column(db.String(50), default='scenic', comment='场景类型')
    ai_platform = db.Column(db.String(50), default='xunfei', comment='AI平台')
    voice_type = db.Column(db.String(50), default='male', comment='语音类型')
    scene_prompt = db.Column(db.Text, comment='场景提示词')
    object_recognition = db.Column(db.Boolean, default=True, comment='对象识别')
    recognition_action = db.Column(db.String(50), default='move', comment='识别动作')
    auto_follow = db.Column(db.Boolean, default=False, comment='自动跟随')
    patrol_mode = db.Column(db.String(50), default='standard', comment='巡逻模式')
    navigation_mode = db.Column(db.String(50), default='dynamic', comment='导航模式')
    emergency_alert = db.Column(db.Boolean, default=True, comment='紧急报警')
    alert_mode = db.Column(db.String(50), default='auto', comment='报警模式')
    robot_speed = db.Column(db.Integer, default=50, comment='机器人速度(0-100)')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='更新者ID')
    
    # 关系定义
    updater = db.relationship('User', backref='navigation_settings_updates', lazy=True)
    
    def save(self):
        """保存导览设置"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除导览设置"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将导览设置对象转换为字典"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'scene_type': self.scene_type,
            'ai_platform': self.ai_platform,
            'voice_type': self.voice_type,
            'scene_prompt': self.scene_prompt,
            'object_recognition': self.object_recognition,
            'recognition_action': self.recognition_action,
            'auto_follow': self.auto_follow,
            'patrol_mode': self.patrol_mode,
            'navigation_mode': self.navigation_mode,
            'emergency_alert': self.emergency_alert,
            'alert_mode': self.alert_mode,
            'robot_speed': self.robot_speed,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'updater_name': self.updater.real_name if self.updater else None
        }
        
    def __repr__(self):
        return f'<NavigationSettings {self.id}>'
    
    @classmethod
    def get_by_id(cls, setting_id):
        """根据ID获取导览设置"""
        return cls.query.get(setting_id)
    
    @classmethod
    def get_by_equipment(cls, equipment_id):
        """根据设备ID获取导览设置"""
        return cls.query.filter_by(equipment_id=equipment_id).first()
    
    @classmethod
    def get_all(cls):
        """获取所有导览设置"""
        return cls.query.all()
    
    @classmethod
    def create_setting(cls, equipment_id, **kwargs):
        """创建导览设置"""
        setting = cls(
            equipment_id=equipment_id,
            **kwargs
        )
        setting.save()
        return setting
    
    def update_setting(self, **kwargs):
        """更新导览设置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self