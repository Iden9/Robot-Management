from app import db
from datetime import datetime

class KnowledgeBase(db.Model):
    """知识库模型"""
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='知识库ID')
    title = db.Column(db.String(255), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    description = db.Column(db.Text, comment='描述')
    category = db.Column(db.String(100), comment='分类')
    tags = db.Column(db.String(500), comment='标签，逗号分隔')
    type = db.Column(db.Enum('text', 'document', 'link', 'faq'), default='text', comment='知识类型')
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='published', comment='状态')
    priority = db.Column(db.Integer, default=0, comment='优先级')
    view_count = db.Column(db.Integer, default=0, comment='查看次数')
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    is_public = db.Column(db.Boolean, default=True, comment='是否公开')
    source_url = db.Column(db.String(500), comment='来源链接')
    source_type = db.Column(db.String(50), comment='来源类型')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='创建用户ID')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='更新用户ID')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_knowledge', lazy=True)
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_knowledge', lazy=True)
    
    def save(self):
        """保存知识库"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除知识库"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将知识库对象转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'description': self.description,
            'category': self.category,
            'tags': self.get_tags_list(),
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'view_count': self.view_count,
            'usage_count': self.usage_count,
            'is_public': self.is_public,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'updater_name': self.updater.real_name if self.updater else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<KnowledgeBase {self.title}>'
    
    @classmethod
    def get_by_id(cls, knowledge_id):
        """根据ID获取知识库"""
        return cls.query.get(knowledge_id)
    
    @classmethod
    def get_by_title(cls, title):
        """根据标题获取知识库"""
        return cls.query.filter_by(title=title).first()
    
    @classmethod
    def get_by_creator(cls, user_id):
        """根据创建者获取知识库"""
        return cls.query.filter_by(created_by=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_category(cls, category):
        """根据分类获取知识库"""
        return cls.query.filter_by(category=category, status='published').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_by_keyword(cls, keyword):
        """根据关键词搜索知识库"""
        return cls.query.filter(
            db.and_(
                cls.status == 'published',
                db.or_(
                    cls.title.contains(keyword),
                    cls.content.contains(keyword),
                    cls.description.contains(keyword),
                    cls.tags.contains(keyword)
                )
            )
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_all_ordered(cls):
        """获取所有知识库，按创建时间倒序"""
        return cls.query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_published(cls):
        """获取已发布的知识库"""
        return cls.query.filter_by(status='published', is_public=True).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_popular(cls, limit=10):
        """获取热门知识库"""
        return cls.query.filter_by(status='published').order_by(
            cls.usage_count.desc(), cls.view_count.desc()
        ).limit(limit).all()
    
    def get_tags_list(self):
        """获取标签列表"""
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    
    def set_tags(self, tags_list):
        """设置标签"""
        self.tags = ','.join(tags_list) if tags_list else None
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save()
    
    def increment_usage_count(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save()
    
    def publish(self):
        """发布知识库"""
        self.status = 'published'
        self.save()
    
    def archive(self):
        """归档知识库"""
        self.status = 'archived'
        self.save()
    
    def update_info(self, title=None, content=None, description=None, category=None, tags=None, updated_by=None):
        """更新知识库信息"""
        if title:
            self.title = title
        if content:
            self.content = content
        if description is not None:
            self.description = description
        if category:
            self.category = category
        if tags is not None:
            self.set_tags(tags)
        if updated_by:
            self.updated_by = updated_by
        self.save()