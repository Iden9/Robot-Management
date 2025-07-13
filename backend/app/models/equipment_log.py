from app import db
from datetime import datetime

class EquipmentLog(db.Model):
    """设备诊断/日志模型"""
    __tablename__ = 'equipment_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)
    log_type = db.Column(db.Enum('error', 'warning', 'info', 'debug'), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def save(self):
        """保存日志"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除日志"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将日志对象转换为字典"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'log_type': self.log_type,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
    def __repr__(self):
        return f'<EquipmentLog {self.id}: {self.log_type}>'
    
    @classmethod
    def get_by_id(cls, log_id):
        """根据ID获取日志"""
        return cls.query.get(log_id)
    
    @classmethod
    def get_by_equipment(cls, equipment_id):
        """根据设备ID获取所有日志"""
        return cls.query.filter_by(equipment_id=equipment_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_type(cls, log_type):
        """根据日志类型获取日志"""
        return cls.query.filter_by(log_type=log_type).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_error_logs(cls):
        """获取所有错误日志"""
        return cls.query.filter_by(log_type='error').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_logs(cls, limit=100):
        """获取最近的日志"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_date_range(cls, start_date, end_date):
        """根据日期范围获取日志"""
        return cls.query.filter(
            cls.created_at >= start_date,
            cls.created_at <= end_date
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_log(cls, equipment_id, log_type, message):
        """创建新日志"""
        log = cls(
            equipment_id=equipment_id,
            log_type=log_type,
            message=message
        )
        log.save()
        return log
