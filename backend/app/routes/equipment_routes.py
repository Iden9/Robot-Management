from flask import request, jsonify, Blueprint, send_file
from app.models import Equipment, EquipmentLog, OperationLog, EquipmentStatusHistory
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
from sqlalchemy import or_, and_
import datetime
import pandas as pd
import io
import os

# 创建设备蓝图
equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('', methods=['GET'])
@require_auth
def get_equipment_list(current_user):
    """获取设备列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        location = request.args.get('location')
        search = request.args.get('search', '').strip()
        maintenance_mode = request.args.get('maintenance_mode')
        
        query = Equipment.query
        
        # 搜索过滤
        if search:
            query = query.filter(or_(
                Equipment.id.contains(search),
                Equipment.location.contains(search),
                Equipment.ip_address.contains(search)
            ))
        
        # 状态过滤 
        if status == 'online':
            query = query.filter_by(status='online')
        elif status == 'offline':
            query = query.filter_by(status='offline')
        elif status == 'error':
            query = query.filter_by(status='error')
        elif status == 'maintenance':
            # 维护模式字段不存在，跳过
            pass
        
        # 位置过滤
        if location:
            query = query.filter(Equipment.location.contains(location))
            
        # 维护模式过滤（字段不存在，跳过）
        # if maintenance_mode is not None:
        #     query = query.filter_by(maintenance_mode=bool(int(maintenance_mode)))
        
        # 按更新时间排序
        query = query.order_by(Equipment.updated_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 获取设备详细信息
        equipment_data = []
        for eq in pagination.items:
            eq_dict = eq.to_dict()
            # 获取健康评分
            eq_dict['health_score'] = eq.get_health_score()
            # 获取最近状态变化
            recent_status = EquipmentStatusHistory.query.filter_by(
                equipment_id=eq.id
            ).order_by(EquipmentStatusHistory.created_at.desc()).first()
            if recent_status:
                eq_dict['last_status_change'] = recent_status.to_dict()
            equipment_data.append(eq_dict)
        
        return jsonify(Result.success(
            message="获取设备列表成功",
            data={
                'equipment': equipment_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取设备列表失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>', methods=['GET'])
@require_auth
def get_equipment(current_user, equipment_id):
    """获取单个设备信息"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        return jsonify(Result.success(
            message="获取设备信息成功",
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取设备信息失败: {str(e)}").to_dict())

@equipment_bp.route('', methods=['POST'])
@require_role(['admin', 'operator'])
def create_equipment(current_user):
    """创建设备"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['id', 'location']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查设备ID是否已存在
        if Equipment.get_by_id(data['id']):
            return jsonify(Result.error(message="设备ID已存在", code=400).to_dict())
        
        # 创建新设备
        equipment = Equipment(
            id=data['id'],
            location=data['location'],
            status=data.get('status', 'offline'),
            ip_address=data.get('ip_address'),
            usage_rate=data.get('usage_rate', '0%')
        )
        equipment.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment.id,
            operation="创建设备",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="设备创建成功",
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备创建失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_equipment(current_user, equipment_id):
    """更新设备信息"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        if not data:
            return jsonify(Result.error(message="请提供更新数据", code=400).to_dict())
        
        # 更新字段
        if 'location' in data:
            equipment.location = data['location']
        if 'status' in data:
            equipment.status = data['status']
        if 'ip_address' in data:
            equipment.ip_address = data['ip_address']
        if 'usage_rate' in data:
            equipment.usage_rate = data['usage_rate']
        if 'is_offline' in data:
            equipment.is_offline = data['is_offline']
        if 'has_error' in data:
            equipment.has_error = data['has_error']
        
        equipment.updated_at = datetime.datetime.utcnow()
        equipment.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment.id,
            operation="更新设备信息",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="设备更新成功",
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备更新失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_equipment(current_user, equipment_id):
    """删除设备"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        equipment.delete()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment_id,
            operation="删除设备",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="设备删除成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备删除失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>/logs', methods=['GET'])
@require_auth
def get_equipment_logs(current_user, equipment_id):
    """获取设备日志"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        log_type = request.args.get('log_type')
        
        query = EquipmentLog.query.filter_by(equipment_id=equipment_id)
        
        if log_type:
            query = query.filter_by(log_type=log_type)
        
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

