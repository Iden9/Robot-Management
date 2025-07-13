from flask import request, jsonify, Blueprint
from app.models import EducationSettings, OperationLog
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_, and_
import datetime
import json

# 创建教育培训蓝图
education_bp = Blueprint('education', __name__)

@education_bp.route('/settings', methods=['GET'])
@require_auth
def get_education_settings(current_user):
    """获取教育培训设置列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        age_group = request.args.get('age_group')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = EducationSettings.query
        
        # 搜索过滤
        if search:
            query = query.filter(or_(
                EducationSettings.name.contains(search),
                EducationSettings.description.contains(search),
                EducationSettings.objectives.contains(search)
            ))
        
        # 分类过滤
        if category:
            query = query.filter_by(category=category)
        
        # 难度过滤
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        
        # 年龄组过滤
        if age_group:
            query = query.filter_by(target_age_group=age_group)
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 分页
        pagination = query.order_by(EducationSettings.updated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取教育培训设置列表成功",
            data={
                'settings': [setting.to_dict() for setting in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取教育培训设置列表失败: {str(e)}").to_dict())

@education_bp.route('/settings/<int:setting_id>', methods=['GET'])
@require_auth
def get_education_setting(current_user, setting_id):
    """获取单个教育培训设置信息"""
    try:
        setting = EducationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="教育培训设置不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取教育培训设置信息成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取教育培训设置信息失败: {str(e)}").to_dict())

@education_bp.route('/settings', methods=['POST'])
@require_role(['admin', 'operator'])
def create_education_setting(current_user):
    """创建教育培训设置"""
    try:
        data = request.get_json()
        
        # 数据验证 - 简化验证，不强制要求name
        equipment_id = data.get('equipment_id')
        if not equipment_id or equipment_id == 'default':
            # 如果没有指定设备ID或使用默认，尝试获取第一个可用设备
            from app.models.equipment import Equipment
            first_equipment = Equipment.query.first()
            if first_equipment:
                equipment_id = first_equipment.id
            else:
                return jsonify(Result.error(message="系统中没有可用设备，请先添加设备", code=400).to_dict())
        
        # 验证设备是否存在
        from app.models.equipment import Equipment
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message=f"设备{equipment_id}不存在", code=404).to_dict())
        
        # 检查是否已存在该设备的设置，如果存在则更新
        existing_setting = EducationSettings.query.filter_by(equipment_id=equipment_id).first()
        
        if existing_setting:
            # 更新现有设置
            existing_setting.screen_sync_mode = data.get('screen_sync_mode', existing_setting.screen_sync_mode)
            existing_setting.ai_platform = data.get('ai_platform', existing_setting.ai_platform)
            existing_setting.subject = data.get('subject', existing_setting.subject)
            existing_setting.voice_type = data.get('voice_type', existing_setting.voice_type)
            existing_setting.robot_action = data.get('robot_action', existing_setting.robot_action)
            existing_setting.hand_recognition = data.get('hand_recognition', existing_setting.hand_recognition)
            existing_setting.interactive_qa = data.get('interactive_qa', existing_setting.interactive_qa)
            existing_setting.navigation_mode = data.get('navigation_mode', existing_setting.navigation_mode)
            existing_setting.updated_by = current_user.id
            existing_setting.save()
            setting = existing_setting
        else:
            # 创建新设置
            setting = EducationSettings(
                equipment_id=equipment_id,
                screen_sync_mode=data.get('screen_sync_mode', 'auto'),
                ai_platform=data.get('ai_platform', 'xunfei'),
                subject=data.get('subject', '语文'),
                voice_type=data.get('voice_type', 'male'),
                robot_action=data.get('robot_action', 'standard'),
                hand_recognition=data.get('hand_recognition', True),
                interactive_qa=data.get('interactive_qa', True),
                navigation_mode=data.get('navigation_mode', 'default'),
                updated_by=current_user.id
            )
            setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        action_text = "更新教育培训设置" if existing_setting else "创建教育培训设置"
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"{action_text}: 设备{setting.equipment_id}",
            details=f"设置项: AI平台={setting.ai_platform}, 学科={setting.subject}, 语音={setting.voice_type}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育培训设置创建成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置创建失败: {str(e)}").to_dict())

@education_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_education_setting(current_user, setting_id):
    """更新教育培训设置"""
    try:
        setting = EducationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="教育培训设置不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = EducationSettings.get_by_name(data['name'])
            if existing and existing.id != setting.id:
                return jsonify(Result.error(message="教育培训设置名称已存在", code=400).to_dict())
            setting.name = data['name']
        
        # 更新基本字段
        basic_fields = ['description', 'category', 'target_age_group', 'difficulty_level', 
                       'duration', 'objectives', 'status', 'max_participants', 
                       'prerequisites', 'learning_outcomes']
        
        for field in basic_fields:
            if field in data:
                setattr(setting, field, data[field])
        
        # 更新JSON字段
        if 'content_structure' in data:
            setting.content_structure = json.dumps(data['content_structure']) if data['content_structure'] else None
        
        if 'assessment_criteria' in data:
            setting.assessment_criteria = json.dumps(data['assessment_criteria']) if data['assessment_criteria'] else None
        
        if 'interactive_elements' in data:
            setting.interactive_elements = json.dumps(data['interactive_elements']) if data['interactive_elements'] else None
        
        setting.updated_at = datetime.datetime.utcnow()
        setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"更新教育培训设置: 设备{setting.equipment_id}",
            details=f"设置项: AI平台={setting.ai_platform}, 学科={setting.subject}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育培训设置更新成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置更新失败: {str(e)}").to_dict())

@education_bp.route('/settings/<int:setting_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_education_setting(current_user, setting_id):
    """删除教育培训设置"""
    try:
        setting = EducationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="教育培训设置不存在", code=404).to_dict())
        
        equipment_id = setting.equipment_id
        setting.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"删除教育培训设置: 设备{setting.equipment_id}",
            details=f"删除设备{setting.equipment_id}的教育设置",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="教育培训设置删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置删除失败: {str(e)}").to_dict())

# 获取教育培训分类
@education_bp.route('/categories', methods=['GET'])
@require_auth
def get_education_categories(current_user):
    """获取教育培训分类统计"""
    try:
        # 获取所有分类及其数量
        category_stats = db.session.query(
            EducationSettings.category,
            db.func.count(EducationSettings.id).label('count')
        ).group_by(EducationSettings.category).all()
        
        categories = []
        for category, count in category_stats:
            categories.append({
                'category': category,
                'count': count
            })
        
        return jsonify(Result.success(
            message="获取教育培训分类成功",
            data=categories
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取教育培训分类失败: {str(e)}").to_dict())

# 获取年龄组统计
@education_bp.route('/age-groups', methods=['GET'])
@require_auth
def get_age_groups(current_user):
    """获取目标年龄组统计"""
    try:
        # 获取所有年龄组及其数量
        age_group_stats = db.session.query(
            EducationSettings.target_age_group,
            db.func.count(EducationSettings.id).label('count')
        ).group_by(EducationSettings.target_age_group).all()
        
        age_groups = []
        for age_group, count in age_group_stats:
            age_groups.append({
                'age_group': age_group,
                'count': count
            })
        
        return jsonify(Result.success(
            message="获取年龄组统计成功",
            data=age_groups
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取年龄组统计失败: {str(e)}").to_dict())

# 搜索教育培训设置
@education_bp.route('/search', methods=['GET'])
@require_auth
def search_education_settings(current_user):
    """搜索教育培训设置"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空", code=400).to_dict())
        
        settings = EducationSettings.query.filter(or_(
            EducationSettings.name.contains(keyword),
            EducationSettings.description.contains(keyword),
            EducationSettings.objectives.contains(keyword),
            EducationSettings.category.contains(keyword)
        )).all()
        
        return jsonify(Result.success(
            message="搜索教育培训设置成功",
            data=[setting.to_dict() for setting in settings]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"搜索教育培训设置失败: {str(e)}").to_dict())

