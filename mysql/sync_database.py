#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宇树G1 EDU机器人管理系统 - 数据库同步脚本
功能：支持远程数据库同步到本地
作者：系统管理员
创建时间：2025-01-03
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Optional, List

try:
    import pymysql
except ImportError:
    print("错误：请先安装 pymysql 库")
    print("安装命令：pip install pymysql")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_database.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': '***',  # 隐藏密码
            'database': self.database
        }

class DatabaseSyncer:
    """数据库同步器"""
    
    def __init__(self, source_config: DatabaseConfig, target_config: DatabaseConfig):
        self.source_config = source_config
        self.target_config = target_config
        self.source_conn = None
        self.target_conn = None
    
    def connect_databases(self) -> bool:
        """连接源数据库和目标数据库"""
        try:
            # 连接源数据库
            logger.info(f"正在连接源数据库: {self.source_config.host}:{self.source_config.port}")
            self.source_conn = pymysql.connect(
                host=self.source_config.host,
                port=self.source_config.port,
                user=self.source_config.username,
                password=self.source_config.password,
                database=self.source_config.database,
                charset='utf8mb4',
                autocommit=False
            )
            logger.info("源数据库连接成功")
            
            # 连接目标数据库
            logger.info(f"正在连接目标数据库: {self.target_config.host}:{self.target_config.port}")
            self.target_conn = pymysql.connect(
                host=self.target_config.host,
                port=self.target_config.port,
                user=self.target_config.username,
                password=self.target_config.password,
                database=self.target_config.database,
                charset='utf8mb4',
                autocommit=False
            )
            logger.info("目标数据库连接成功")
            
            return True
            
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False
    
    def get_table_list(self, connection) -> List[str]:
        """获取数据库表列表"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                return tables
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            return []
    
    def get_table_structure(self, connection, table_name: str) -> str:
        """获取表结构"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                result = cursor.fetchone()
                return result[1] if result else ""
        except Exception as e:
            logger.error(f"获取表结构失败 {table_name}: {str(e)}")
            return ""
    
    def get_table_data(self, connection, table_name: str) -> List[tuple]:
        """获取表数据"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `{table_name}`")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"获取表数据失败 {table_name}: {str(e)}")
            return []
    
    def get_table_columns(self, connection, table_name: str) -> List[str]:
        """获取表字段列表"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = [row[0] for row in cursor.fetchall()]
                return columns
        except Exception as e:
            logger.error(f"获取表字段失败 {table_name}: {str(e)}")
            return []
    
    def drop_table_if_exists(self, connection, table_name: str) -> bool:
        """删除表（如果存在）"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                connection.commit()
                return True
        except Exception as e:
            logger.error(f"删除表失败 {table_name}: {str(e)}")
            return False
    
    def create_table(self, connection, create_sql: str) -> bool:
        """创建表"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(create_sql)
                connection.commit()
                return True
        except Exception as e:
            logger.error(f"创建表失败: {str(e)}")
            return False
    
    def insert_data(self, connection, table_name: str, columns: List[str], data: List[tuple]) -> bool:
        """插入数据"""
        if not data:
            return True
            
        try:
            with connection.cursor() as cursor:
                # 构建插入SQL
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join([f'`{col}`' for col in columns])
                sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
                
                # 批量插入
                cursor.executemany(sql, data)
                connection.commit()
                return True
        except Exception as e:
            logger.error(f"插入数据失败 {table_name}: {str(e)}")
            connection.rollback()
            return False
    
    def sync_table(self, table_name: str, drop_target: bool = True) -> bool:
        """同步单个表"""
        logger.info(f"开始同步表: {table_name}")
        
        try:
            # 获取源表结构
            create_sql = self.get_table_structure(self.source_conn, table_name)
            if not create_sql:
                logger.error(f"无法获取表结构: {table_name}")
                return False
            
            # 删除目标表（如果需要）
            if drop_target:
                if not self.drop_table_if_exists(self.target_conn, table_name):
                    logger.error(f"删除目标表失败: {table_name}")
                    return False
            
            # 创建目标表
            if not self.create_table(self.target_conn, create_sql):
                logger.error(f"创建目标表失败: {table_name}")
                return False
            
            # 获取源表数据
            data = self.get_table_data(self.source_conn, table_name)
            if not data:
                logger.info(f"表 {table_name} 无数据，跳过数据同步")
                return True
            
            # 获取表字段
            columns = self.get_table_columns(self.source_conn, table_name)
            if not columns:
                logger.error(f"无法获取表字段: {table_name}")
                return False
            
            # 插入数据到目标表
            if not self.insert_data(self.target_conn, table_name, columns, data):
                logger.error(f"插入数据失败: {table_name}")
                return False
            
            logger.info(f"表 {table_name} 同步完成，共同步 {len(data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步表失败 {table_name}: {str(e)}")
            return False
    
    def sync_all_tables(self, exclude_tables: List[str] = None, include_tables: List[str] = None) -> bool:
        """同步所有表"""
        if exclude_tables is None:
            exclude_tables = []
        
        # 获取源数据库表列表
        source_tables = self.get_table_list(self.source_conn)
        if not source_tables:
            logger.error("源数据库无表或获取表列表失败")
            return False
        
        # 过滤表列表
        tables_to_sync = []
        for table in source_tables:
            if table in exclude_tables:
                logger.info(f"跳过表: {table} (在排除列表中)")
                continue
            
            if include_tables and table not in include_tables:
                logger.info(f"跳过表: {table} (不在包含列表中)")
                continue
            
            tables_to_sync.append(table)
        
        logger.info(f"准备同步 {len(tables_to_sync)} 个表: {', '.join(tables_to_sync)}")
        
        # 同步表
        success_count = 0
        for table in tables_to_sync:
            if self.sync_table(table):
                success_count += 1
            else:
                logger.error(f"表 {table} 同步失败")
        
        logger.info(f"同步完成: {success_count}/{len(tables_to_sync)} 个表同步成功")
        return success_count == len(tables_to_sync)
    
    def close_connections(self):
        """关闭数据库连接"""
        if self.source_conn:
            self.source_conn.close()
            logger.info("源数据库连接已关闭")
        
        if self.target_conn:
            self.target_conn.close()
            logger.info("目标数据库连接已关闭")