@equipment_bp.route('/<equipment_id>/logs', methods=['POST'])
@require_auth
def create_equipment_log(current_user, equipment_id):
    """创建设备日志"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        
        # 数据验证
        if not data or not data.get('log_type') or not data.get('message'):
            return jsonify(Result.error(message="日志类型和消息不能为空", code=400).to_dict())
        
        log = EquipmentLog.create_log(
            equipment_id=equipment_id,
            log_type=data['log_type'],
            message=data['message']
        )
        
        return jsonify(Result.success(
            message="设备日志创建成功",
            data=log.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备日志创建失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>/status', methods=['PUT'])
@require_role(['admin', 'operator'])
def update_equipment_status(current_user, equipment_id):
    """更新设备状态"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        new_status = data.get('status')
        reason = data.get('reason', '')
        
        if not new_status:
            return jsonify(Result.error(message="状态不能为空", code=400).to_dict())
        
        # 记录状态变更历史
        old_status = equipment.status
        if old_status != new_status:
            EquipmentStatusHistory.create_change_record(
                equipment_id=equipment_id,
                previous_status=old_status,
                current_status=new_status,
                change_reason=reason,
                changed_by=current_user.id
            )
        
        # 更新设备状态
        equipment.update_status(new_status)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment_id,
            operation=f"状态变更: {old_status} -> {new_status}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="设备状态更新成功",
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备状态更新失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>/maintenance', methods=['POST'])
@require_role(['admin', 'operator'])
def toggle_maintenance_mode(current_user, equipment_id):
    """切换设备维护模式"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        maintenance_mode = data.get('maintenance_mode')
        
        if maintenance_mode is None:
            # 切换维护模式
            equipment.toggle_maintenance_mode()
        else:
            # 设置维护模式
            equipment.set_maintenance_mode(maintenance_mode)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        action = "进入维护模式" if equipment.maintenance_mode else "退出维护模式"
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment_id,
            operation=action,
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=f"设备{action}成功",
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"维护模式切换失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>/control', methods=['POST'])
@require_role(['admin', 'operator'])
def control_equipment(current_user, equipment_id):
    """设备控制操作"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        data = request.get_json()
        action = data.get('action')
        
        if not action:
            return jsonify(Result.error(message="操作类型不能为空", code=400).to_dict())
        
        # 执行设备控制操作
        result_message = ""
        if action == 'start':
            # 启动设备
            equipment.start()
            result_message = "设备启动成功"
        elif action == 'stop':
            # 停止设备
            equipment.stop()
            result_message = "设备停止成功"
        elif action == 'restart':
            # 重启设备
            equipment.restart()
            result_message = "设备重启成功"
        elif action == 'shutdown':
            # 关闭设备
            equipment.shutdown()
            result_message = "设备关闭成功"
        elif action == 'reboot':
            # 重新启动
            equipment.reboot()
            result_message = "设备重新启动成功"
        elif action == 'diagnose':
            # 设备诊断
            diagnosis = equipment.diagnose()
            result_message = "设备诊断完成"
        else:
            return jsonify(Result.error(message="不支持的操作类型", code=400).to_dict())
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_equipment_operation(
            user_id=current_user.id,
            equipment_id=equipment_id,
            operation=f"设备控制: {action}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message=result_message,
            data=equipment.to_dict()
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"设备控制失败: {str(e)}").to_dict())

