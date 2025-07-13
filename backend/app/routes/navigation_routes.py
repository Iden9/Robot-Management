from flask import request, jsonify, Blueprint
from app.models import NavigationSettings, NavigationPoint, OperationLog
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_, and_
import datetime

# 创建导览蓝图
navigation_bp = Blueprint('navigation', __name__)

# 导览设置管理
@navigation_bp.route('/settings', methods=['GET'])
@require_auth
def get_navigation_settings(current_user):
    """获取导览设置列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = NavigationSettings.query
        
        # 搜索过滤
        if search:
            query = query.filter(or_(
                NavigationSettings.name.contains(search),
                NavigationSettings.description.contains(search)
            ))
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 分页
        pagination = query.order_by(NavigationSettings.updated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 获取详细信息
        settings_data = []
        for setting in pagination.items:
            setting_dict = setting.to_dict()
            # 获取该设置下的导览点位数量
            point_count = NavigationPoint.query.filter_by(equipment_id=setting.equipment_id).count()
            setting_dict['point_count'] = point_count
            settings_data.append(setting_dict)
        
        return jsonify(Result.success(
            message="获取导览设置列表成功",
            data={
                'settings': settings_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览设置列表失败: {str(e)}").to_dict())

@navigation_bp.route('/settings/<int:setting_id>', methods=['GET'])
@require_auth
def get_navigation_setting(current_user, setting_id):
    """获取单个导览设置信息"""
    try:
        setting = NavigationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="导览设置不存在", code=404).to_dict())
        
        setting_dict = setting.to_dict()
        # 获取导览点位信息
        points = NavigationPoint.query.filter_by(equipment_id=setting.equipment_id).order_by(NavigationPoint.id).all()
        setting_dict['points'] = [point.to_dict() for point in points]
        
        return jsonify(Result.success(
            message="获取导览设置信息成功",
            data=setting_dict
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览设置信息失败: {str(e)}").to_dict())

@navigation_bp.route('/settings', methods=['POST'])
@require_role(['admin', 'operator'])
def create_navigation_setting(current_user):
    """创建导览设置"""
    try:
        data = request.get_json()
        
        # 数据验证 - 简化验证，不强制要求start_point
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
        existing_setting = NavigationSettings.query.filter_by(equipment_id=equipment_id).first()
        
        if existing_setting:
            # 更新现有设置
            existing_setting.scene_type = data.get('scene', existing_setting.scene_type)
            existing_setting.ai_platform = data.get('ai_platform', existing_setting.ai_platform)
            existing_setting.voice_type = data.get('voice_type', existing_setting.voice_type)
            existing_setting.scene_prompt = data.get('scene_prompt', existing_setting.scene_prompt)
            existing_setting.object_recognition = data.get('object_recognition', existing_setting.object_recognition)
            existing_setting.recognition_action = data.get('recognition_action', existing_setting.recognition_action)
            existing_setting.auto_follow = data.get('auto_follow', existing_setting.auto_follow)
            existing_setting.patrol_mode = data.get('patrol_mode', existing_setting.patrol_mode)
            existing_setting.navigation_mode = data.get('navigation_mode', existing_setting.navigation_mode)
            existing_setting.emergency_alert = data.get('emergency_alert', existing_setting.emergency_alert)
            existing_setting.alert_mode = data.get('alert_mode', existing_setting.alert_mode)
            existing_setting.robot_speed = data.get('robot_speed', existing_setting.robot_speed)
            existing_setting.updated_by = current_user.id
            existing_setting.save()
            setting = existing_setting
        else:
            # 创建新设置
            setting = NavigationSettings(
                equipment_id=equipment_id,
                scene_type=data.get('scene', 'scenic'),
                ai_platform=data.get('ai_platform', 'xunfei'),
                voice_type=data.get('voice_type', 'male'),
                scene_prompt=data.get('scene_prompt', ''),
                object_recognition=data.get('object_recognition', True),
                recognition_action=data.get('recognition_action', 'move'),
                auto_follow=data.get('auto_follow', False),
                patrol_mode=data.get('patrol_mode', 'standard'),
                navigation_mode=data.get('navigation_mode', 'dynamic'),
                emergency_alert=data.get('emergency_alert', True),
                alert_mode=data.get('alert_mode', 'auto'),
                robot_speed=data.get('robot_speed', 50),
                updated_by=current_user.id
            )
            setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        action_text = "更新导览设置" if existing_setting else "创建导览设置"
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"{action_text}: 设备{setting.equipment_id}",
            details=f"设置项: 场景={setting.scene_type}, AI平台={setting.ai_platform}, 语音={setting.voice_type}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览设置创建成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览设置创建失败: {str(e)}").to_dict())

@navigation_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_navigation_setting(current_user, setting_id):
    """更新导览设置"""
    try:
        setting = NavigationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="导览设置不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'name' in data:
            # 检查新名称是否已存在
            existing = NavigationSettings.get_by_name(data['name'])
            if existing and existing.id != setting.id:
                return jsonify(Result.error(message="导览设置名称已存在", code=400).to_dict())
            setting.name = data['name']
        
        if 'description' in data:
            setting.description = data['description']
        
        if 'start_point' in data:
            setting.start_point = data['start_point']
        
        if 'end_point' in data:
            setting.end_point = data['end_point']
        
        if 'total_duration' in data:
            setting.total_duration = data['total_duration']
        
        if 'status' in data:
            setting.status = data['status']
        
        if 'max_participants' in data:
            setting.max_participants = data['max_participants']
        
        if 'difficulty_level' in data:
            setting.difficulty_level = data['difficulty_level']
        
        if 'route_type' in data:
            setting.route_type = data['route_type']
        
        setting.updated_at = datetime.datetime.utcnow()
        setting.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='update',
            action=f"更新导览设置: {setting.name}",
            target_type='navigation_setting',
            target_id=str(setting.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览设置更新成功",
            data=setting.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览设置更新失败: {str(e)}").to_dict())

@navigation_bp.route('/settings/<int:setting_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_navigation_setting(current_user, setting_id):
    """删除导览设置"""
    try:
        setting = NavigationSettings.get_by_id(setting_id)
        if not setting:
            return jsonify(Result.error(message="导览设置不存在", code=404).to_dict())
        
        # 检查是否有关联的导览点位
        point_count = NavigationPoint.query.filter_by(navigation_setting_id=setting_id).count()
        if point_count > 0:
            return jsonify(Result.error(message=f"该导览设置下还有 {point_count} 个导览点位，不能删除", code=400).to_dict())
        
        setting_name = setting.name
        setting.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='delete',
            action=f"删除导览设置: {setting_name}",
            target_type='navigation_setting',
            target_id=str(setting_id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="导览设置删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览设置删除失败: {str(e)}").to_dict())

# 导览点位管理
@navigation_bp.route('/points', methods=['GET'])
@require_auth
def get_navigation_points(current_user):
    """获取导览点位列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        setting_id = request.args.get('setting_id', type=int)
        point_type = request.args.get('point_type')
        search = request.args.get('search', '').strip()
        
        query = NavigationPoint.query
        
        # 导览设置过滤
        if setting_id:
            query = query.filter_by(navigation_setting_id=setting_id)
        
        # 点位类型过滤
        if point_type:
            query = query.filter_by(point_type=point_type)
        
        # 搜索过滤
        if search:
            query = query.filter(or_(
                NavigationPoint.name.contains(search),
                NavigationPoint.description.contains(search)
            ))
        
        # 分页
        pagination = query.order_by(NavigationPoint.id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取导览点位列表成功",
            data={
                'points': [point.to_dict() for point in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览点位列表失败: {str(e)}").to_dict())

@navigation_bp.route('/points/<int:point_id>', methods=['GET'])
@require_auth
def get_navigation_point(current_user, point_id):
    """获取单个导览点位信息"""
    try:
        point = NavigationPoint.get_by_id(point_id)
        if not point:
            return jsonify(Result.error(message="导览点位不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取导览点位信息成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览点位信息失败: {str(e)}").to_dict())

@navigation_bp.route('/points', methods=['POST'])
@require_role(['admin', 'operator'])
def create_navigation_point(current_user):
    """创建导览点位"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['navigation_setting_id', 'name', 'x_coordinate', 'y_coordinate']
        for field in required_fields:
            if not data or data.get(field) is None:
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 验证导览设置是否存在
        setting = NavigationSettings.get_by_id(data['navigation_setting_id'])
        if not setting:
            return jsonify(Result.error(message="导览设置不存在", code=400).to_dict())
        
        # 获取下一个排序序号
        max_order = db.session.query(db.func.max(NavigationPoint.order_index)).filter_by(
            navigation_setting_id=data['navigation_setting_id']
        ).scalar() or 0
        
        # 创建新导览点位
        point = NavigationPoint(
            navigation_setting_id=data['navigation_setting_id'],
            name=data['name'],
            description=data.get('description'),
            x_coordinate=data['x_coordinate'],
            y_coordinate=data['y_coordinate'],
            z_coordinate=data.get('z_coordinate', 0),
            point_type=data.get('point_type', 'waypoint'),
            duration=data.get('duration', 60),
            order_index=max_order + 1,
            is_mandatory=data.get('is_mandatory', True),
            interaction_content=data.get('interaction_content'),
            voice_content=data.get('voice_content'),
            created_by=current_user.id
        )
        point.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='create',
            action=f"创建导览点位: {point.name}",
            target_type='navigation_point',
            target_id=str(point.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览点位创建成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位创建失败: {str(e)}").to_dict())

@navigation_bp.route('/points/<int:point_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_navigation_point(current_user, point_id):
    """更新导览点位"""
    try:
        point = NavigationPoint.get_by_id(point_id)
        if not point:
            return jsonify(Result.error(message="导览点位不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        updatable_fields = ['name', 'description', 'x_coordinate', 'y_coordinate', 'z_coordinate',
                           'point_type', 'duration', 'is_mandatory', 'interaction_content', 'voice_content']
        
        for field in updatable_fields:
            if field in data:
                setattr(point, field, data[field])
        
        point.updated_at = datetime.datetime.utcnow()
        point.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='update',
            action=f"更新导览点位: {point.name}",
            target_type='navigation_point',
            target_id=str(point.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览点位更新成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位更新失败: {str(e)}").to_dict())

@navigation_bp.route('/points/<int:point_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_navigation_point(current_user, point_id):
    """删除导览点位"""
    try:
        point = NavigationPoint.get_by_id(point_id)
        if not point:
            return jsonify(Result.error(message="导览点位不存在", code=404).to_dict())
        
        point_name = point.name
        navigation_setting_id = point.navigation_setting_id
        order_index = point.order_index
        
        point.delete()
        
        # 重新排序其他点位
        NavigationPoint.query.filter(
            NavigationPoint.navigation_setting_id == navigation_setting_id,
            NavigationPoint.order_index > order_index
        ).update({'order_index': NavigationPoint.order_index - 1})
        db.session.commit()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='delete',
            action=f"删除导览点位: {point_name}",
            target_type='navigation_point',
            target_id=str(point_id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="导览点位删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位删除失败: {str(e)}").to_dict())

# 点位排序
@navigation_bp.route('/points/<int:point_id>/move', methods=['POST'])
@require_role(['admin', 'operator'])
def move_navigation_point(current_user, point_id):
    """移动导览点位顺序"""
    try:
        point = NavigationPoint.get_by_id(point_id)
        if not point:
            return jsonify(Result.error(message="导览点位不存在", code=404).to_dict())
        
        data = request.get_json()
        new_order = data.get('new_order')
        direction = data.get('direction')  # 'up' or 'down'
        
        current_order = point.order_index
        navigation_setting_id = point.navigation_setting_id
        
        if new_order is not None:
            # 指定新位置
            if new_order != current_order:
                if new_order > current_order:
                    # 向后移动
                    NavigationPoint.query.filter(
                        NavigationPoint.navigation_setting_id == navigation_setting_id,
                        NavigationPoint.order_index > current_order,
                        NavigationPoint.order_index <= new_order
                    ).update({'order_index': NavigationPoint.order_index - 1})
                else:
                    # 向前移动
                    NavigationPoint.query.filter(
                        NavigationPoint.navigation_setting_id == navigation_setting_id,
                        NavigationPoint.order_index >= new_order,
                        NavigationPoint.order_index < current_order
                    ).update({'order_index': NavigationPoint.order_index + 1})
                
                point.order_index = new_order
        
        elif direction == 'up' and current_order > 1:
            # 向上移动
            prev_point = NavigationPoint.query.filter_by(
                navigation_setting_id=navigation_setting_id,
                order_index=current_order - 1
            ).first()
            if prev_point:
                prev_point.order_index = current_order
                point.order_index = current_order - 1
                prev_point.save()
        
        elif direction == 'down':
            # 向下移动
            next_point = NavigationPoint.query.filter_by(
                navigation_setting_id=navigation_setting_id,
                order_index=current_order + 1
            ).first()
            if next_point:
                next_point.order_index = current_order
                point.order_index = current_order + 1
                next_point.save()
        
        point.save()
        db.session.commit()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='update',
            action=f"移动导览点位顺序: {point.name}",
            target_type='navigation_point',
            target_id=str(point.id),
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="点位顺序调整成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"点位顺序调整失败: {str(e)}").to_dict())

# 批量操作
@navigation_bp.route('/settings/batch-operation', methods=['POST'])
@require_role(['admin', 'operator'])
def batch_navigation_settings_operation(current_user):
    """批量导览设置操作"""
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
                setting = NavigationSettings.get_by_id(setting_id)
                if not setting:
                    results.append({"setting_id": setting_id, "status": "failed", "message": "导览设置不存在"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    # 检查是否有关联的导览点位
                    point_count = NavigationPoint.query.filter_by(navigation_setting_id=setting_id).count()
                    if point_count > 0:
                        results.append({"setting_id": setting_id, "status": "failed", "message": "存在关联的导览点位"})
                        failed_count += 1
                        continue
                    setting.delete()
                elif operation == 'activate':
                    setting.status = 'active'
                    setting.save()
                elif operation == 'deactivate':
                    setting.status = 'inactive'
                    setting.save()
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
            action_type='config',
            action=f"批量导览设置操作: {operation}",
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

# 导览统计
@navigation_bp.route('/statistics', methods=['GET'])
@require_auth
def get_navigation_statistics(current_user):
    """获取导览统计信息"""
    try:
        # 导览设置统计
        total_settings = NavigationSettings.query.count()
        # NavigationSettings模型没有status字段，使用其他统计
        ai_xunfei_count = NavigationSettings.query.filter_by(ai_platform='xunfei').count()
        ai_baidu_count = NavigationSettings.query.filter_by(ai_platform='baidu').count()
        
        # 导览点位统计
        from app.models.navigation_point import NavigationPoint
        total_points = NavigationPoint.query.count()
        
        # 按场景类型统计
        scene_type_stats = db.session.query(
            NavigationSettings.scene_type, 
            db.func.count(NavigationSettings.id)
        ).group_by(NavigationSettings.scene_type).all()
        
        # 按巡逻模式统计
        patrol_mode_stats = db.session.query(
            NavigationSettings.patrol_mode, 
            db.func.count(NavigationSettings.id)
        ).group_by(NavigationSettings.patrol_mode).all()
        
        # 最近更新的导览设置
        recent_settings = NavigationSettings.query.order_by(
            NavigationSettings.updated_at.desc()
        ).limit(5).all()
        
        return jsonify(Result.success(
            message="获取导览统计成功",
            data={
                "total_settings": total_settings,
                "ai_xunfei_count": ai_xunfei_count,
                "ai_baidu_count": ai_baidu_count,
                "total_points": total_points,
                "scene_type_distribution": dict(scene_type_stats),
                "patrol_mode_distribution": dict(patrol_mode_stats),
                "recent_settings": [setting.to_dict() for setting in recent_settings]
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览统计失败: {str(e)}").to_dict())