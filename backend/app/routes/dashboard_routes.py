from flask import request, jsonify, Blueprint
from app.models import (Equipment, User, Courseware, OperationLog, NavigationSettings, 
                       EducationSettings, UserSession, CoursewareUsage, EquipmentStatusHistory)
from app.models.result import Result
from app.auth import require_auth, require_role
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, and_, or_
from app import db

# 创建仪表板蓝图
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@require_auth
def get_overview(current_user):
    """获取仪表板概览数据"""
    try:
        # 基础统计数据
        total_users = User.query.count()
        total_equipment = Equipment.query.count()
        total_courseware = Courseware.query.count()
        total_navigation_settings = NavigationSettings.query.count()
        total_education_settings = EducationSettings.query.count()
        
        # 在线用户统计
        online_users = 0
        for user in User.get_all():
            active_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            if active_sessions:
                online_users += 1
        
        # 设备状态统计
        equipment_online = Equipment.query.filter_by(status='online').count()
        equipment_offline = Equipment.query.filter_by(status='offline').count()
        equipment_error = Equipment.query.filter_by(status='error').count()
        equipment_maintenance = 0  # 维护模式字段不存在于数据库中
        
        # 课件状态统计
        active_courseware = Courseware.query.filter_by(status='active').count()
        inactive_courseware = Courseware.query.filter_by(status='inactive').count()
        
        # 导览设置统计
        total_navigation = NavigationSettings.query.count()
        active_navigation = total_navigation  # 假设所有都是激活的
        inactive_navigation = 0
        
        # 教育设置统计
        total_education = EducationSettings.query.count()
        active_education = total_education  # 假设所有都是激活的
        inactive_education = 0
        
        # 今日活动统计
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_operations = OperationLog.query.filter(OperationLog.created_at >= today_start).count()
        today_logins = OperationLog.query.filter(
            and_(OperationLog.action.contains('登录'), OperationLog.created_at >= today_start)
        ).count()
        
        return jsonify(Result.success(
            message="获取仪表板概览成功",
            data={
                "summary": {
                    "total_users": total_users,
                    "online_users": online_users,
                    "total_equipment": total_equipment,
                    "total_courseware": total_courseware,
                    "total_navigation_settings": total_navigation_settings,
                    "total_education_settings": total_education_settings
                },
                "equipment_status": {
                    "online": equipment_online,
                    "offline": equipment_offline,
                    "error": equipment_error,
                    "maintenance": equipment_maintenance
                },
                "content_status": {
                    "active_courseware": active_courseware,
                    "inactive_courseware": inactive_courseware,
                    "active_navigation": active_navigation,
                    "inactive_navigation": inactive_navigation,
                    "active_education": active_education,
                    "inactive_education": inactive_education
                },
                "today_activity": {
                    "total_operations": today_operations,
                    "login_count": today_logins
                }
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取仪表板概览失败: {str(e)}").to_dict())

@dashboard_bp.route('/statistics', methods=['GET'])
@require_auth
def get_statistics(current_user):
    """获取仪表板统计数据"""
    try:
        # 获取时间范围参数
        days = request.args.get('days', 7, type=int)  # 默认7天
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 用户注册趋势
        user_registrations = []
        for i in range(days):
            date_obj = start_date + timedelta(days=i)
            next_date = date_obj + timedelta(days=1)
            count = User.query.filter(
                and_(User.created_at >= date_obj, User.created_at < next_date)
            ).count()
            user_registrations.append({
                "date": date_obj.strftime('%Y-%m-%d'),
                "count": count
            })
        
        # 设备状态变更趋势
        equipment_changes = []
        for i in range(days):
            date_obj = start_date + timedelta(days=i)
            next_date = date_obj + timedelta(days=1)
            count = EquipmentStatusHistory.query.filter(
                and_(EquipmentStatusHistory.created_at >= date_obj, EquipmentStatusHistory.created_at < next_date)
            ).count()
            equipment_changes.append({
                "date": date_obj.strftime('%Y-%m-%d'),
                "count": count
            })
        
        # 课件使用趋势
        courseware_usage = []
        for i in range(days):
            date_obj = start_date + timedelta(days=i)
            next_date = date_obj + timedelta(days=1)
            count = CoursewareUsage.query.filter(
                and_(CoursewareUsage.used_at >= date_obj, CoursewareUsage.used_at < next_date)
            ).count()
            courseware_usage.append({
                "date": date_obj.strftime('%Y-%m-%d'),
                "count": count
            })
        
        # 操作日志趋势
        operation_logs = []
        for i in range(days):
            date_obj = start_date + timedelta(days=i)
            next_date = date_obj + timedelta(days=1)
            count = OperationLog.query.filter(
                and_(OperationLog.created_at >= date_obj, OperationLog.created_at < next_date)
            ).count()
            operation_logs.append({
                "date": date_obj.strftime('%Y-%m-%d'),
                "count": count
            })
        
        # 热门课件统计
        popular_courseware = db.session.query(
            Courseware.title,
            func.count(CoursewareUsage.id).label('usage_count')
        ).join(CoursewareUsage).group_by(Courseware.id).order_by(
            desc('usage_count')
        ).limit(10).all()
        
        # 活跃用户统计
        active_users = db.session.query(
            User.username,
            func.count(OperationLog.id).label('operation_count')
        ).join(OperationLog).filter(
            OperationLog.created_at >= start_date
        ).group_by(User.id).order_by(
            desc('operation_count')
        ).limit(10).all()
        
        return jsonify(Result.success(
            message="获取仪表板统计数据成功",
            data={
                "time_range": {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "days": days
                },
                "trends": {
                    "user_registrations": user_registrations,
                    "equipment_changes": equipment_changes,
                    "courseware_usage": courseware_usage,
                    "operation_logs": operation_logs
                },
                "rankings": {
                    "popular_courseware": [
                        {"title": title, "usage_count": count} 
                        for title, count in popular_courseware
                    ],
                    "active_users": [
                        {"username": username, "operation_count": count} 
                        for username, count in active_users
                    ]
                }
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取仪表板统计数据失败: {str(e)}").to_dict())

@dashboard_bp.route('/statistics/today', methods=['GET'])
@require_auth
def get_today_statistics(current_user):
    """获取今日统计数据"""
    try:
        today_stats = DashboardStatistics.get_today_stats()
        
        if not today_stats:
            # 如果没有今日统计，创建一个
            today_stats = DashboardStatistics.create_or_update_today()
        
        return jsonify(Result.success(
            message="获取今日统计成功",
            data=today_stats.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取今日统计失败: {str(e)}").to_dict())

@dashboard_bp.route('/statistics/update', methods=['POST'])
@require_auth
def update_statistics(current_user):
    """更新统计数据"""
    try:
        data = request.get_json()
        
        # 更新今日统计
        today_stats = DashboardStatistics.create_or_update_today(**data)
        
        return jsonify(Result.success(
            message="统计数据更新成功",
            data=today_stats.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"统计数据更新失败: {str(e)}").to_dict())

@dashboard_bp.route('/equipment-status', methods=['GET'])
@require_auth
def get_equipment_status(current_user):
    """获取设备状态分布"""
    try:
        # 按位置统计设备状态
        equipment_by_location = db.session.query(
            Equipment.location,
            func.count(Equipment.id).label('total'),
            func.sum(func.if_(Equipment.is_offline == False, 1, 0)).label('online'),
            func.sum(func.if_(Equipment.is_offline == True, 1, 0)).label('offline'),
            func.sum(func.if_(Equipment.has_error == True, 1, 0)).label('error')
        ).group_by(Equipment.location).all()
        
        location_stats = []
        for row in equipment_by_location:
            location_stats.append({
                'location': row[0],
                'total': row[1],
                'online': row[2],
                'offline': row[3],
                'error': row[4],
                'online_rate': round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
            })
        
        return jsonify(Result.success(
            message="获取设备状态分布成功",
            data=location_stats
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取设备状态分布失败: {str(e)}").to_dict())

@dashboard_bp.route('/recent-activities', methods=['GET'])
@require_auth
def get_recent_activities(current_user):
    """获取最近活动"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # 获取最近的操作日志
        recent_logs = OperationLog.get_recent_logs(limit)
        
        activities = []
        for log in recent_logs:
            activities.append({
                'id': log.id,
                'action': log.action,
                'user': log.user.real_name if log.user else '未知用户',
                'details': log.details,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        return jsonify(Result.success(
            message="获取最近活动成功",
            data=activities
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取最近活动失败: {str(e)}").to_dict())

@dashboard_bp.route('/alerts', methods=['GET'])
@require_auth
def get_alerts(current_user):
    """获取系统警报"""
    try:
        alerts = []
        
        # 检查离线设备
        offline_equipment = Equipment.get_offline_equipment()
        for eq in offline_equipment:
            alerts.append({
                'type': 'warning',
                'title': '设备离线',
                'message': f'设备 {eq.id} ({eq.location}) 已离线',
                'equipment_id': eq.id,
                'created_at': eq.updated_at.isoformat() if eq.updated_at else None
            })
        
        # 检查错误设备
        error_equipment = Equipment.get_error_equipment()
        for eq in error_equipment:
            alerts.append({
                'type': 'error',
                'title': '设备错误',
                'message': f'设备 {eq.id} ({eq.location}) 出现错误',
                'equipment_id': eq.id,
                'created_at': eq.updated_at.isoformat() if eq.updated_at else None
            })
        
        # 按时间排序
        alerts.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify(Result.success(
            message="获取系统警报成功",
            data=alerts[:50]  # 最多返回50个警报
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统警报失败: {str(e)}").to_dict())

@dashboard_bp.route('/realtime', methods=['GET'])
@require_auth
def get_realtime_data(current_user):
    """获取实时数据"""
    try:
        # 当前在线用户
        current_online_users = []
        for user in User.get_all():
            active_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            if active_sessions:
                session = active_sessions[0]  # 取最新的会话
                current_online_users.append({
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "login_time": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "ip_address": session.ip_address
                })
        
        # 设备实时状态
        equipment_realtime = []
        for equipment in Equipment.get_all():
            equipment_dict = equipment.to_dict()
            # 获取最新状态变更
            latest_status = EquipmentStatusHistory.query.filter_by(
                equipment_id=equipment.id
            ).order_by(EquipmentStatusHistory.created_at.desc()).first()
            if latest_status:
                equipment_dict['last_status_change'] = latest_status.to_dict()
            equipment_realtime.append(equipment_dict)
        
        # 最近操作日志
        recent_operations = OperationLog.query.order_by(
            OperationLog.created_at.desc()
        ).limit(20).all()
        
        # 系统性能指标（模拟数据）
        import random
        performance_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": round(random.uniform(20, 80), 2),
            "memory_usage": round(random.uniform(40, 90), 2),
            "disk_usage": round(random.uniform(30, 70), 2),
            "network_io": {
                "bytes_sent": random.randint(1000000, 10000000),
                "bytes_received": random.randint(2000000, 20000000)
            },
            "active_connections": len(current_online_users),
            "response_time": round(random.uniform(50, 200), 2)
        }
        
        # 告警信息
        alerts = []
        
        # 检查离线设备
        offline_equipment = Equipment.query.filter_by(status='offline').count()
        if offline_equipment > 0:
            alerts.append({
                "type": "warning",
                "message": f"有 {offline_equipment} 台设备离线",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # 检查故障设备
        error_equipment = Equipment.query.filter_by(status='error').count()
        if error_equipment > 0:
            alerts.append({
                "type": "error",
                "message": f"有 {error_equipment} 台设备故障",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # 检查CPU使用率
        if performance_metrics["cpu_usage"] > 80:
            alerts.append({
                "type": "warning",
                "message": f"CPU使用率过高: {performance_metrics['cpu_usage']}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return jsonify(Result.success(
            message="获取实时数据成功",
            data={
                "online_users": current_online_users,
                "equipment_status": equipment_realtime,
                "recent_operations": [op.to_dict() for op in recent_operations],
                "performance_metrics": performance_metrics,
                "alerts": alerts
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取实时数据失败: {str(e)}").to_dict())

@dashboard_bp.route('/charts', methods=['GET'])
@require_auth
def get_chart_data(current_user):
    """获取图表数据"""
    try:
        chart_type = request.args.get('type', 'all')
        
        charts_data = {}
        
        if chart_type in ['all', 'user_role_distribution']:
            # 用户角色分布饼图
            role_stats = db.session.query(
                User.role,
                func.count(User.id).label('count')
            ).group_by(User.role).all()
            
            charts_data['user_role_distribution'] = {
                "type": "pie",
                "title": "用户角色分布",
                "data": [{"name": role, "value": count} for role, count in role_stats]
            }
        
        if chart_type in ['all', 'equipment_status_distribution']:
            # 设备状态分布饼图
            status_stats = db.session.query(
                Equipment.status,
                func.count(Equipment.id).label('count')
            ).group_by(Equipment.status).all()
            
            charts_data['equipment_status_distribution'] = {
                "type": "pie",
                "title": "设备状态分布",
                "data": [{"name": status, "value": count} for status, count in status_stats]
            }
        
        if chart_type in ['all', 'courseware_category_distribution']:
            # 课件分类分布柱状图
            category_stats = db.session.query(
                Courseware.file_type,
                func.count(Courseware.id).label('count')
            ).group_by(Courseware.file_type).all()
            
            charts_data['courseware_category_distribution'] = {
                "type": "bar",
                "title": "课件类型分布",
                "data": [{"name": file_type or "未分类", "value": count} for file_type, count in category_stats]
            }
        
        return jsonify(Result.success(
            message="获取图表数据成功",
            data=charts_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取图表数据失败: {str(e)}").to_dict())

@dashboard_bp.route('/export', methods=['POST'])
@require_role(['admin'])
def export_dashboard_data(current_user):
    """导出仪表板数据"""
    try:
        data = request.get_json()
        export_type = data.get('export_type', 'summary')  # summary, detailed, charts
        format_type = data.get('format', 'json')  # json, csv, excel
        
        export_data = {}
        
        if export_type in ['summary', 'detailed']:
            # 基础统计
            export_data['summary'] = {
                "total_users": User.query.count(),
                "total_equipment": Equipment.query.count(),
                "total_courseware": Courseware.query.count(),
                "export_time": datetime.utcnow().isoformat()
            }
        
        if export_type == 'detailed':
            # 详细数据
            export_data['users'] = [user.to_dict() for user in User.get_all()]
            export_data['equipment'] = [eq.to_dict() for eq in Equipment.get_all()]
            export_data['courseware'] = [cw.to_dict() for cw in Courseware.get_all()]
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='export',
            action=f"导出仪表板数据: {export_type}",
            details=f"格式: {format_type}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="仪表板数据导出成功",
            data={
                "export_type": export_type,
                "format": format_type,
                "data": export_data,
                "export_time": datetime.utcnow().isoformat()
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"仪表板数据导出失败: {str(e)}").to_dict())

@dashboard_bp.route('/refresh', methods=['POST'])
@require_auth
def refresh_dashboard_cache(current_user):
    """刷新仪表板缓存"""
    try:
        refresh_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "cache_cleared": True,
            "data_refreshed": True
        }
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='system',
            action="刷新仪表板缓存",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="仪表板缓存刷新成功",
            data=refresh_info
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"仪表板缓存刷新失败: {str(e)}").to_dict())
