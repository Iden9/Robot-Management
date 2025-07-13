from flask import request, jsonify, Blueprint
from app.models import Equipment, EducationSettings, NavigationSettings, NavigationPoint, OperationLog
from app.models.result import Result
from app.auth import require_auth, require_role

# 创建设置蓝图
settings_bp = Blueprint('settings', __name__)

# ==================== 教育设置 ====================

@settings_bp.route('/education/<equipment_id>', methods=['GET'])
@require_auth
def get_education_settings(current_user, equipment_id):
    """获取设备教育设置"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        settings = EducationSettings.get_by_equipment(equipment_id)
        if not settings:
            return jsonify(Result.error(message="教育设置不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取教育设置成功",
            data=settings.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取教育设置失败: {str(e)}").to_dict())

@settings_bp.route('/education/<equipment_id>', methods=['POST', 'PUT'])
@require_role(['admin', 'operator'])
def update_education_settings(current_user, equipment_id):
    """更新设备教育设置"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供设置数据", code=400).to_dict())
        
        # 添加更新者信息
        data['updated_by'] = current_user.id
        
        settings = EducationSettings.create_or_update(equipment_id, **data)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_settings_change(
            user_id=current_user.id,
            settings_type="教育设置",
            equipment_id=equipment_id,
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="教育设置更新成功",
            data=settings.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"教育设置更新失败: {str(e)}").to_dict())

# ==================== 导览设置 ====================

@settings_bp.route('/navigation/<equipment_id>', methods=['GET'])
@require_auth
def get_navigation_settings(current_user, equipment_id):
    """获取设备导览设置"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        settings = NavigationSettings.get_by_equipment(equipment_id)
        if not settings:
            return jsonify(Result.error(message="导览设置不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取导览设置成功",
            data=settings.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览设置失败: {str(e)}").to_dict())

@settings_bp.route('/navigation/<equipment_id>', methods=['POST', 'PUT'])
@require_role(['admin', 'operator'])
def update_navigation_settings(current_user, equipment_id):
    """更新设备导览设置"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供设置数据", code=400).to_dict())
        
        # 添加更新者信息
        data['updated_by'] = current_user.id
        
        settings = NavigationSettings.create_or_update(equipment_id, **data)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_settings_change(
            user_id=current_user.id,
            settings_type="导览设置",
            equipment_id=equipment_id,
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览设置更新成功",
            data=settings.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览设置更新失败: {str(e)}").to_dict())

# ==================== 导览点位 ====================

@settings_bp.route('/navigation/<equipment_id>/points', methods=['GET'])
@require_auth
def get_navigation_points(current_user, equipment_id):
    """获取设备导览点位"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        if enabled_only:
            points = NavigationPoint.get_enabled_by_equipment(equipment_id)
        else:
            points = NavigationPoint.get_by_equipment(equipment_id)
        
        return jsonify(Result.success(
            message="获取导览点位成功",
            data=[point.to_dict() for point in points]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取导览点位失败: {str(e)}").to_dict())

@settings_bp.route('/navigation/<equipment_id>/points', methods=['POST'])
@require_role(['admin', 'operator'])
def create_navigation_point(current_user, equipment_id):
    """创建导览点位"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        
        # 数据验证
        required_fields = ['name', 'x_position', 'y_position']
        for field in required_fields:
            if not data or field not in data:
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查点位名称是否已存在
        if NavigationPoint.get_by_name(equipment_id, data['name']):
            return jsonify(Result.error(message="点位名称已存在", code=400).to_dict())
        
        point = NavigationPoint(
            equipment_id=equipment_id,
            name=data['name'],
            description=data.get('description'),
            x_position=data['x_position'],
            y_position=data['y_position'],
            rotation=data.get('rotation', 0),
            enabled=data.get('enabled', True)
        )
        point.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"创建导览点位: {point.name}",
            details=f"设备ID: {equipment_id}, 点位ID: {point.id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览点位创建成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位创建失败: {str(e)}").to_dict())

@settings_bp.route('/navigation/points/<int:point_id>', methods=['PUT'])
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
        if 'name' in data:
            # 检查新名称是否已存在
            existing = NavigationPoint.get_by_name(point.equipment_id, data['name'])
            if existing and existing.id != point.id:
                return jsonify(Result.error(message="点位名称已存在", code=400).to_dict())
            point.name = data['name']
        
        if 'description' in data:
            point.description = data['description']
        if 'x_position' in data:
            point.x_position = data['x_position']
        if 'y_position' in data:
            point.y_position = data['y_position']
        if 'rotation' in data:
            point.rotation = data['rotation']
        if 'enabled' in data:
            point.enabled = data['enabled']
        
        point.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"更新导览点位: {point.name}",
            details=f"设备ID: {point.equipment_id}, 点位ID: {point.id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="导览点位更新成功",
            data=point.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位更新失败: {str(e)}").to_dict())

@settings_bp.route('/navigation/points/<int:point_id>', methods=['DELETE'])
@require_role(['admin', 'operator'])
def delete_navigation_point(current_user, point_id):
    """删除导览点位"""
    try:
        point = NavigationPoint.get_by_id(point_id)
        if not point:
            return jsonify(Result.error(message="导览点位不存在", code=404).to_dict())
        
        name = point.name
        equipment_id = point.equipment_id
        point.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"删除导览点位: {name}",
            details=f"设备ID: {equipment_id}, 点位ID: {point_id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="导览点位删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"导览点位删除失败: {str(e)}").to_dict())
