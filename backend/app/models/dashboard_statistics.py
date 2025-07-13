from app import db
from datetime import datetime, date, timedelta
import json

class DashboardStatistics(db.Model):
    """系统看板统计数据模型"""
    __tablename__ = 'dashboard_statistics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='统计ID')
    statistic_date = db.Column(db.Date, nullable=False, comment='统计日期')
    statistic_hour = db.Column(db.Integer, comment='统计小时(0-23)')
    total_devices = db.Column(db.Integer, default=0, comment='设备总数')
    total_online_devices = db.Column(db.Integer, default=0, comment='在线设备数')
    total_offline_devices = db.Column(db.Integer, default=0, comment='离线设备数')
    total_error_devices = db.Column(db.Integer, default=0, comment='错误设备数')
    total_maintenance_devices = db.Column(db.Integer, default=0, comment='维护设备数')
    total_courses_delivered = db.Column(db.Integer, default=0, comment='课程投递数')
    total_tours_conducted = db.Column(db.Integer, default=0, comment='导览进行数')
    total_interactions = db.Column(db.Integer, default=0, comment='交互总数')
    total_users = db.Column(db.Integer, default=0, comment='用户总数')
    active_users = db.Column(db.Integer, default=0, comment='活跃用户数')
    total_courseware = db.Column(db.Integer, default=0, comment='课件总数')
    total_navigation_points = db.Column(db.Integer, default=0, comment='导览点总数')
    total_operations = db.Column(db.Integer, default=0, comment='操作总数')
    failed_operations = db.Column(db.Integer, default=0, comment='失败操作数')
    average_response_time = db.Column(db.Numeric(8,2), default=0, comment='平均响应时间(毫秒)')
    peak_concurrent_users = db.Column(db.Integer, default=0, comment='并发用户峰值')
    total_data_transfer = db.Column(db.BigInteger, default=0, comment='数据传输量(字节)')
    system_uptime = db.Column(db.Integer, default=0, comment='系统运行时间(秒)')
    error_rate = db.Column(db.Numeric(5,2), default=0, comment='错误率(%)')
    performance_score = db.Column(db.Numeric(5,2), default=100, comment='性能评分')
    additional_metrics = db.Column(db.Text, comment='额外指标(JSON)')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def save(self):
        """保存统计数据"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """删除统计数据"""
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        """将统计数据对象转换为字典"""
        return {
            'id': self.id,
            'statistic_date': self.statistic_date.isoformat() if self.statistic_date else None,
            'statistic_hour': self.statistic_hour,
            'total_devices': self.total_devices,
            'total_online_devices': self.total_online_devices,
            'total_offline_devices': self.total_offline_devices,
            'total_error_devices': self.total_error_devices,
            'total_maintenance_devices': self.total_maintenance_devices,
            'total_courses_delivered': self.total_courses_delivered,
            'total_tours_conducted': self.total_tours_conducted,
            'total_interactions': self.total_interactions,
            'total_users': self.total_users,
            'active_users': self.active_users,
            'total_courseware': self.total_courseware,
            'total_navigation_points': self.total_navigation_points,
            'total_operations': self.total_operations,
            'failed_operations': self.failed_operations,
            'average_response_time': float(self.average_response_time) if self.average_response_time else 0,
            'peak_concurrent_users': self.peak_concurrent_users,
            'total_data_transfer': self.total_data_transfer,
            'system_uptime': self.system_uptime,
            'error_rate': float(self.error_rate) if self.error_rate else 0,
            'performance_score': float(self.performance_score) if self.performance_score else 100,
            'additional_metrics': self.get_additional_metrics(),
            'device_online_rate': self.get_device_online_rate(),
            'device_error_rate': self.get_device_error_rate(),
            'operation_success_rate': self.get_operation_success_rate(),
            'uptime_display': self.get_uptime_display(),
            'data_transfer_display': self.get_data_transfer_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def get_additional_metrics(self):
        """获取额外指标"""
        try:
            return json.loads(self.additional_metrics) if self.additional_metrics else {}
        except json.JSONDecodeError:
            return {}
    
    def set_additional_metrics(self, metrics):
        """设置额外指标"""
        self.additional_metrics = json.dumps(metrics, ensure_ascii=False) if metrics else None
    
    def get_uptime_display(self):
        """获取运行时间显示"""
        if not self.system_uptime:
            return "0秒"
        
        days = self.system_uptime // 86400
        hours = (self.system_uptime % 86400) // 3600
        minutes = (self.system_uptime % 3600) // 60
        seconds = self.system_uptime % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}秒")
        
        return "".join(parts)
    
    def get_data_transfer_display(self):
        """获取数据传输量显示"""
        if not self.total_data_transfer:
            return "0B"
        
        bytes_val = self.total_data_transfer
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}PB"
        
    def __repr__(self):
        hour_str = f" {self.statistic_hour}:00" if self.statistic_hour is not None else ""
        return f'<DashboardStatistics {self.statistic_date}{hour_str}>'
    
    @classmethod
    def get_by_id(cls, stats_id):
        """根据ID获取统计数据"""
        return cls.query.get(stats_id)
    
    @classmethod
    def get_by_date(cls, statistic_date):
        """根据日期获取统计数据"""
        return cls.query.filter_by(statistic_date=statistic_date).first()
    
    @classmethod
    def get_today_stats(cls):
        """获取今日统计数据"""
        today = date.today()
        return cls.get_by_date(today)
    
    @classmethod
    def get_date_range_stats(cls, start_date, end_date):
        """获取日期范围内的统计数据"""
        return cls.query.filter(
            cls.statistic_date >= start_date,
            cls.statistic_date <= end_date
        ).order_by(cls.statistic_date.desc()).all()
    
    @classmethod
    def get_recent_stats(cls, days=7):
        """获取最近几天的统计数据"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        return cls.get_date_range_stats(start_date, end_date)
    
    @classmethod
    def get_hourly_stats(cls, target_date):
        """获取指定日期的小时统计数据"""
        return cls.query.filter(
            cls.statistic_date == target_date,
            cls.statistic_hour.isnot(None)
        ).order_by(cls.statistic_hour.asc()).all()
    
    @classmethod
    def get_by_date_and_hour(cls, statistic_date, statistic_hour):
        """根据日期和小时获取统计数据"""
        return cls.query.filter_by(
            statistic_date=statistic_date,
            statistic_hour=statistic_hour
        ).first()
    
    @classmethod
    def create_or_update_today(cls, **kwargs):
        """创建或更新今日统计数据"""
        today = date.today()
        stats = cls.get_by_date(today)
        
        if stats:
            # 更新现有统计
            for key, value in kwargs.items():
                if hasattr(stats, key):
                    setattr(stats, key, value)
        else:
            # 创建新统计
            stats = cls(statistic_date=today, **kwargs)
        
        stats.save()
        return stats
    
    def update_device_counts(self, total=None, online=None, offline=None, error=None, maintenance=None):
        """更新设备数量统计"""
        if total is not None:
            self.total_devices = total
        if online is not None:
            self.total_online_devices = online
        if offline is not None:
            self.total_offline_devices = offline
        if error is not None:
            self.total_error_devices = error
        if maintenance is not None:
            self.total_maintenance_devices = maintenance
        self.updated_at = datetime.utcnow()
        self.save()
    
    def increment_courses(self, count=1):
        """增加课程数量"""
        self.total_courses_delivered += count
        self.save()
    
    def increment_tours(self, count=1):
        """增加导览数量"""
        self.total_tours_conducted += count
        self.save()
    
    def increment_interactions(self, count=1):
        """增加交互数量"""
        self.total_interactions += count
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_user_stats(self, total_users=None, active_users=None):
        """更新用户统计"""
        if total_users is not None:
            self.total_users = total_users
        if active_users is not None:
            self.active_users = active_users
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_content_stats(self, courseware_count=None, navigation_points=None):
        """更新内容统计"""
        if courseware_count is not None:
            self.total_courseware = courseware_count
        if navigation_points is not None:
            self.total_navigation_points = navigation_points
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_operation_stats(self, total_operations=None, failed_operations=None):
        """更新操作统计"""
        if total_operations is not None:
            self.total_operations = total_operations
        if failed_operations is not None:
            self.failed_operations = failed_operations
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_performance_metrics(self, response_time=None, peak_users=None, 
                                  data_transfer=None, uptime=None, error_rate=None, 
                                  performance_score=None):
        """更新性能指标"""
        if response_time is not None:
            self.average_response_time = response_time
        if peak_users is not None:
            self.peak_concurrent_users = peak_users
        if data_transfer is not None:
            self.total_data_transfer = data_transfer
        if uptime is not None:
            self.system_uptime = uptime
        if error_rate is not None:
            self.error_rate = error_rate
        if performance_score is not None:
            self.performance_score = performance_score
        self.updated_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def create_or_update_current(cls, statistic_hour=None, **kwargs):
        """创建或更新当前统计数据"""
        today = date.today()
        current_hour = datetime.now().hour if statistic_hour is None else statistic_hour
        
        # 尝试获取现有记录
        if statistic_hour is not None:
            stats = cls.get_by_date_and_hour(today, current_hour)
        else:
            stats = cls.get_by_date(today)
        
        if stats:
            # 更新现有统计
            for key, value in kwargs.items():
                if hasattr(stats, key):
                    setattr(stats, key, value)
            stats.updated_at = datetime.utcnow()
        else:
            # 创建新统计
            stats = cls(
                statistic_date=today,
                statistic_hour=current_hour if statistic_hour is not None else None,
                **kwargs
            )
        
        stats.save()
        return stats
    
    @classmethod
    def get_performance_summary(cls, days=7):
        """获取性能概要"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        stats_list = cls.get_date_range_stats(start_date, end_date)
        
        if not stats_list:
            return {}
        
        total_operations = sum(s.total_operations for s in stats_list)
        total_failed = sum(s.failed_operations for s in stats_list)
        total_uptime = sum(s.system_uptime for s in stats_list)
        avg_response_time = sum(s.average_response_time for s in stats_list if s.average_response_time) / len([s for s in stats_list if s.average_response_time])
        avg_performance_score = sum(s.performance_score for s in stats_list if s.performance_score) / len([s for s in stats_list if s.performance_score])
        
        return {
            'period_days': days,
            'total_operations': total_operations,
            'total_failed_operations': total_failed,
            'success_rate': round(((total_operations - total_failed) / total_operations * 100) if total_operations > 0 else 100, 2),
            'total_uptime': total_uptime,
            'average_response_time': round(avg_response_time, 2) if avg_response_time else 0,
            'average_performance_score': round(avg_performance_score, 2) if avg_performance_score else 100,
            'total_data_transfer': sum(s.total_data_transfer for s in stats_list),
            'peak_concurrent_users': max(s.peak_concurrent_users for s in stats_list),
            'average_device_online_rate': round(sum(s.get_device_online_rate() for s in stats_list) / len(stats_list), 2)
        }
    
    def get_device_online_rate(self):
        """获取设备在线率"""
        if self.total_devices == 0:
            return 0
        return round((self.total_online_devices / self.total_devices) * 100, 2)
    
    def get_device_error_rate(self):
        """获取设备错误率"""
        if self.total_devices == 0:
            return 0
        return round((self.total_error_devices / self.total_devices) * 100, 2)
    
    def get_operation_success_rate(self):
        """获取操作成功率"""
        if self.total_operations == 0:
            return 100
        success_operations = self.total_operations - self.failed_operations
        return round((success_operations / self.total_operations) * 100, 2)
    
    def get_user_activity_rate(self):
        """获取用户活跃率"""
        if self.total_users == 0:
            return 0
        return round((self.active_users / self.total_users) * 100, 2)
