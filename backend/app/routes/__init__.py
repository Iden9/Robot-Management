from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入所有API路由
from .auth_routes import auth_bp
from .user_routes import user_bp
from .equipment_routes import equipment_bp
from .courseware_routes import courseware_bp
from .navigation_routes import navigation_bp
from .education_routes import education_bp
from .system_routes import system_bp
from .dashboard_routes import dashboard_bp
from .log_routes import log_bp
from .role_routes import role_bp
from .permission_routes import permission_bp
from .menu_routes import menu_bp

# 注册所有蓝图
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(equipment_bp, url_prefix='/equipment')
api_bp.register_blueprint(courseware_bp, url_prefix='/courseware')
api_bp.register_blueprint(navigation_bp, url_prefix='/navigation')
api_bp.register_blueprint(education_bp, url_prefix='/education')
api_bp.register_blueprint(system_bp, url_prefix='/system')
api_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
api_bp.register_blueprint(log_bp, url_prefix='/logs')
api_bp.register_blueprint(role_bp, url_prefix='/roles')
api_bp.register_blueprint(permission_bp, url_prefix='/permissions')
api_bp.register_blueprint(menu_bp, url_prefix='/menus')

__all__ = ['api_bp']