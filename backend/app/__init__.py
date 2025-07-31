from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp)

    # 注册CLI命令
    register_cli_commands(app)

    return app


def register_cli_commands(app):
    """注册CLI命令"""

    @app.cli.command()
    def init():
        """初始化数据库并创建默认管理员用户"""
        from app.models.user import User
        from app.models.equipment import Equipment
        from app.models.courseware_category import CoursewareCategory

        # 创建所有表
        db.create_all()
        print('✓ 数据库表创建完成')

        # 检查是否已存在admin用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # 创建默认管理员用户
            admin_user = User(
                username='admin',
                real_name='System Admin',
                email='admin@system.com',
                role='admin',
                status=True
            )
            admin_user.set_password('admin123')
            admin_user.save()
            print('✓ 默认管理员用户创建完成 (admin/admin123)')
        else:
            print('✓ 管理员用户已存在')

        # 创建默认设备（如果不存在）
        if Equipment.query.count() == 0:
            default_equipment = Equipment(
                id='G1-EDU-001',
                location='默认教室',
                status='offline',
                ip_address='192.168.1.100',
                usage_rate='0%'
            )
            default_equipment.save()
            print('✓ 默认设备创建完成 (G1-EDU-001)')

        # 创建默认课件分类（如果不存在）
        if CoursewareCategory.query.count() == 0:
            categories = [
                {
                    'name': '基础编程',
                    'description': '编程入门和基础概念课程',
                    'sort_order': 1
                },
                {
                    'name': '机器人控制',
                    'description': '机器人动作和控制相关课程',
                    'sort_order': 2
                },
                {
                    'name': '人工智能',
                    'description': 'AI和机器学习基础课程',
                    'sort_order': 3
                }
            ]

            for cat_data in categories:
                category = CoursewareCategory(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    sort_order=cat_data['sort_order'],
                    is_active=True
                )
                category.save()

            print('✓ 默认课件分类创建完成')

        print('✓ 数据库初始化完成！')
        print('')
        print('登录信息:')
        print('  用户名: admin')
        print('  密码: admin123')
        print('  角色: 管理员')

    @app.cli.command()
    def reset_admin():
        """重置默认管理员用户密码"""
        from app.models.user import User

        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            admin_user.set_password('admin123')
            admin_user.save()
            print('✓ 管理员密码重置完成')
            print('')
            print('登录信息:')
            print('  用户名: admin')
            print('  密码: admin123')
        else:
            print('✗ 未找到admin用户，请先运行 flask init')

    @app.cli.command()
    def create_user():
        """创建测试用户"""
        from app.models.user import User

        # 创建操作员用户
        if not User.query.filter_by(username='operator').first():
            operator_user = User(
                username='operator',
                real_name='系统操作员',
                email='operator@system.com',
                role='operator',
                status=True
            )
            operator_user.set_password('operator123')
            operator_user.save()
            print('✓ 操作员用户创建完成 (operator/operator123)')

        # 创建查看者用户
        if not User.query.filter_by(username='viewer').first():
            viewer_user = User(
                username='viewer',
                real_name='系统查看者',
                email='viewer@system.com',
                role='viewer',
                status=True
            )
            viewer_user.set_password('viewer123')
            viewer_user.save()
            print('✓ 查看者用户创建完成 (viewer/viewer123)')

        print('✓ 测试用户创建完成！')