# 复制教育培训设置
@education_bp.route('/settings/<int:setting_id>/copy', methods=['POST'])
@require_role(['admin', 'operator'])
def copy_education_setting(current_user, setting_id):
    """复制教育培训设置"""
    try:
        original_setting = EducationSettings.get_by_id(setting_id)
        if not original_setting:
            return jsonify(Result.error(message="原教育培训设置不存在", code=404).to_dict())
        
        data = request.get_json()
        new_name = data.get('name', f"{original_setting.name} (副本)")
        
        # 检查新名称是否已存在
        if EducationSettings.get_by_name(new_name):
            return jsonify(Result.error(message="教育培训设置名称已存在", code=400).to_dict())
        
        # 创建副本
        new_setting = EducationSettings(
            name=new_name,
            description=original_setting.description,
            category=original_setting.category,
            target_age_group=original_setting.target_age_group,
            difficulty_level=original_setting.difficulty_level,
            duration=original_setting.duration,
            objectives=original_setting.objectives,
            content_structure=original_setting.content_structure,
            assessment_criteria=original_setting.assessment_criteria,
            interactive_elements=original_setting.interactive_elements,
            status='inactive',  # 副本默认为非激活状态
            max_participants=original_setting.max_participants,
            prerequisites=original_setting.prerequisites,
            learning_outcomes=original_setting.learning_outcomes,
            created_by=current_user.id
        )
        new_setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"复制教育培训设置: 设备{original_setting.equipment_id}",
            details=f"复制教育设置到新设备",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育培训设置复制成功",
            data=new_setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置复制失败: {str(e)}").to_dict())

