from app import db
from datetime import datetime

class Equipment(db.Model):
    """设备模型"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.String(50), primary_key=True, comment='设备唯一标识，如G1-EDU-001')
    location = db.Column(db.String(255), nullable=False, comment='设备所在位置')
    status = db.Column(db.String(50), comment='设备当前状态')
    ip_address = db.Column(db.String(50), comment='IP地址')
    last_active = db.Column(db.DateTime, comment='最后活跃时间')
    usage_rate = db.Column(db.String(10), comment='使用率')
    is_offline = db.Column(db.Boolean, default=False, comment='离线状态: 1-离线, 0-在线')
    has_error = db.Column(db.Boolean, default=False, comment='错误状态: 1-有错误, 0-正常')
    # maintenance_mode = db.Column(db.Boolean, default=False, comment='维护模式: 1-维护中, 0-正常')  # TODO: Add via migration
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    equipment_logs = db.relationship('EquipmentLog', backref='equipment', lazy=True, cascade='all, delete-orphan')
    education_settings = db.relationship('EducationSettings', backref='equipment', lazy=True, cascade='all, delete-orphan')
    navigation_settings = db.relationship('NavigationSettings', backref='equipment', lazy=True, cascade='all, delete-orphan')
    navigation_points = db.relationship('NavigationPoint', backref='equipment', lazy=True, cascade='all, delete-orphan')
    
    def save(self):
        """保存设备"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除设备"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将设备对象转换为字典"""
        return {
            'id': self.id,
            'name': self.id,  # 使用id作为显示名称
            'location': self.location,
            'status': self.status,
            'ip_address': self.ip_address,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'usage_rate': self.usage_rate,
            'is_offline': self.is_offline,
            'has_error': self.has_error,
            'maintenance_mode': getattr(self, 'maintenance_mode', False),
            'health_score': self.get_health_score(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<Equipment {self.id}>'
    
    @classmethod
    def get_by_id(cls, equipment_id):
        """根据ID获取设备"""
        return cls.query.get(equipment_id)
    
    @classmethod
    def get_online_equipment(cls):
        """获取所有在线设备"""
        return cls.query.filter_by(is_offline=False).all()
    
    @classmethod
    def get_offline_equipment(cls):
        """获取所有离线设备"""
        return cls.query.filter_by(is_offline=True).all()
    
    @classmethod
    def get_error_equipment(cls):
        """获取所有有错误的设备"""
        return cls.query.filter_by(has_error=True).all()
    
    @classmethod
    def get_by_location(cls, location):
        """根据位置获取设备"""
        return cls.query.filter_by(location=location).all()
    
    def update_status(self, status):
        """更新设备状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
        self.save()
    
    def set_offline(self, offline=True):
        """设置设备离线状态"""
        self.is_offline = offline
        self.updated_at = datetime.utcnow()
        self.save()
    
    def set_error(self, has_error=True):
        """设置设备错误状态"""
        self.has_error = has_error
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_last_active(self):
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()
        self.save()
    
    def set_maintenance_mode(self, maintenance=True):
        """设置维护模式"""
        # Temporarily disabled until maintenance_mode column is added via migration
        if maintenance:
            self.status = 'maintenance'
        else:
            self.status = 'online' if not self.is_offline else 'offline'
        self.updated_at = datetime.utcnow()
        self.save()
    
    def toggle_maintenance_mode(self):
        """切换维护模式"""
        # Temporarily disabled until maintenance_mode column is added via migration
        current_maintenance = self.status == 'maintenance'
        self.set_maintenance_mode(not current_maintenance)
    
    # def update_battery_level(self, level):
    #     """更新电池电量"""
    #     if 0 <= level <= 100:
    #         self.battery_level = level
    #         self.save()
    
    def update_usage_rate(self, rate):
        """更新使用率"""
        if 0 <= rate <= 100:
            self.usage_rate = rate
            self.save()
    
    def get_status_display(self):
        """获取状态显示文本"""
        status_map = {
            'online': '在线',
            'offline': '离线',
            'teaching': '教学中',
            'touring': '导览中',
            'standby': '待机中',
            'maintenance': '维护中'
        }
        return status_map.get(self.status, '未知')
    
    def is_online(self):
        """是否在线"""
        return not self.is_offline and not self.has_error
    
    def is_available(self):
        """是否可用"""
        return self.is_online() and self.status != 'maintenance'
    
    def get_health_score(self):
        """获取设备健康分数"""
        score = 100
        if self.is_offline:
            score -= 50
        if self.has_error:
            score -= 30
        # if self.battery_level < 20:
        #     score -= 20
        return max(0, score)
    
    @classmethod
    def get_online_count(cls):
        """获取在线设备数量"""
        return cls.query.filter_by(is_offline=False).count()
    
    @classmethod
    def get_offline_count(cls):
        """获取离线设备数量"""
        return cls.query.filter_by(is_offline=True).count()
    
    @classmethod
    def get_error_count(cls):
        """获取故障设备数量"""
        return cls.query.filter_by(has_error=True).count()
    
    @classmethod
    def get_maintenance_count(cls):
        """获取维护中设备数量"""
        return cls.query.filter_by(status='maintenance').count()
    
    @classmethod
    def get_by_status(cls, status):
        """根据状态获取设备列表"""
        return cls.query.filter_by(status=status).all()
    
    @classmethod
    def search_equipment(cls, keyword):
        """搜索设备"""
        return cls.query.filter(
            db.or_(
                cls.id.contains(keyword),
                cls.location.contains(keyword)
            )
        ).all()
    
    def start(self):
        """启动设备"""
        self.is_offline = False
        self.has_error = False
        self.status = 'online'
        self.last_active = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.save()
    
    def stop(self):
        """停止设备"""
        self.is_offline = True
        self.status = 'offline'
        self.updated_at = datetime.utcnow()
        self.save()
    
    def restart(self):
        """重启设备"""
        self.status = 'offline'
        self.updated_at = datetime.utcnow()
        self.save()
        # 模拟重启过程
        import time
        time.sleep(1)
        self.is_offline = False
        self.has_error = False
        self.status = 'online'
        self.last_active = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.save()
    
    def shutdown(self):
        """关闭设备"""
        self.is_offline = True
        self.status = 'offline'
        self.updated_at = datetime.utcnow()
        self.save()
    
    def reboot(self):
        """重新启动设备"""
        self.restart()
    
    def diagnose(self):
        """设备诊断"""
        # 模拟诊断过程
        diagnosis_result = {
            'status': 'healthy' if not self.has_error else 'error',
            'health_score': self.get_health_score(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_offline': self.is_offline,
            'has_error': self.has_error
        }
        return diagnosis_result
