from flask import request, jsonify, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, OperationLog, UserSession
from app.models.result import Result
from app.auth import require_auth, require_role
from app import db
import jwt
import datetime
import os

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data or not data.get('username') or not data.get('password'):
            return jsonify(Result.error(message="用户名和密码不能为空", code=400).to_dict())
        
        # 检查用户是否存在
        user = User.get_by_username(data['username'])
        if not user:
            return jsonify(Result.error(message="用户不存在", code=404).to_dict())
        
        # 检查用户状态
        if not user.status:
            return jsonify(Result.error(message="账户已被禁用", code=403).to_dict())
        
        # 检查密码 (兼容新旧密码字段)
        password_field = user.password_hash if hasattr(user, 'password_hash') and user.password_hash else user.password
        if not user.check_password(data['password']):
            return jsonify(Result.error(message="密码错误", code=401).to_dict())
        
        # 不再需要验证角色选择，系统会自动使用用户的实际角色
        
        # 更新最后登录时间和登录次数
        user.last_login = datetime.datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        user.save()
        
        # 创建用户会话
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        session = UserSession.create_session(
            user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # 记录登录日志
        OperationLog.log_user_login(
            user_id=user.id, 
            ip_address=client_ip
        )
        
        # 生成JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'session_id': session.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            os.getenv('SECRET_KEY', 'dev_key'),
            algorithm="HS256"
        )
        
        return jsonify(Result.success(
            message="登录成功",
            data={
                "token": token,
                "user": user.to_dict(),
                "session": session.to_dict(),
                "permissions": user.get_permissions()
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"登录失败: {str(e)}").to_dict())

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout(current_user):
    """用户登出"""
    try:
        # 记录登出日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.log_user_logout(current_user.id, client_ip)
        
        return jsonify(Result.success(message="登出成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"登出失败: {str(e)}").to_dict())

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """获取当前用户信息"""
    try:
        return jsonify(Result.success(
            message="获取用户信息成功",
            data={
                "user": current_user.to_dict(),
                "permissions": current_user.get_permissions()
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取用户信息失败: {str(e)}").to_dict())

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password(current_user):
    """修改密码"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify(Result.error(message="旧密码和新密码不能为空", code=400).to_dict())
        
        # 验证旧密码
        if not check_password_hash(current_user.password, data['old_password']):
            return jsonify(Result.error(message="旧密码错误", code=401).to_dict())
        
        # 更新密码
        from werkzeug.security import generate_password_hash
        current_user.password = generate_password_hash(data['new_password'], method='pbkdf2:sha256')
        current_user.save()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="修改密码",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="密码修改成功").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"密码修改失败: {str(e)}").to_dict())

@auth_bp.route('/sessions', methods=['GET'])
@require_auth
def get_user_sessions(current_user):
    """获取用户活跃会话列表"""
    try:
        sessions = UserSession.get_user_sessions(current_user.id, active_only=True)
        sessions_data = [session.to_dict() for session in sessions]
        
        return jsonify(Result.success(
            message="获取会话列表成功",
            data=sessions_data
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"获取会话列表失败: {str(e)}").to_dict())

@auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
def terminate_session(current_user, session_id):
    """终止指定会话"""
    try:
        session = UserSession.get_by_id(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify(Result.error(message="会话不存在或无权限", code=404).to_dict())
        
        session.invalidate()
        
        # 记录操作日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=current_user.id,
            action="终止会话",
            details=f"会话ID: {session_id}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(message="会话已终止").to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"终止会话失败: {str(e)}").to_dict())

@auth_bp.route('/sessions/cleanup', methods=['POST'])
@require_auth
def cleanup_expired_sessions(current_user):
    """清理过期会话"""
    try:
        count = UserSession.cleanup_expired_sessions()
        
        return jsonify(Result.success(
            message=f"已清理 {count} 个过期会话",
            data={"count": count}
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"清理会话失败: {str(e)}").to_dict())

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """验证JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify(Result.error(message="Token不能为空", code=401).to_dict())
        
        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY', 'dev_key'), algorithms=["HS256"])
            
            # 检查用户是否存在
            user = User.get_by_id(payload['user_id'])
            if not user or not user.status:
                return jsonify(Result.error(message="用户不存在或已被禁用", code=401).to_dict())
            
            # 检查会话是否有效
            if 'session_id' in payload:
                session = UserSession.get_active_session(payload['session_id'])
                if not session:
                    return jsonify(Result.error(message="会话已过期", code=401).to_dict())
                
                # 更新会话活动时间
                session.update_activity()
            
            return jsonify(Result.success(
                message="Token验证成功",
                data={
                    "user": user.to_dict(),
                    "permissions": user.get_permissions()
                }
            ).to_dict())
            
        except jwt.ExpiredSignatureError:
            return jsonify(Result.error(message="Token已过期", code=401).to_dict())
        except jwt.InvalidTokenError:
            return jsonify(Result.error(message="Token无效", code=401).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"Token验证失败: {str(e)}", code=401).to_dict())

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 数据验证
        required_fields = ['username', 'password', 'real_name', 'email']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify(Result.error(message=f"{field}不能为空", code=400).to_dict())
        
        # 检查用户名是否已存在
        if User.get_by_username(data['username']):
            return jsonify(Result.error(message="用户名已存在", code=400).to_dict())
        
        # 检查邮箱是否已存在
        if User.get_by_email(data['email']):
            return jsonify(Result.error(message="邮箱已存在", code=400).to_dict())
        
        # 创建新用户
        user = User(
            username=data['username'],
            real_name=data['real_name'],
            email=data['email'],
            phone=data.get('phone'),
            role='viewer',  # 默认角色为查看者
            status=True
        )
        user.set_password(data['password'])
        user.save()
        
        # 记录注册日志
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        OperationLog.create_log(
            user_id=user.id,
            action="用户注册",
            details=f"用户名: {user.username}, 邮箱: {user.email}",
            ip_address=client_ip
        )
        
        return jsonify(Result.success(
            message="注册成功",
            data={
                "user": user.to_dict()
            }
        ).to_dict())
        
    except Exception as e:
        return jsonify(Result.error(message=f"注册失败: {str(e)}").to_dict())
