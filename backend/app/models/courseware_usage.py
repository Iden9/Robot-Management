from app import db
from datetime import datetime, timedelta

class CoursewareUsage(db.Model):
    """课件使用记录模型"""
    __tablename__ = 'courseware_usage'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='使用记录ID')
    courseware_id = db.Column(db.Integer, db.ForeignKey('courseware.id', ondelete='CASCADE'), nullable=False, comment='课件ID')
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, comment='设备ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='操作用户ID')
    action = db.Column(db.Enum('play', 'download', 'view', 'share'), nullable=False, comment='操作类型')
    duration = db.Column(db.Integer, comment='使用时长(秒)')
    ip_address = db.Column(db.String(50), comment='IP地址')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    
    # 关系定义
    courseware = db.relationship('Courseware', backref='usage_records', lazy=True)
    equipment = db.relationship('Equipment', backref='courseware_usage', lazy=True)
    user = db.relationship('User', backref='courseware_usage', lazy=True)
    
    def save(self):
        """保存使用记录"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除使用记录"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将使用记录对象转换为字典"""
        return {
            'id': self.id,
            'courseware_id': self.courseware_id,
            'courseware_title': self.courseware.title if self.courseware else None,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'equipment_location': self.equipment.location if self.equipment else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'user_real_name': self.user.real_name if self.user else None,
            'action': self.action,
            'action_display': self.get_action_display(),
            'duration': self.duration,
            'duration_display': self.get_duration_display(),
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_action_display(self):
        """获取操作类型显示文本"""
        action_map = {
            'play': '播放',
            'download': '下载',
            'view': '查看',
            'share': '分享'
        }
        return action_map.get(self.action, '未知')
    
    def get_duration_display(self):
        """获取时长显示文本"""
        if not self.duration:
            return None
        
        if self.duration < 60:
            return f"{self.duration}秒"
        elif self.duration < 3600:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes}分{seconds}秒"
        else:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            return f"{hours}小时{minutes}分钟"
        
    def __repr__(self):
        return f'<CoursewareUsage {self.action} courseware {self.courseware_id} on {self.equipment_id}>'
    
    @classmethod
    def get_by_id(cls, usage_id):
        """根据ID获取使用记录"""
        return cls.query.get(usage_id)
    
    @classmethod
    def get_by_courseware(cls, courseware_id, limit=100):
        """根据课件ID获取使用记录"""
        return cls.query.filter_by(courseware_id=courseware_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_equipment(cls, equipment_id, limit=100):
        """根据设备ID获取使用记录"""
        return cls.query.filter_by(equipment_id=equipment_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户ID获取使用记录"""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_usage(cls, limit=100):
        """获取最近的使用记录"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_usage_by_date_range(cls, start_date, end_date):
        """根据日期范围获取使用记录"""
        return cls.query.filter(
            cls.created_at >= start_date,
            cls.created_at <= end_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_usage_record(cls, courseware_id, equipment_id, action, user_id=None, 
                          duration=None, ip_address=None):
        """创建使用记录"""
        usage = cls(
            courseware_id=courseware_id,
            equipment_id=equipment_id,
            action=action,
            user_id=user_id,
            duration=duration,
            ip_address=ip_address
        )
        usage.save()
        return usage
    
    @classmethod
    def get_courseware_statistics(cls, courseware_id, days=30):
        """获取课件使用统计"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        usage_records = cls.query.filter(
            cls.courseware_id == courseware_id,
            cls.created_at >= start_date
        ).all()
        
        stats = {
            'total_usage': len(usage_records),
            'play_count': 0,
            'download_count': 0,
            'view_count': 0,
            'share_count': 0,
            'total_duration': 0,
            'average_duration': 0,
            'unique_users': set(),
            'unique_equipment': set(),
            'daily_usage': {}
        }
        
        for record in usage_records:
            # 统计各种操作
            if record.action == 'play':
                stats['play_count'] += 1
            elif record.action == 'download':
                stats['download_count'] += 1
            elif record.action == 'view':
                stats['view_count'] += 1
            elif record.action == 'share':
                stats['share_count'] += 1
            
            # 统计时长
            if record.duration:
                stats['total_duration'] += record.duration
            
            # 统计用户和设备
            if record.user_id:
                stats['unique_users'].add(record.user_id)
            stats['unique_equipment'].add(record.equipment_id)
            
            # 按日期统计
            date_key = record.created_at.date().isoformat()
            if date_key not in stats['daily_usage']:
                stats['daily_usage'][date_key] = 0
            stats['daily_usage'][date_key] += 1
        
        # 计算平均时长
        duration_records = [r for r in usage_records if r.duration]
        if duration_records:
            stats['average_duration'] = stats['total_duration'] / len(duration_records)
        
        # 转换集合为计数
        stats['unique_users'] = len(stats['unique_users'])
        stats['unique_equipment'] = len(stats['unique_equipment'])
        
        return stats
    
    @classmethod
    def get_equipment_usage_statistics(cls, equipment_id, days=30):
        """获取设备使用统计"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        usage_records = cls.query.filter(
            cls.equipment_id == equipment_id,
            cls.created_at >= start_date
        ).all()
        
        stats = {
            'total_usage': len(usage_records),
            'unique_courseware': set(),
            'popular_courseware': {},
            'usage_by_action': {},
            'daily_usage': {}
        }
        
        for record in usage_records:
            # 统计课件
            stats['unique_courseware'].add(record.courseware_id)
            
            # 统计热门课件
            if record.courseware_id not in stats['popular_courseware']:
                stats['popular_courseware'][record.courseware_id] = 0
            stats['popular_courseware'][record.courseware_id] += 1
            
            # 按操作类型统计
            if record.action not in stats['usage_by_action']:
                stats['usage_by_action'][record.action] = 0
            stats['usage_by_action'][record.action] += 1
            
            # 按日期统计
            date_key = record.created_at.date().isoformat()
            if date_key not in stats['daily_usage']:
                stats['daily_usage'][date_key] = 0
            stats['daily_usage'][date_key] += 1
        
        # 转换集合为计数
        stats['unique_courseware'] = len(stats['unique_courseware'])
        
        # 排序热门课件
        stats['popular_courseware'] = dict(
            sorted(stats['popular_courseware'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        return stats