# 批量操作
@education_bp.route('/settings/batch-operation', methods=['POST'])
@require_role(['admin', 'operator'])
def batch_education_settings_operation(current_user):
    """批量教育培训设置操作"""
    try:
        data = request.get_json()
        setting_ids = data.get('setting_ids', [])
        operation = data.get('operation')
        
        if not setting_ids or not operation:
            return jsonify(Result.error(message="设置ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for setting_id in setting_ids:
            try:
                setting = EducationSettings.get_by_id(setting_id)
                if not setting:
                    results.append({"setting_id": setting_id, "status": "failed", "message": "教育培训设置不存在"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    setting.delete()
                elif operation == 'activate':
                    setting.status = 'active'
                    setting.save()
                elif operation == 'deactivate':
                    setting.status = 'inactive'
                    setting.save()
                elif operation == 'change_category':
                    new_category = data.get('category')
                    if new_category:
                        setting.category = new_category
                        setting.save()
                    else:
                        results.append({"setting_id": setting_id, "status": "failed", "message": "未提供新分类"})
                        failed_count += 1
                        continue
                else:
                    results.append({"setting_id": setting_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"setting_id": setting_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"setting_id": setting_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"批量教育培训设置操作: {operation}",
            details=f"成功: {success_count}, 失败: {failed_count}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"批量操作完成，成功: {success_count}, 失败: {failed_count}",
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"批量操作失败: {str(e)}").to_dict())

# 教育培训统计
@education_bp.route('/statistics', methods=['GET'])
@require_auth
def get_education_statistics(current_user):
    """获取教育培训统计信息"""
    try:
        # 基本统计
        total_settings = EducationSettings.query.count()
        active_settings = EducationSettings.query.filter_by(status='active').count()
        inactive_settings = EducationSettings.query.filter_by(status='inactive').count()
        
        # 按分类统计
        category_stats = db.session.query(
            EducationSettings.category,
            db.func.count(EducationSettings.id)
        ).group_by(EducationSettings.category).all()
        
        # 按难度级别统计
        difficulty_stats = db.session.query(
            EducationSettings.difficulty_level,
            db.func.count(EducationSettings.id)
        ).group_by(EducationSettings.difficulty_level).all()
        
        # 按年龄组统计
        age_group_stats = db.session.query(
            EducationSettings.target_age_group,
            db.func.count(EducationSettings.id)
        ).group_by(EducationSettings.target_age_group).all()
        
        # 平均时长
        avg_duration = db.session.query(db.func.avg(EducationSettings.duration)).scalar() or 0
        
        # 最近创建的设置
        recent_settings = EducationSettings.query.order_by(
            EducationSettings.updated_at.desc()
        ).limit(5).all()
        
        return jsonify(Result.success(
            message="获取教育培训统计成功",
            data={
                "total_settings": total_settings,
                "active_settings": active_settings,
                "inactive_settings": inactive_settings,
                "category_distribution": dict(category_stats),
                "difficulty_distribution": dict(difficulty_stats),
                "age_group_distribution": dict(age_group_stats),
                "average_duration": round(avg_duration, 2),
                "recent_settings": [setting.to_dict() for setting in recent_settings]
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取教育培训统计失败: {str(e)}").to_dict())

# 导出教育培训设置
@education_bp.route('/settings/<int:setting_id>/export', methods=['GET'])
@require_auth
def export_education_setting(current_user, setting_id):
    """导出教育培训设置配置"""
    try:
        setting = EducationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="教育培训设置不存在", code=404).to_dict())
        
        # 准备导出数据
        export_data = setting.to_dict()
        export_data['export_time'] = datetime.datetime.utcnow().isoformat()
        export_data['exported_by'] = current_user.username
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"导出教育培训设置: 设备{setting.equipment_id}",
            details=f"导出设备{setting.equipment_id}的教育设置",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育培训设置导出成功",
            data=export_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置导出失败: {str(e)}").to_dict())

# 导入教育培训设置
@education_bp.route('/settings/import', methods=['POST'])
@require_role(['admin', 'operator'])
def import_education_setting(current_user):
    """导入教育培训设置配置"""
    try:
        data = request.get_json()
        import_data = data.get('setting_data')
        
        if not import_data:
            return jsonify(Result.error(message="请提供导入数据", code=400).to_dict())
        
        # 验证必需字段
        required_fields = ['name', 'category', 'target_age_group', 'difficulty_level']
        for field in required_fields:
            if not import_data.get(field):
                return jsonify(Result.error(message=f"导入数据缺少必需字段: {field}", code=400).to_dict())
        
        # 检查名称是否已存在，如果存在则添加后缀
        original_name = import_data['name']
        new_name = original_name
        counter = 1
        while EducationSettings.get_by_name(new_name):
            new_name = f"{original_name} (导入{counter})"
            counter += 1
        
        # 创建新设置
        setting = EducationSettings(
            name=new_name,
            description=import_data.get('description'),
            category=import_data['category'],
            target_age_group=import_data['target_age_group'],
            difficulty_level=import_data['difficulty_level'],
            duration=import_data.get('duration', 30),
            objectives=import_data.get('objectives'),
            content_structure=import_data.get('content_structure'),
            assessment_criteria=import_data.get('assessment_criteria'),
            interactive_elements=import_data.get('interactive_elements'),
            status='inactive',  # 导入的设置默认为非激活状态
            max_participants=import_data.get('max_participants', 20),
            prerequisites=import_data.get('prerequisites'),
            learning_outcomes=import_data.get('learning_outcomes'),
            created_by=current_user.id
        )
        setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"导入教育培训设置: 设备{setting.equipment_id}",
            details=f"导入教育设置到设备{setting.equipment_id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育培训设置导入成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育培训设置导入失败: {str(e)}").to_dict())