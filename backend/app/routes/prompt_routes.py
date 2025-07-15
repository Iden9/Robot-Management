from flask import Blueprint, request, jsonify, current_app
from app.models.prompt_template import PromptTemplate
from app.models.user import User
from app.auth import require_auth
from app.models.result import Result
from datetime import datetime
import json

prompt_bp = Blueprint('prompt', __name__, url_prefix='/api/prompt')

@prompt_bp.route('', methods=['GET'])
@require_auth
def get_prompt_list(current_user):
    """获取提示词模板列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        template_type = request.args.get('type', '').strip()
        
        # 构建查询
        query = PromptTemplate.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                PromptTemplate.title.contains(keyword) |
                PromptTemplate.content.contains(keyword) |
                PromptTemplate.description.contains(keyword)
            )
        
        # 分类过滤
        if category:
            query = query.filter(PromptTemplate.category == category)
        
        # 状态过滤
        if status:
            query = query.filter(PromptTemplate.status == status)
        
        # 类型过滤
        if template_type:
            query = query.filter(PromptTemplate.type == template_type)
        
        # 按创建时间倒序
        query = query.order_by(PromptTemplate.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        prompt_list = [prompt.to_dict() for prompt in pagination.items]
        
        return jsonify(Result.success(data={
            'items': prompt_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取提示词模板列表失败: {str(e)}")
        return jsonify(Result.error(message="获取提示词模板列表失败").to_dict())

@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
@require_auth
def get_prompt_detail(current_user, prompt_id):
    """获取提示词模板详情"""
    try:
        prompt = PromptTemplate.get_by_id(prompt_id)
        if not prompt:
            return jsonify(Result.error(message="提示词模板不存在").to_dict())
        
        # 增加查看次数
        prompt.increment_view_count()
        
        return jsonify(Result.success(data=prompt.to_dict()).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取提示词模板详情失败: {str(e)}")
        return jsonify(Result.error(message="获取提示词模板详情失败").to_dict())

@prompt_bp.route('', methods=['POST'])
@require_auth
def create_prompt(current_user):
    """创建提示词模板"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify(Result.error(message="标题不能为空").to_dict())
        
        if not data.get('content'):
            return jsonify(Result.error(message="内容不能为空").to_dict())
        
        # 检查标题是否重复
        existing_prompt = PromptTemplate.get_by_title(data['title'])
        if existing_prompt:
            return jsonify(Result.error(message="标题已存在").to_dict())
        
        # 创建提示词模板
        prompt = PromptTemplate(
            title=data['title'],
            content=data['content'],
            description=data.get('description', ''),
            category=data.get('category', ''),
            type=data.get('type', 'general'),
            status=data.get('status', 'published'),
            priority=data.get('priority', 0),
            is_public=data.get('is_public', True),
            variables=data.get('variables', ''),
            example_input=data.get('example_input', ''),
            example_output=data.get('example_output', ''),
            model_type=data.get('model_type', ''),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        # 设置标签
        if data.get('tags'):
            prompt.set_tags(data['tags'])
        
        prompt.save()
        
        return jsonify(Result.success(data=prompt.to_dict(), message="提示词模板创建成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"创建提示词模板失败: {str(e)}")
        return jsonify(Result.error(message="创建提示词模板失败").to_dict())

@prompt_bp.route('/<int:prompt_id>', methods=['PUT'])
@require_auth
def update_prompt(current_user, prompt_id):
    """更新提示词模板"""
    try:
        prompt = PromptTemplate.get_by_id(prompt_id)
        if not prompt:
            return jsonify(Result.error(message="提示词模板不存在").to_dict())
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify(Result.error(message="标题不能为空").to_dict())
        
        if not data.get('content'):
            return jsonify(Result.error(message="内容不能为空").to_dict())
        
        # 检查标题是否重复（排除当前记录）
        existing_prompt = PromptTemplate.get_by_title(data['title'])
        if existing_prompt and existing_prompt.id != prompt_id:
            return jsonify(Result.error(message="标题已存在").to_dict())
        
        # 更新提示词模板信息
        prompt.title = data['title']
        prompt.content = data['content']
        prompt.description = data.get('description', '')
        prompt.category = data.get('category', '')
        prompt.type = data.get('type', 'general')
        prompt.status = data.get('status', 'published')
        prompt.priority = data.get('priority', 0)
        prompt.is_public = data.get('is_public', True)
        prompt.variables = data.get('variables', '')
        prompt.example_input = data.get('example_input', '')
        prompt.example_output = data.get('example_output', '')
        prompt.model_type = data.get('model_type', '')
        prompt.temperature = data.get('temperature', 0.7)
        prompt.max_tokens = data.get('max_tokens')
        prompt.updated_by = current_user.id
        
        # 设置标签
        if 'tags' in data:
            prompt.set_tags(data['tags'])
        
        prompt.save()
        
        return jsonify(Result.success(data=prompt.to_dict(), message="提示词模板更新成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"更新提示词模板失败: {str(e)}")
        return jsonify(Result.error(message="更新提示词模板失败").to_dict())

@prompt_bp.route('/<int:prompt_id>', methods=['DELETE'])
@require_auth
def delete_prompt(current_user, prompt_id):
    """删除提示词模板"""
    try:
        prompt = PromptTemplate.get_by_id(prompt_id)
        if not prompt:
            return jsonify(Result.error(message="提示词模板不存在").to_dict())
        
        prompt.delete()
        
        return jsonify(Result.success(message="提示词模板删除成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"删除提示词模板失败: {str(e)}")
        return jsonify(Result.error(message="删除提示词模板失败").to_dict())

@prompt_bp.route('/search', methods=['GET'])
@require_auth
def search_prompt(current_user):
    """搜索提示词模板"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空").to_dict())
        
        prompt_list = PromptTemplate.search_by_keyword(keyword)
        
        return jsonify(Result.success(data=[prompt.to_dict() for prompt in prompt_list]).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"搜索提示词模板失败: {str(e)}")
        return jsonify(Result.error(message="搜索提示词模板失败").to_dict())

@prompt_bp.route('/categories', methods=['GET'])
@require_auth
def get_prompt_categories(current_user):
    """获取提示词模板分类列表"""
    try:
        # 获取所有不同的分类
        categories = PromptTemplate.query.with_entities(PromptTemplate.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify(Result.success(data=category_list).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取提示词模板分类失败: {str(e)}")
        return jsonify(Result.error(message="获取提示词模板分类失败").to_dict())

@prompt_bp.route('/popular', methods=['GET'])
@require_auth
def get_popular_prompt(current_user):
    """获取热门提示词模板"""
    try:
        limit = request.args.get('limit', 10, type=int)
        prompt_list = PromptTemplate.get_popular(limit)
        
        return jsonify(Result.success(data=[prompt.to_dict() for prompt in prompt_list]).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取热门提示词模板失败: {str(e)}")
        return jsonify(Result.error(message="获取热门提示词模板失败").to_dict())

@prompt_bp.route('/<int:prompt_id>/usage', methods=['POST'])
@require_auth
def record_prompt_usage(current_user, prompt_id):
    """记录提示词模板使用"""
    try:
        prompt = PromptTemplate.get_by_id(prompt_id)
        if not prompt:
            return jsonify(Result.error(message="提示词模板不存在").to_dict())
        
        # 增加使用次数
        prompt.increment_usage_count()
        
        return jsonify(Result.success(message="使用记录成功").to_dict())
        
    except Exception as e:
        current_app.logger.error(f"记录提示词模板使用失败: {str(e)}")
        return jsonify(Result.error(message="记录提示词模板使用失败").to_dict())

@prompt_bp.route('/types', methods=['GET'])
@require_auth
def get_prompt_types(current_user):
    """获取提示词模板类型列表"""
    try:
        types = ['system', 'user', 'assistant', 'general']
        return jsonify(Result.success(data=types).to_dict())
        
    except Exception as e:
        current_app.logger.error(f"获取提示词模板类型失败: {str(e)}")
        return jsonify(Result.error(message="获取提示词模板类型失败").to_dict())