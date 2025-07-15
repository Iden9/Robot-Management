from flask import Blueprint, request, jsonify, current_app
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.auth import require_auth
from app.models.result import Result
from datetime import datetime
import json

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

@knowledge_bp.route('', methods=['GET'])
@require_auth
def get_knowledge_list(current_user):
    """获取知识库列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        
        # 构建查询
        query = KnowledgeBase.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                KnowledgeBase.title.contains(keyword) |
                KnowledgeBase.content.contains(keyword) |
                KnowledgeBase.description.contains(keyword)
            )
        
        # 分类过滤
        if category:
            query = query.filter(KnowledgeBase.category == category)
        
        # 状态过滤
        if status:
            query = query.filter(KnowledgeBase.status == status)
        
        # 按创建时间倒序
        query = query.order_by(KnowledgeBase.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        knowledge_list = [knowledge.to_dict() for knowledge in pagination.items]
        
        return jsonify(Result.success(data={
            'items': knowledge_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取知识库列表失败: {str(e)}")
        return jsonify(Result.error(message="获取知识库列表失败").to_dict())

@knowledge_bp.route('/<int:knowledge_id>', methods=['GET'])
@require_auth
def get_knowledge_detail(current_user, knowledge_id):
    """获取知识库详情"""
    try:
        knowledge = KnowledgeBase.get_by_id(knowledge_id)
        if not knowledge:
            return jsonify(Result.error(message="知识库不存在").to_dict())
        
        # 增加查看次数
        knowledge.increment_view_count()
        
        return jsonify(Result.success(data=knowledge.to_dict()).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取知识库详情失败: {str(e)}")
        return jsonify(Result.error(message="获取知识库详情失败").to_dict())

@knowledge_bp.route('', methods=['POST'])
@require_auth
def create_knowledge(current_user):
    """创建知识库"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify(Result.error(message="标题不能为空").to_dict())
        
        if not data.get('content'):
            return jsonify(Result.error(message="内容不能为空").to_dict())
        
        # 检查标题是否重复
        existing_knowledge = KnowledgeBase.get_by_title(data['title'])
        if existing_knowledge:
            return jsonify(Result.error(message="标题已存在").to_dict())
        
        # 创建知识库
        knowledge = KnowledgeBase(
            title=data['title'],
            content=data['content'],
            description=data.get('description', ''),
            category=data.get('category', ''),
            type=data.get('type', 'text'),
            status=data.get('status', 'published'),
            priority=data.get('priority', 0),
            is_public=data.get('is_public', True),
            source_url=data.get('source_url', ''),
            source_type=data.get('source_type', ''),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        # 设置标签
        if data.get('tags'):
            knowledge.set_tags(data['tags'])
        
        knowledge.save()
        
        return jsonify(Result.success(data=knowledge.to_dict(), message="知识库创建成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"创建知识库失败: {str(e)}")
        return jsonify(Result.error(message="创建知识库失败").to_dict())

@knowledge_bp.route('/<int:knowledge_id>', methods=['PUT'])
@require_auth
def update_knowledge(current_user, knowledge_id):
    """更新知识库"""
    try:
        knowledge = KnowledgeBase.get_by_id(knowledge_id)
        if not knowledge:
            return jsonify(Result.error(message="知识库不存在").to_dict())
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify(Result.error(message="标题不能为空").to_dict())
        
        if not data.get('content'):
            return jsonify(Result.error(message="内容不能为空").to_dict())
        
        # 检查标题是否重复（排除当前记录）
        existing_knowledge = KnowledgeBase.get_by_title(data['title'])
        if existing_knowledge and existing_knowledge.id != knowledge_id:
            return jsonify(Result.error(message="标题已存在").to_dict())
        
        # 更新知识库信息
        knowledge.title = data['title']
        knowledge.content = data['content']
        knowledge.description = data.get('description', '')
        knowledge.category = data.get('category', '')
        knowledge.type = data.get('type', 'text')
        knowledge.status = data.get('status', 'published')
        knowledge.priority = data.get('priority', 0)
        knowledge.is_public = data.get('is_public', True)
        knowledge.source_url = data.get('source_url', '')
        knowledge.source_type = data.get('source_type', '')
        knowledge.updated_by = current_user.id
        
        # 设置标签
        if 'tags' in data:
            knowledge.set_tags(data['tags'])
        
        knowledge.save()
        
        return jsonify(Result.success(data=knowledge.to_dict(), message="知识库更新成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"更新知识库失败: {str(e)}")
        return jsonify(Result.error(message="更新知识库失败").to_dict())

@knowledge_bp.route('/<int:knowledge_id>', methods=['DELETE'])
@require_auth
def delete_knowledge(current_user, knowledge_id):
    """删除知识库"""
    try:
        knowledge = KnowledgeBase.get_by_id(knowledge_id)
        if not knowledge:
            return jsonify(Result.error(message="知识库不存在").to_dict())
        
        knowledge.delete()
        
        return jsonify(Result.success(message="知识库删除成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"删除知识库失败: {str(e)}")
        return jsonify(Result.error(message="删除知识库失败").to_dict())

@knowledge_bp.route('/search', methods=['GET'])
@require_auth
def search_knowledge(current_user):
    """搜索知识库"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空").to_dict())
        
        knowledge_list = KnowledgeBase.search_by_keyword(keyword)
        
        return jsonify(Result.success(data=[knowledge.to_dict() for knowledge in knowledge_list]).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"搜索知识库失败: {str(e)}")
        return jsonify(Result.error(message="搜索知识库失败").to_dict())

@knowledge_bp.route('/categories', methods=['GET'])
@require_auth
def get_knowledge_categories(current_user):
    """获取知识库分类列表"""
    try:
        # 获取所有不同的分类
        categories = KnowledgeBase.query.with_entities(KnowledgeBase.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify(Result.success(data=category_list).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取知识库分类失败: {str(e)}")
        return jsonify(Result.error(message="获取知识库分类失败").to_dict())

@knowledge_bp.route('/popular', methods=['GET'])
@require_auth
def get_popular_knowledge(current_user):
    """获取热门知识库"""
    try:
        limit = request.args.get('limit', 10, type=int)
        knowledge_list = KnowledgeBase.get_popular(limit)
        
        return jsonify(Result.success(data=[knowledge.to_dict() for knowledge in knowledge_list]).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取热门知识库失败: {str(e)}")
        return jsonify(Result.error(message="获取热门知识库失败").to_dict())

@knowledge_bp.route('/<int:knowledge_id>/usage', methods=['POST'])
@require_auth
def record_knowledge_usage(current_user, knowledge_id):
    """记录知识库使用"""
    try:
        knowledge = KnowledgeBase.get_by_id(knowledge_id)
        if not knowledge:
            return jsonify(Result.error(message="知识库不存在").to_dict())
        
        # 增加使用次数
        knowledge.increment_usage_count()
        
        return jsonify(Result.success(message="使用记录成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"记录知识库使用失败: {str(e)}")
        return jsonify(Result.error(message="记录知识库使用失败").to_dict())