@equipment_bp.route('/<equipment_id>/status-history', methods=['GET'])
@require_auth
def get_equipment_status_history(current_user, equipment_id):
    """获取设备状态变更历史"""
    try:
        equipment = Equipment.get_by_id(equipment_id)
        if not equipment:
            return jsonify(Result.error(message="设备不存在", code=404).to_dict())
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history = EquipmentStatusHistory.get_by_equipment(equipment_id)
        
        return jsonify(Result.success(
            message="获取状态历史成功",
            data=[record.to_dict() for record in history]
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取状态历史失败: {str(e)}").to_dict())

@equipment_bp.route('/statistics', methods=['GET'])
@require_auth
def get_equipment_statistics(current_user):
    """获取设备统计信息"""
    try:
        # 设备状态统计
        status_stats = db.session.query(Equipment.status, db.func.count(Equipment.id)).group_by(Equipment.status).all()
        
        # 在线设备统计
        online_count = Equipment.query.filter_by(status='online').count()
        offline_count = Equipment.query.filter_by(status='offline').count()
        error_count = Equipment.query.filter_by(status='error').count()
        maintenance_count = 0  # 维护模式字段不存在
        
        # 设备位置分布
        location_stats = db.session.query(Equipment.location, db.func.count(Equipment.id)).group_by(Equipment.location).all()
        
        # 设备健康状况
        total_devices = Equipment.query.count()
        healthy_devices = Equipment.query.filter(Equipment.has_error == False).count()
        
        # 最近添加的设备
        recent_equipment = Equipment.query.order_by(Equipment.created_at.desc()).limit(5).all()
        
        return jsonify(Result.success(
            message="获取设备统计成功",
            data={
                "total_equipment": total_devices,
                "online_count": online_count,
                "offline_count": offline_count,
                "error_count": error_count,
                "maintenance_count": maintenance_count,
                "healthy_ratio": round((healthy_devices / total_devices * 100) if total_devices > 0 else 0, 2),
                "status_distribution": dict(status_stats),
                "location_distribution": dict(location_stats),
                "recent_equipment": [eq.to_dict() for eq in recent_equipment]
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取设备统计失败: {str(e)}").to_dict())

@equipment_bp.route('/batch-operation', methods=['POST'])
@require_role(['admin', 'operator'])
def batch_equipment_operation(current_user):
    """批量设备操作"""
    try:
        data = request.get_json()
        equipment_ids = data.get('equipment_ids', [])
        operation = data.get('operation')
        
        if not equipment_ids or not operation:
            return jsonify(Result.error(message="设备ID列表和操作类型不能为空", code=400).to_dict())
        
        success_count = 0
        failed_count = 0
        results = []
        
        for equipment_id in equipment_ids:
            try:
                equipment = Equipment.get_by_id(equipment_id)
                if not equipment:
                    results.append({"equipment_id": equipment_id, "status": "failed", "message": "设备不存在"})
                    failed_count += 1
                    continue
                
                if operation == 'delete':
                    equipment.delete()
                elif operation == 'maintenance_on':
                    equipment.set_maintenance_mode(True)
                elif operation == 'maintenance_off':
                    equipment.set_maintenance_mode(False)
                elif operation == 'restart':
                    equipment.restart()
                else:
                    results.append({"equipment_id": equipment_id, "status": "failed", "message": "不支持的操作"})
                    failed_count += 1
                    continue
                
                results.append({"equipment_id": equipment_id, "status": "success", "message": "操作成功"})
                success_count += 1
                
            except Exception as e:
                results.append({"equipment_id": equipment_id, "status": "failed", "message": str(e)})
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action=f"批量设备操作: {operation}",
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

@equipment_bp.route('/export', methods=['GET'])
@require_auth
def export_equipment_list(current_user):
    """导出设备列表"""
    try:
        # 获取过滤参数
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = Equipment.query
        
        # 应用过滤条件
        if search:
            query = query.filter(or_(
                Equipment.id.contains(search),
                Equipment.location.contains(search),
                Equipment.ip_address.contains(search)
            ))
        
        if status and status != 'all':
            if status == 'online':
                query = query.filter_by(status='online')
            elif status == 'offline':
                query = query.filter_by(status='offline')
            elif status == 'error':
                query = query.filter_by(status='error')
        
        # 获取设备列表
        equipment_list = query.order_by(Equipment.created_at.desc()).all()
        
        # 准备导出数据
        export_data = []
        for eq in equipment_list:
            export_data.append({
                '设备ID': eq.id,
                '设备位置': eq.location,
                'IP地址': eq.ip_address or '',
                '状态': eq.status,
                '使用率': eq.usage_rate or '0%',
                '是否离线': '是' if eq.is_offline else '否',
                '是否有错误': '是' if eq.has_error else '否',
                '创建时间': eq.created_at.strftime('%Y-%m-%d %H:%M:%S') if eq.created_at else '',
                '更新时间': eq.updated_at.strftime('%Y-%m-%d %H:%M:%S') if eq.updated_at else ''
            })
        
        # 创建Excel文件
        df = pd.DataFrame(export_data)
        
        # 创建BytesIO对象
        output = io.BytesIO()
        
        # 使用ExcelWriter写入数据
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='设备列表', index=False)
            
            # 获取工作表并设置列宽
            workbook = writer.book
            worksheet = writer.sheets['设备列表']
            
            # 自动调整列宽
            for column in worksheet.columns:
                max_length = 0
                column_name = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_name].width = adjusted_width
        
        output.seek(0)
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="导出设备列表",
            details=f"导出了 {len(export_data)} 条设备记录",
            ip_address=client_ip
        )
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"设备列表_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify(Result.error(message=f"导出设备列表失败: {str(e)}").to_dict())

@equipment_bp.route('/import-template', methods=['GET'])
@require_auth
def download_import_template(current_user):
    """下载设备导入模板"""
    try:
        # 创建模板数据
        template_data = {
            '设备ID': ['ROBOT001', 'ROBOT002'],
            '设备位置': ['实验室A', '实验室B'],
            'IP地址': ['192.168.1.100', '192.168.1.101'],
            '状态': ['online', 'offline'],
            '使用率': ['85%', '60%'],
            '描述信息': ['G1机器人-实验用', 'G1机器人-演示用']
        }
        
        # 创建DataFrame
        df = pd.DataFrame(template_data)
        
        # 创建BytesIO对象
        output = io.BytesIO()
        
        # 使用ExcelWriter写入数据
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='设备导入模板', index=False)
            
            # 获取工作表
            workbook = writer.book
            worksheet = writer.sheets['设备导入模板']
            
            # 设置列宽
            column_widths = {
                'A': 15,  # 设备ID
                'B': 20,  # 设备位置
                'C': 18,  # IP地址
                'D': 12,  # 状态
                'E': 12,  # 使用率
                'F': 25   # 描述信息
            }
            
            for column, width in column_widths.items():
                worksheet.column_dimensions[column].width = width
            
            # 添加说明工作表
            notes_data = {
                '字段名': ['设备ID', '设备位置', 'IP地址', '状态', '使用率', '描述信息'],
                '是否必填': ['是', '是', '否', '否', '否', '否'],
                '格式说明': [
                    '唯一标识符，不能重复',
                    '设备所在位置',
                    'IPv4格式，如：192.168.1.100',
                    'online/offline/error之一，默认为offline',
                    '百分比格式，如：85%',
                    '设备的描述信息'
                ],
                '示例': [
                    'ROBOT001',
                    '实验室A',
                    '192.168.1.100',
                    'online',
                    '85%',
                    'G1机器人-实验用'
                ]
            }
            
            notes_df = pd.DataFrame(notes_data)
            notes_df.to_excel(writer, sheet_name='导入说明', index=False)
            
            # 设置说明工作表的列宽
            notes_worksheet = writer.sheets['导入说明']
            notes_column_widths = {'A': 15, 'B': 12, 'C': 35, 'D': 20}
            for column, width in notes_column_widths.items():
                notes_worksheet.column_dimensions[column].width = width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name="设备导入模板.xlsx"
        )
        
    except Exception as e:
        return jsonify(Result.error(message=f"下载模板失败: {str(e)}").to_dict())

