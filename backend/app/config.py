import os
from dotenv import load_dotenv
from app.utils.config import get_config_value

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL数据库配置
    MYSQL_USER = get_config_value('mysql.user', 'root')
    MYSQL_PASSWORD = get_config_value('mysql.password', '123456')
    MYSQL_HOST = get_config_value('mysql.host', 'localhost')
    MYSQL_PORT = get_config_value('mysql.port', 3306)
    MYSQL_DATABASE = get_config_value('mysql.database', 'g1_edu')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JSON配置
    JSON_AS_ASCII = False