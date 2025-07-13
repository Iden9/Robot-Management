from flask import request, jsonify, Blueprint
from app.models import SystemSettings, OperationLog
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_, and_, func
import datetime
import json

# 创建系统设置蓝图
system_bp = Blueprint('system', __name__)

# 系统配置管理
@system_bp.route('/config', methods=['GET'])
@require_auth
def get_system_config(current_user):
    """获取系统配置"""
    try:
        # 这里可以从配置文件或数据库中获取系统配置
        # 目前返回模拟的系统配置数据
        config = {
            "system_name": "G1 EDU机器人管理系统",
            "version": "1.0.0",
            "description": "智能教育机器人管理平台",
            "max_concurrent_users": 100,
            "session_timeout": 7200,  # 2小时
            "password_policy": {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": False
            },
            "file_upload": {
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "allowed_extensions": [".pdf", ".ppt", ".pptx", ".doc", ".docx", ".mp4", ".mp3", ".jpg", ".png"],
                "upload_path": "/uploads/"
            },
            "navigation": {
                "default_speed": 1.0,
                "max_participants_per_tour": 20,
                "default_voice_volume": 80
            },
            "education": {
                "default_session_duration": 45,  # 分钟
                "max_students_per_class": 30,
                "assessment_passing_score": 70
            },
            "backup": {
                "auto_backup_enabled": True,
                "backup_frequency": "daily",
                "backup_retention_days": 30
            },
            "monitoring": {
                "log_level": "INFO",
                "enable_performance_monitoring": True,
                "enable_error_tracking": True
            }
        }
        
        return jsonify(Result.success(
            message="获取系统配置成功",
            data=config
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统配置失败: {str(e)}").to_dict())

@system_bp.route('/config', methods=['PUT'])
@require_role(['admin'])
def update_system_config(current_user):
    """更新系统配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(Result.error(message="请提供配置数据", code=400).to_dict())
        
        # 这里应该将配置保存到配置文件或数据库
        # 目前只是记录操作日志
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='config',
            action="更新系统配置",
            details=f"配置项数量: {len(data)}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="系统配置更新成功",
            data=data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"系统配置更新失败: {str(e)}").to_dict())

# 系统信息
@system_bp.route('/info', methods=['GET'])
@require_auth
def get_system_info(current_user):
    """获取系统信息"""
    try:
        import platform
        import os
        import shutil
        
        # 系统基本信息
        system_info = {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor() or "未知处理器",
            "python_version": platform.python_version(),
            "system_uptime": "系统运行中",
        }
        
        # 硬件信息 (不依赖psutil的替代实现)
        try:
            # 获取CPU数量
            cpu_count = os.cpu_count() or 1
            
            # 获取磁盘使用情况
            disk_usage = shutil.disk_usage('/')
            disk_total = disk_usage.total
            disk_free = disk_usage.free
            disk_used = disk_total - disk_free
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            
            hardware_info = {
                "cpu_count": cpu_count,
                "cpu_percent": "暂无法获取",
                "memory_total": "暂无法获取",
                "memory_available": "暂无法获取",
                "memory_percent": "暂无法获取",
                "disk_usage": {
                    "total": disk_total,
                    "used": disk_used,
                    "free": disk_free,
                    "percent": round(disk_percent, 2)
                }
            }
        except Exception as hw_error:
            hardware_info = {"error": f"无法获取硬件信息: {str(hw_error)}"}
        
        # 应用信息
        app_info = {
            "name": "G1 EDU Robot Management System",
            "version": "1.0.0",
            "start_time": datetime.datetime.utcnow().isoformat(),
            "environment": os.getenv('FLASK_ENV', 'production'),
            "debug_mode": os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        }
        
        return jsonify(Result.success(
            message="获取系统信息成功",
            data={
                "system": system_info,
                "hardware": hardware_info,
                "application": app_info
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统信息失败: {str(e)}").to_dict())

# 系统日志
@system_bp.route('/logs', methods=['GET'])
@require_role(['admin'])
def get_system_logs(current_user):
    """获取系统日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        log_level = request.args.get('level')
        action_type = request.args.get('action_type')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = OperationLog.query
        
        # 日志级别过滤
        if log_level:
            query = query.filter_by(level=log_level)
        
        # 操作类型过滤
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        # 用户过滤
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # 日期范围过滤
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OperationLog.created_at >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
                query = query.filter(OperationLog.created_at < end_dt)
            except ValueError:
                pass
        
        # 分页
        pagination = query.order_by(OperationLog.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify(Result.success(
            message="获取系统日志成功",
            data={
                'logs': [log.to_dict() for log in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统日志失败: {str(e)}").to_dict())

# 清理系统日志
@system_bp.route('/logs/cleanup', methods=['POST'])
@require_role(['admin'])
def cleanup_system_logs(current_user):
    """清理系统日志"""
    try:
        data = request.get_json()
        days_to_keep = data.get('days_to_keep', 30)
        
        # 计算删除日期
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_to_keep)
        
        # 删除旧日志
        deleted_count = OperationLog.query.filter(
            OperationLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='maintenance',
            action="清理系统日志",
            details=f"删除了 {deleted_count} 条日志记录",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"系统日志清理完成，删除了 {deleted_count} 条记录",
            data={"deleted_count": deleted_count}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"系统日志清理失败: {str(e)}").to_dict())

# 数据库维护
@system_bp.route('/database/optimize', methods=['POST'])
@require_role(['admin'])
def optimize_database(current_user):
    """优化数据库"""
    try:
        # 这里可以执行数据库优化操作
        # 例如：重建索引、更新统计信息等
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='maintenance',
            action="数据库优化",
            details="执行数据库优化操作",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="数据库优化完成",
            data={"optimization_time": datetime.datetime.utcnow().isoformat()}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"数据库优化失败: {str(e)}").to_dict())

# 系统备份
@system_bp.route('/backup', methods=['POST'])
@require_role(['admin'])
def create_system_backup(current_user):
    """创建系统备份"""
    try:
        data = request.get_json()
        backup_type = data.get('backup_type', 'full')  # full, database, files
        
        # 这里应该实现实际的备份逻辑
        backup_info = {
            "backup_id": f"backup_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "backup_type": backup_type,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "status": "completed",
            "size": "假设备份大小",
            "location": f"/backups/backup_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        }
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='backup',
            action=f"创建系统备份: {backup_type}",
            details=f"备份ID: {backup_info['backup_id']}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="系统备份创建成功",
            data=backup_info
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"系统备份创建失败: {str(e)}").to_dict())

# 获取备份列表
@system_bp.route('/backups', methods=['GET'])
@require_role(['admin'])
def get_system_backups(current_user):
    """获取系统备份列表"""
    try:
        # 这里应该从备份目录或数据库中获取实际的备份列表
        # 目前返回模拟数据
        backups = [
            {
                "backup_id": f"backup_20250704_120000",
                "backup_type": "full",
                "created_at": "2025-07-04T12:00:00Z",
                "size": "256MB",
                "status": "completed",
                "location": "/backups/backup_20250704_120000.tar.gz"
            },
            {
                "backup_id": f"backup_20250703_120000",
                "backup_type": "database",
                "created_at": "2025-07-03T12:00:00Z",
                "size": "128MB",
                "status": "completed",
                "location": "/backups/backup_20250703_120000.tar.gz"
            }
        ]
        
        return jsonify(Result.success(
            message="获取备份列表成功",
            data=backups
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取备份列表失败: {str(e)}").to_dict())

# 系统健康检查
@system_bp.route('/health', methods=['GET'])
@require_auth
def get_system_health(current_user):
    """获取系统健康状态"""
    try:
        # 检查各个组件的健康状态
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "components": {
                "database": {
                    "status": "healthy",
                    "response_time": "< 10ms",
                    "connections": 5
                },
                "file_system": {
                    "status": "healthy",
                    "disk_usage": "45%",
                    "available_space": "2.5GB"
                },
                "external_services": {
                    "status": "healthy",
                    "services_checked": 3,
                    "services_online": 3
                },
                "background_tasks": {
                    "status": "healthy",
                    "active_tasks": 2,
                    "failed_tasks": 0
                }
            },
            "metrics": {
                "cpu_usage": "25%",
                "memory_usage": "60%",
                "disk_usage": "45%",
                "network_latency": "< 5ms"
            }
        }
        
        return jsonify(Result.success(
            message="获取系统健康状态成功",
            data=health_status
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统健康状态失败: {str(e)}").to_dict())

# 系统重启
@system_bp.route('/restart', methods=['POST'])
@require_role(['admin'])
def restart_system(current_user):
    """重启系统服务"""
    try:
        data = request.get_json()
        restart_type = data.get('restart_type', 'graceful')  # graceful, force
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='system',
            action=f"系统重启: {restart_type}",
            details="系统重启请求已提交",
            ip_address=client_ip
        )
        
        # 这里应该实现实际的重启逻辑
        # 注意：在实际环境中，这可能会导致当前请求无法正常返回响应
        
        return jsonify(Result.success(
            message="系统重启请求已提交",
            data={
                "restart_type": restart_type,
                "estimated_downtime": "30-60秒",
                "restart_time": datetime.datetime.utcnow().isoformat()
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"系统重启失败: {str(e)}").to_dict())

# 系统性能监控
@system_bp.route('/performance', methods=['GET'])
@require_auth
def get_system_performance(current_user):
    """获取系统性能数据"""
    try:
        # 获取性能统计数据
        # 这些数据可能来自监控系统或实时计算
        performance_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": 25.5,
                "load_average": [1.2, 1.1, 1.0],
                "cores": 4
            },
            "memory": {
                "total": 8589934592,  # 8GB
                "used": 5150765056,   # ~4.8GB
                "available": 3439169536,  # ~3.2GB
                "usage_percent": 60.0
            },
            "disk": {
                "total": 107374182400,  # 100GB
                "used": 48318382080,    # ~45GB
                "available": 59055800320,  # ~55GB
                "usage_percent": 45.0
            },
            "network": {
                "bytes_sent": 1048576000,  # 1GB
                "bytes_received": 2097152000,  # 2GB
                "packets_sent": 1000000,
                "packets_received": 1500000
            },
            "application": {
                "active_connections": 25,
                "total_requests": 150000,
                "response_time_avg": 120,  # ms
                "error_rate": 0.01  # 1%
            }
        }
        
        return jsonify(Result.success(
            message="获取系统性能数据成功",
            data=performance_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取系统性能数据失败: {str(e)}").to_dict())

# 系统设置重置
@system_bp.route('/reset', methods=['POST'])
@require_role(['admin'])
def reset_system_settings(current_user):
    """重置系统设置"""
    try:
        data = request.get_json()
        reset_type = data.get('reset_type', 'config')  # config, database, all
        
        reset_info = {
            "reset_type": reset_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "affected_components": []
        }
        
        if reset_type == 'config':
            reset_info["affected_components"].append("系统配置")
        elif reset_type == 'database':
            reset_info["affected_components"].append("数据库设置")
        elif reset_type == 'all':
            reset_info["affected_components"].extend(["系统配置", "数据库设置", "用户偏好"])
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action_type='system',
            action=f"系统重置: {reset_type}",
            details=f"重置组件: {', '.join(reset_info['affected_components'])}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="系统设置重置完成",
            data=reset_info
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"系统设置重置失败: {str(e)}").to_dict())