from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """为Flask shell提供上下文"""
    return {'db': db, 'User': User}

@app.route('/')
def index():
    return "启动成功"

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("数据库表创建完成")
    
    app.run(debug=True, host='0.0.0.0', port=5001)