@equipment_bp.route('/batch-import', methods=['POST'])
@require_role(['admin', 'operator'])
def batch_import_equipment(current_user):
    """批量导入设备"""
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify(Result.error(message="请选择要导入的文件", code=400).to_dict())
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(Result.error(message="请选择要导入的文件", code=400).to_dict())
        
        # 检查文件类型
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            return jsonify(Result.error(message="文件格式不支持，请上传Excel或CSV文件", code=400).to_dict())
        
        # 读取文件内容
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, sheet_name=0)  # 读取第一个工作表
        except Exception as e:
            return jsonify(Result.error(message=f"文件读取失败: {str(e)}", code=400).to_dict())
        
        # 验证必需的列
        required_columns = ['设备ID', '设备位置']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify(Result.error(
                message=f"文件缺少必需的列: {', '.join(missing_columns)}",
                code=400
            ).to_dict())
        
        # 统计变量
        success_count = 0
        failed_count = 0
        total_count = len(df)
        failed_items = []
        
        # 逐行处理数据
        for index, row in df.iterrows():
            try:
                # 获取设备数据
                equipment_id = str(row['设备ID']).strip()
                location = str(row['设备位置']).strip()
                
                # 验证必填字段
                if not equipment_id or equipment_id == 'nan':
                    failed_items.append({
                        'row': index + 2,  # Excel行号从2开始（第1行是标题）
                        'error': '设备ID不能为空'
                    })
                    failed_count += 1
                    continue
                
                if not location or location == 'nan':
                    failed_items.append({
                        'row': index + 2,
                        'error': '设备位置不能为空'
                    })
                    failed_count += 1
                    continue
                
                # 检查设备ID是否已存在
                existing_equipment = Equipment.get_by_id(equipment_id)
                if existing_equipment:
                    failed_items.append({
                        'row': index + 2,
                        'error': '设备ID已存在'
                    })
                    failed_count += 1
                    continue
                
                # 获取可选字段
                ip_address = str(row.get('IP地址', '')).strip()
                if ip_address == 'nan':
                    ip_address = None
                
                status = str(row.get('状态', 'offline')).strip().lower()
                if status == 'nan' or status not in ['online', 'offline', 'error']:
                    status = 'offline'
                
                usage_rate = str(row.get('使用率', '0%')).strip()
                if usage_rate == 'nan':
                    usage_rate = '0%'
                
                # 创建设备
                equipment = Equipment(
                    id=equipment_id,
                    location=location,
                    ip_address=ip_address,
                    status=status,
                    usage_rate=usage_rate,
                    is_offline=(status == 'offline'),
                    has_error=(status == 'error')
                )
                equipment.save()
                success_count += 1
                
            except Exception as e:
                failed_items.append({
                    'row': index + 2,
                    'error': f'处理错误: {str(e)}'
                })
                failed_count += 1
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="批量导入设备",
            details=f"总计: {total_count}, 成功: {success_count}, 失败: {failed_count}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="批量导入完成",
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": total_count,
                "failed_items": failed_items
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"批量导入失败: {str(e)}").to_dict())
