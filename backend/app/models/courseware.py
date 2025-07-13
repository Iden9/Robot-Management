from app import db
from datetime import datetime

class Courseware(db.Model):
    """课件模型"""
    __tablename__ = 'courseware'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='课件ID')
    title = db.Column(db.String(255), nullable=False, comment='课件标题')
    category_id = db.Column(db.Integer, db.ForeignKey('courseware_categories.id', ondelete='SET NULL'), comment='分类ID')
    file_path = db.Column(db.String(500), nullable=False, comment='文件存储路径')
    file_name = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_type = db.Column(db.String(50), nullable=False, comment='文件类型')
    file_size = db.Column(db.BigInteger, nullable=False, comment='文件大小(字节)')
    mime_type = db.Column(db.String(100), comment='MIME类型')
    description = db.Column(db.Text, comment='课件描述')
    tags = db.Column(db.String(500), comment='标签，逗号分隔')
    subject = db.Column(db.String(100), comment='学科')
    grade_level = db.Column(db.String(50), comment='年级水平')
    duration = db.Column(db.Integer, comment='播放时长(秒)')
    thumbnail_path = db.Column(db.String(500), comment='缩略图路径')
    download_count = db.Column(db.Integer, default=0, comment='下载次数')
    view_count = db.Column(db.Integer, default=0, comment='查看次数')
    is_public = db.Column(db.Boolean, default=True, comment='是否公开')
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='published', comment='状态')
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), comment='上传用户ID')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    uploader = db.relationship('User', backref='uploaded_courseware', lazy=True)
    category = db.relationship('CoursewareCategory', backref='courseware_items', lazy=True)
    
    def save(self):
        """保存课件"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除课件"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将课件对象转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'mime_type': self.mime_type,
            'description': self.description,
            'tags': self.get_tags_list(),
            'subject': self.subject,
            'grade_level': self.grade_level,
            'duration': self.duration,
            'thumbnail_path': self.thumbnail_path,
            'download_count': self.download_count,
            'view_count': self.view_count,
            'is_public': self.is_public,
            'status': self.status,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.real_name if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def __repr__(self):
        return f'<Courseware {self.title}>'
    
    @classmethod
    def get_by_id(cls, courseware_id):
        """根据ID获取课件"""
        return cls.query.get(courseware_id)
    
    @classmethod
    def get_by_title(cls, title):
        """根据标题获取课件"""
        return cls.query.filter_by(title=title).first()
    
    @classmethod
    def get_by_uploader(cls, user_id):
        """根据上传者获取课件"""
        return cls.query.filter_by(uploaded_by=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_file_type(cls, file_type):
        """根据文件类型获取课件"""
        return cls.query.filter_by(file_type=file_type).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_by_title(cls, keyword):
        """根据标题关键词搜索课件"""
        return cls.query.filter(cls.title.contains(keyword)).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_courseware(cls, limit=20):
        """获取最近上传的课件"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_all_ordered(cls):
        """获取所有课件，按创建时间倒序"""
        return cls.query.order_by(cls.created_at.desc()).all()
    
    def get_file_size_mb(self):
        """获取文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
    
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
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save()
    
    def publish(self):
        """发布课件"""
        self.status = 'published'
        self.save()
    
    def archive(self):
        """归档课件"""
        self.status = 'archived'
        self.save()
    
    def update_info(self, title=None, description=None, tags=None, subject=None, grade_level=None):
        """更新课件信息"""
        if title:
            self.title = title
        if description is not None:
            self.description = description
        if tags is not None:
            self.set_tags(tags)
        if subject:
            self.subject = subject
        if grade_level:
            self.grade_level = grade_level
        self.save()
    
    @classmethod
    def get_published(cls):
        """获取已发布的课件"""
        return cls.query.filter_by(status='published', is_public=True).all()
    
    @classmethod
    def get_by_category(cls, category_id):
        """根据分类获取课件"""
        return cls.query.filter_by(category_id=category_id, status='published').all()
    
    @classmethod
    def search_courseware(cls, keyword):
        """搜索课件"""
        return cls.query.filter(
            db.and_(
                cls.status == 'published',
                db.or_(
                    cls.title.contains(keyword),
                    cls.description.contains(keyword),
                    cls.tags.contains(keyword)
                )
            )
        ).all()
    
    @classmethod
    def get_popular_courseware(cls, limit=10):
        """获取热门课件"""
        return cls.query.filter_by(status='published').order_by(
            cls.view_count.desc(), cls.download_count.desc()
        ).limit(limit).all()
