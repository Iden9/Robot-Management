from flask import request, jsonify
from functools import wraps
import jwt
import os
from app.models.result import Result
from app.models.user import User

def require_auth(f):
    """
    权限验证装饰器
    验证请求头中的token，如果验证通过则将当前用户对象传递给被装饰的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # 如果没有Token
        if not token:
            return jsonify(Result.unauthorized(message="缺少Token").to_dict())
        
        try:
            # 解码Token
            data = jwt.decode(
                token, 
                os.getenv('SECRET_KEY', 'dev_key'),
                algorithms=["HS256"]
            )
            # 获取用户
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify(Result.unauthorized(message="无效的Token").to_dict())
                
        except jwt.ExpiredSignatureError:
            return jsonify(Result.unauthorized(message="Token已过期").to_dict())
        except Exception:
            return jsonify(Result.unauthorized(message="无效的Token").to_dict())
            
        # 将用户信息传递给被装饰的函数
        return f(current_user, *args, **kwargs)

    return decorated

def require_role(allowed_roles):
    """
    角色权限验证装饰器
    验证用户是否具有指定角色的权限
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # 获取Token
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

            # 如果没有Token
            if not token:
                return jsonify(Result.unauthorized(message="缺少Token").to_dict())

            try:
                # 解码Token
                data = jwt.decode(
                    token,
                    os.getenv('SECRET_KEY', 'dev_key'),
                    algorithms=["HS256"]
                )
                # 获取用户
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    return jsonify(Result.unauthorized(message="无效的Token").to_dict())

                # 检查用户状态
                if not current_user.status:
                    return jsonify(Result.forbidden(message="账户已被禁用").to_dict())

                # 检查角色权限
                if current_user.role not in allowed_roles:
                    return jsonify(Result.forbidden(message="权限不足").to_dict())

            except jwt.ExpiredSignatureError:
                return jsonify(Result.unauthorized(message="Token已过期").to_dict())
            except Exception:
                return jsonify(Result.unauthorized(message="无效的Token").to_dict())

            # 将用户信息传递给被装饰的函数
            return f(current_user, *args, **kwargs)

        return decorated
    return decorator

def require_permission(permission_code):
    """
    权限验证装饰器
    验证用户是否具有指定权限
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # 获取Token
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

            # 如果没有Token
            if not token:
                return jsonify(Result.unauthorized(message="缺少Token").to_dict())

            try:
                # 解码Token
                data = jwt.decode(
                    token,
                    os.getenv('SECRET_KEY', 'dev_key'),
                    algorithms=["HS256"]
                )
                # 获取用户
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    return jsonify(Result.unauthorized(message="无效的Token").to_dict())

                # 检查用户状态
                if not current_user.status:
                    return jsonify(Result.forbidden(message="账户已被禁用").to_dict())

                # 检查权限
                if not current_user.has_permission(permission_code):
                    return jsonify(Result.forbidden(message=f"缺少权限: {permission_code}").to_dict())

            except jwt.ExpiredSignatureError:
                return jsonify(Result.unauthorized(message="Token已过期").to_dict())
            except Exception:
                return jsonify(Result.unauthorized(message="无效的Token").to_dict())

            # 将用户信息传递给被装饰的函数
            return f(current_user, *args, **kwargs)

        return decorated
    return decorator

def verify_token(token):
    """
    验证token并返回用户对象
    """
    try:
        # 解码Token
        data = jwt.decode(
            token,
            os.getenv('SECRET_KEY', 'dev_key'),
            algorithms=["HS256"]
        )
        # 获取用户
        current_user = User.query.get(data['user_id'])
        if not current_user or not current_user.status:
            return None
        return current_user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        return None