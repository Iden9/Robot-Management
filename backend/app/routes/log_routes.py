from flask import request, jsonify, Blueprint
from app.models import OperationLog, EquipmentLog
from app.models.result import Result
from app.auth import require_auth, require_role
from datetime import datetime, timedelta

# 创建日志蓝图
log_bp = Blueprint('logs', __name__)

@log_bp.route('/operations', methods=['GET'])
@require_auth
def get_operation_logs(current_user):
    """获取操作日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = OperationLog.query
        
        # 用户过滤
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # 操作类型过滤
        if action:
            query = query.filter(OperationLog.action.contains(action))
        
        # 日期范围过滤
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(OperationLog.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(OperationLog.created_at < end_dt)
        
        # 分页
        pagination = query.order_by(OperationLog.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取操作日志成功",
            data={
                'logs': [log.to_dict() for log in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取操作日志失败: {str(e)}").to_dict())

@log_bp.route('/operations/search', methods=['GET'])
@require_auth
def search_operation_logs(current_user):
    """搜索操作日志"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify(Result.error(message="搜索关键词不能为空", code=400).to_dict())
        
        logs = OperationLog.search_logs(keyword)
        
        return jsonify(Result.success(
            message="搜索操作日志成功",
            data=[log.to_dict() for log in logs[:100]]  # 限制返回100条
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"搜索操作日志失败: {str(e)}").to_dict())

@log_bp.route('/equipment', methods=['GET'])
@require_auth
def get_equipment_logs(current_user):
    """获取设备日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        equipment_id = request.args.get('equipment_id')
        log_type = request.args.get('log_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = EquipmentLog.query
        
        # 设备过滤
        if equipment_id:
            query = query.filter_by(equipment_id=equipment_id)
        
        # 日志类型过滤
        if log_type:
            query = query.filter_by(log_type=log_type)
        
        # 日期范围过滤
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(EquipmentLog.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(EquipmentLog.created_at < end_dt)
        
        # 分页
        pagination = query.order_by(EquipmentLog.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取设备日志成功",
            data={
                'logs': [log.to_dict() for log in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取设备日志失败: {str(e)}").to_dict())

@log_bp.route('/equipment/errors', methods=['GET'])
@require_auth
def get_error_logs(current_user):
    """获取错误日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = EquipmentLog.query.filter_by(log_type='error')
        
        # 分页
        pagination = query.order_by(EquipmentLog.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取错误日志成功",
            data={
                'logs': [log.to_dict() for log in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取错误日志失败: {str(e)}").to_dict())

@log_bp.route('/equipment/statistics', methods=['GET'])
@require_auth
def get_log_statistics(current_user):
    """获取日志统计"""
    try:
        from sqlalchemy import func
        from app import db
        
        # 按日志类型统计
        type_stats = db.session.query(
            EquipmentLog.log_type,
            func.count(EquipmentLog.id).label('count')
        ).group_by(EquipmentLog.log_type).all()
        
        # 按设备统计
        equipment_stats = db.session.query(
            EquipmentLog.equipment_id,
            func.count(EquipmentLog.id).label('count')
        ).group_by(EquipmentLog.equipment_id).order_by(func.count(EquipmentLog.id).desc()).limit(10).all()
        
        # 最近7天的日志数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(EquipmentLog.created_at).label('date'),
            func.count(EquipmentLog.id).label('count')
        ).filter(
            EquipmentLog.created_at >= seven_days_ago
        ).group_by(func.date(EquipmentLog.created_at)).all()
        
        statistics = {
            'by_type': [{'type': row[0], 'count': row[1]} for row in type_stats],
            'by_equipment': [{'equipment_id': row[0], 'count': row[1]} for row in equipment_stats],
            'daily': [{'date': row[0].isoformat(), 'count': row[1]} for row in daily_stats]
        }
        
        return jsonify(Result.success(
            message="获取日志统计成功",
            data=statistics
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取日志统计失败: {str(e)}").to_dict())

@log_bp.route('/operations/<int:log_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_operation_log(current_user, log_id):
    """删除操作日志"""
    try:
        log = OperationLog.get_by_id(log_id)
        if not log:
            return jsonify(Result.error(message="操作日志不存在", code=404).to_dict())
        
        log.delete()
        
        return jsonify(Result.success(message="操作日志删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"操作日志删除失败: {str(e)}").to_dict())

@log_bp.route('/equipment/<int:log_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_equipment_log(current_user, log_id):
    """删除设备日志"""
    try:
        log = EquipmentLog.get_by_id(log_id)
        if not log:
            return jsonify(Result.error(message="设备日志不存在", code=404).to_dict())
        
        log.delete()
        
        return jsonify(Result.success(message="设备日志删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备日志删除失败: {str(e)}").to_dict())

@log_bp.route('/cleanup', methods=['POST'])
@require_role(['admin'])
def cleanup_logs(current_user):
    """清理旧日志"""
    try:
        data = request.get_json()
        days = data.get('days', 30)  # 默认清理30天前的日志
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 删除旧的操作日志
        old_operation_logs = OperationLog.query.filter(OperationLog.created_at < cutoff_date)
        operation_count = old_operation_logs.count()
        old_operation_logs.delete()
        
        # 删除旧的设备日志
        old_equipment_logs = EquipmentLog.query.filter(EquipmentLog.created_at < cutoff_date)
        equipment_count = old_equipment_logs.count()
        old_equipment_logs.delete()
        
        from app import db
        db.session.commit()
        
        # 记录清理操作
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="清理日志",
            details=f"清理了{days}天前的日志，操作日志: {operation_count}条，设备日志: {equipment_count}条",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="日志清理成功",
            data={
                'operation_logs_deleted': operation_count,
                'equipment_logs_deleted': equipment_count
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"日志清理失败: {str(e)}").to_dict())
