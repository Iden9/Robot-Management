class Result:
    """通用返回结果类"""
    
    def __init__(self, code=200, message="success", data=None):
        """
        初始化返回结果
        :param code: 状态码，默认200表示成功
        :param message: 返回信息
        :param data: 返回的数据
        """
        self.code = code
        self.message = message
        self.data = data if data is not None else {}
    
    def to_dict(self):
        """
        将结果转换为字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
    
    @classmethod
    def success(cls, data=None, message="success"):
        """
        成功返回
        """
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, message="error", code=500, data=None):
        """
        错误返回
        """
        return cls(code=code, message=message, data=data)
    
    @classmethod
    def unauthorized(cls, message="unauthorized", data=None):
        """
        未授权返回
        """
        return cls(code=401, message=message, data=data)
    
    @classmethod
    def forbidden(cls, message="forbidden", data=None):
        """
        禁止访问返回
        """
        return cls(code=403, message=message, data=data)
    
    @classmethod
    def not_found(cls, message="not found", data=None):
        """
        资源不存在返回
        """
        return cls(code=404, message=message, data=data) 