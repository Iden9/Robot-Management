from app import db
from datetime import datetime

class CoursewareCategory(db.Model):
    """课件分类模型"""
    __tablename__ = 'courseware_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='分类ID')
    name = db.Column(db.String(100), nullable=False, comment='分类名称')
    description = db.Column(db.Text, comment='分类描述')
    parent_id = db.Column(db.Integer, db.ForeignKey('courseware_categories.id', ondelete='SET NULL'), comment='父分类ID')
    sort_order = db.Column(db.Integer, default=0, comment='排序序号')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    children = db.relationship('CoursewareCategory', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    # courseware_items relationship is defined in Courseware model with backref
    
    def save(self):
        """保存分类"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除分类"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将分类对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'children_count': self.children.count(),
            'courseware_count': len(self.courseware_items),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<CoursewareCategory {self.name}>'
    
    @classmethod
    def get_by_id(cls, category_id):
        """根据ID获取分类"""
        return cls.query.get(category_id)
    
    @classmethod
    def get_by_name(cls, name):
        """根据名称获取分类"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_root_categories(cls):
        """获取根分类"""
        return cls.query.filter_by(parent_id=None, is_active=True).order_by(cls.sort_order).all()
    
    @classmethod
    def get_children(cls, parent_id):
        """获取子分类"""
        return cls.query.filter_by(parent_id=parent_id, is_active=True).order_by(cls.sort_order).all()
    
    @classmethod
    def get_active_categories(cls):
        """获取所有启用的分类"""
        return cls.query.filter_by(is_active=True).order_by(cls.sort_order).all()
    
    @classmethod
    def get_all(cls):
        """获取所有分类"""
        return cls.query.order_by(cls.sort_order).all()
    
    def get_full_path(self):
        """获取完整路径"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)
    
    def get_all_children(self):
        """获取所有子分类（递归）"""
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def can_delete(self):
        """是否可以删除"""
        # 如果有子分类或课件，则不能删除
        return self.children.count() == 0 and len(self.courseware_items) == 0
    
    def activate(self):
        """启用分类"""
        self.is_active = True
        self.save()
    
    def deactivate(self):
        """禁用分类"""
        self.is_active = False
        self.save()