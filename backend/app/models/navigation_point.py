from app import db
from datetime import datetime

class NavigationPoint(db.Model):
    """导览点位模型"""
    __tablename__ = 'navigation_points'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='点位ID')
    equipment_id = db.Column(db.String(50), db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, comment='设备ID')
    name = db.Column(db.String(100), nullable=False, comment='点位名称')
    description = db.Column(db.Text, comment='点位描述')
    x_position = db.Column(db.Float, nullable=False, comment='X坐标')
    y_position = db.Column(db.Float, nullable=False, comment='Y坐标')
    rotation = db.Column(db.Float, default=0, comment='朝向角度')
    enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    def save(self):
        """保存点位"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除点位"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将点位对象转换为字典"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'name': self.name,
            'description': self.description,
            'x_position': self.x_position,
            'y_position': self.y_position,
            'rotation': self.rotation,
            'enabled': self.enabled
        }
        
    def __repr__(self):
        return f'<NavigationPoint {self.name}>'
    
    @classmethod
    def get_by_id(cls, point_id):
        """根据ID获取点位"""
        return cls.query.get(point_id)
    
    @classmethod
    def get_by_equipment(cls, equipment_id):
        """根据设备ID获取点位列表"""
        return cls.query.filter_by(equipment_id=equipment_id).all()
    
    @classmethod
    def get_enabled_points(cls, equipment_id):
        """获取启用的点位"""
        return cls.query.filter_by(equipment_id=equipment_id, enabled=True).all()
    
    @classmethod
    def create_point(cls, equipment_id, **kwargs):
        """创建点位"""
        point = cls(
            equipment_id=equipment_id,
            **kwargs
        )
        point.save()
        return point