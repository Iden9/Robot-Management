from app import db
from datetime import datetime

class EquipmentStatusHistory(db.Model):
    """设备状态历史模型"""
    __tablename__ = 'equipment_status_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='历史记录ID')
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, comment='设备ID')
    previous_status = db.Column(db.String(50), comment='之前状态')
    current_status = db.Column(db.String(50), nullable=False, comment='当前状态')
    change_reason = db.Column(db.String(255), comment='状态变更原因')
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='操作用户ID')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    
    # 关系定义
    equipment = db.relationship('Equipment', backref='status_history', lazy=True)
    changer = db.relationship('User', backref='equipment_status_changes', lazy=True)
    
    def save(self):
        """保存状态历史"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除状态历史"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将状态历史对象转换为字典"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'equipment_location': self.equipment.location if self.equipment else None,
            'previous_status': self.previous_status,
            'current_status': self.current_status,
            'change_reason': self.change_reason,
            'changed_by': self.changed_by,
            'changer_name': self.changer.real_name if self.changer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
    def __repr__(self):
        return f'<EquipmentStatusHistory {self.equipment_id}: {self.previous_status} -> {self.current_status}>'
    
    @classmethod
    def get_by_id(cls, history_id):
        """根据ID获取状态历史"""
        return cls.query.get(history_id)
    
    @classmethod
    def get_by_equipment(cls, equipment_id, limit=50):
        """根据设备ID获取状态历史"""
        return cls.query.filter_by(equipment_id=equipment_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_changes(cls, limit=100):
        """获取最近的状态变更"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_changes_by_user(cls, user_id):
        """获取用户的状态变更记录"""
        return cls.query.filter_by(changed_by=user_id).order_by(
            cls.created_at.desc()
        ).all()
    
    @classmethod
    def get_changes_by_date_range(cls, start_date, end_date):
        """根据日期范围获取状态变更"""
        return cls.query.filter(
            cls.created_at >= start_date,
            cls.created_at <= end_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_change_record(cls, equipment_id, previous_status, current_status, 
                           change_reason=None, changed_by=None):
        """创建状态变更记录"""
        history = cls(
            equipment_id=equipment_id,
            previous_status=previous_status,
            current_status=current_status,
            change_reason=change_reason,
            changed_by=changed_by
        )
        history.save()
        return history
    
    def get_status_duration(self):
        """获取状态持续时间（如果有下一个状态）"""
        next_change = EquipmentStatusHistory.query.filter(
            EquipmentStatusHistory.equipment_id == self.equipment_id,
            EquipmentStatusHistory.created_at > self.created_at
        ).order_by(EquipmentStatusHistory.created_at.asc()).first()
        
        if next_change:
            delta = next_change.created_at - self.created_at
            return {
                'seconds': delta.total_seconds(),
                'minutes': delta.total_seconds() / 60,
                'hours': delta.total_seconds() / 3600,
                'days': delta.days
            }
        else:
            # 当前状态的持续时间
            delta = datetime.utcnow() - self.created_at
            return {
                'seconds': delta.total_seconds(),
                'minutes': delta.total_seconds() / 60,
                'hours': delta.total_seconds() / 3600,
                'days': delta.days
            }
    
    @classmethod
    def get_status_statistics(cls, equipment_id, start_date=None, end_date=None):
        """获取设备状态统计"""
        query = cls.query.filter_by(equipment_id=equipment_id)
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        changes = query.order_by(cls.created_at.asc()).all()
        
        if not changes:
            return {}
        
        status_durations = {}
        total_duration = 0
        
        for i, change in enumerate(changes):
            status = change.current_status
            if i < len(changes) - 1:
                # 有下一个状态
                duration = (changes[i + 1].created_at - change.created_at).total_seconds()
            else:
                # 最后一个状态，持续到现在
                end_time = end_date if end_date else datetime.utcnow()
                duration = (end_time - change.created_at).total_seconds()
            
            if status not in status_durations:
                status_durations[status] = 0
            status_durations[status] += duration
            total_duration += duration
        
        # 计算百分比
        status_percentages = {}
        for status, duration in status_durations.items():
            status_percentages[status] = {
                'duration_seconds': duration,
                'duration_hours': duration / 3600,
                'percentage': (duration / total_duration * 100) if total_duration > 0 else 0
            }
        
        return status_percentages