def load_config_from_file(config_file: str) -> Dict:
    """从配置文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {str(e)}")
        return {}

def create_sample_config(config_file: str):
    """创建示例配置文件"""
    sample_config = {
        "source": {
            "host": "192.168.1.100",
            "port": 3306,
            "username": "root",
            "password": "your_password",
            "database": "g1_edu_system"
        },
        "target": {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": "local_password",
            "database": "g1_edu_system_local"
        },
        "sync_options": {
            "exclude_tables": ["user_sessions", "login_attempts"],
            "include_tables": [],
            "drop_target_tables": True
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=4, ensure_ascii=False)
        logger.info(f"示例配置文件已创建: {config_file}")
        return True
    except Exception as e:
        logger.error(f"创建配置文件失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='宇树G1 EDU机器人管理系统 - 数据库同步工具')
    parser.add_argument('--config', '-c', default='sync_config.json', help='配置文件路径')
    parser.add_argument('--create-config', action='store_true', help='创建示例配置文件')
    parser.add_argument('--source-host', help='源数据库主机')
    parser.add_argument('--source-port', type=int, default=3306, help='源数据库端口')
    parser.add_argument('--source-user', help='源数据库用户名')
    parser.add_argument('--source-password', help='源数据库密码')
    parser.add_argument('--source-database', help='源数据库名')
    parser.add_argument('--target-host', default='localhost', help='目标数据库主机')
    parser.add_argument('--target-port', type=int, default=3306, help='目标数据库端口')
    parser.add_argument('--target-user', help='目标数据库用户名')
    parser.add_argument('--target-password', help='目标数据库密码')
    parser.add_argument('--target-database', help='目标数据库名')
    parser.add_argument('--exclude-tables', nargs='*', help='排除的表名列表')
    parser.add_argument('--include-tables', nargs='*', help='包含的表名列表')
    parser.add_argument('--no-drop', action='store_true', help='不删除目标表')
    
    args = parser.parse_args()
    
    # 创建示例配置文件
    if args.create_config:
        if create_sample_config(args.config):
            print(f"示例配置文件已创建: {args.config}")
            print("请编辑配置文件后重新运行同步命令")
        return
    
    # 加载配置
    config = {}
    if os.path.exists(args.config):
        config = load_config_from_file(args.config)
        logger.info(f"已加载配置文件: {args.config}")
    
    # 命令行参数优先级更高
    source_config = DatabaseConfig(
        host=args.source_host or config.get('source', {}).get('host'),
        port=args.source_port or config.get('source', {}).get('port', 3306),
        username=args.source_user or config.get('source', {}).get('username'),
        password=args.source_password or config.get('source', {}).get('password'),
        database=args.source_database or config.get('source', {}).get('database')
    )
    
    target_config = DatabaseConfig(
        host=args.target_host or config.get('target', {}).get('host', 'localhost'),
        port=args.target_port or config.get('target', {}).get('port', 3306),
        username=args.target_user or config.get('target', {}).get('username'),
        password=args.target_password or config.get('target', {}).get('password'),
        database=args.target_database or config.get('target', {}).get('database')
    )
    
    # 验证必要参数
    if not all([source_config.host, source_config.username, source_config.password, source_config.database]):
        logger.error("源数据库配置不完整，请提供主机、用户名、密码和数据库名")
        print("\n使用示例:")
        print("python sync_database.py --source-host 192.168.1.100 --source-user root --source-password password --source-database g1_edu_system --target-user root --target-password local_password --target-database g1_edu_local")
        print("\n或者创建配置文件:")
        print("python sync_database.py --create-config")
        return
    
    if not all([target_config.username, target_config.password, target_config.database]):
        logger.error("目标数据库配置不完整，请提供用户名、密码和数据库名")
        return
    
    # 获取同步选项
    sync_options = config.get('sync_options', {})
    exclude_tables = args.exclude_tables or sync_options.get('exclude_tables', [])
    include_tables = args.include_tables or sync_options.get('include_tables', [])
    drop_target = not args.no_drop and sync_options.get('drop_target_tables', True)
    
    logger.info("=" * 60)
    logger.info("开始数据库同步")
    logger.info(f"源数据库: {source_config.to_dict()}")
    logger.info(f"目标数据库: {target_config.to_dict()}")
    logger.info(f"排除表: {exclude_tables}")
    logger.info(f"包含表: {include_tables}")
    logger.info(f"删除目标表: {drop_target}")
    logger.info("=" * 60)
    
    # 创建同步器
    syncer = DatabaseSyncer(source_config, target_config)
    
    try:
        # 连接数据库
        if not syncer.connect_databases():
            logger.error("数据库连接失败，同步终止")
            return
        
        # 开始同步
        start_time = datetime.now()
        success = syncer.sync_all_tables(exclude_tables, include_tables)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f"数据库同步成功完成，耗时: {duration:.2f} 秒")
        else:
            logger.error(f"数据库同步部分失败，耗时: {duration:.2f} 秒")
        
    except KeyboardInterrupt:
        logger.info("用户中断同步操作")
    except Exception as e:
        logger.error(f"同步过程中发生错误: {str(e)}")
    finally:
        # 关闭连接
        syncer.close_connections()
        logger.info("数据库同步操作结束")

if __name__ == '__main__':
    main()