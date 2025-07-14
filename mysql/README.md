# 数据库同步工具使用说明

## 概述

这是一个专为宇树G1 EDU机器人管理系统设计的数据库同步工具，支持将远程MySQL数据库同步到本地数据库。

## 功能特性

- ✅ 支持远程到本地的完整数据库同步
- ✅ 支持表结构和数据的完整复制
- ✅ 支持排除/包含特定表的同步
- ✅ 支持配置文件和命令行参数两种配置方式
- ✅ 详细的日志记录和错误处理
- ✅ 批量数据插入优化
- ✅ 事务回滚保护

## 环境要求

- Python 3.6+
- PyMySQL 库

## 安装依赖

```bash
pip install pymysql
```

## 使用方法

### 方法一：使用配置文件（推荐）

1. **创建配置文件**
   ```bash
   python sync_database.py --create-config
   ```
   这将创建一个 `sync_config.json` 示例配置文件。

2. **编辑配置文件**
   ```json
   {
       "source": {
           "host": "192.168.1.100",
           "port": 3306,
           "username": "root",
           "password": "your_remote_password",
           "database": "g1_edu_system"
       },
       "target": {
           "host": "localhost",
           "port": 3306,
           "username": "root",
           "password": "your_local_password",
           "database": "g1_edu_system_local"
       },
       "sync_options": {
           "exclude_tables": ["user_sessions", "login_attempts"],
           "include_tables": [],
           "drop_target_tables": true
       }
   }
   ```

3. **执行同步**
   ```bash
   python sync_database.py
   ```
   或指定配置文件：
   ```bash
   python sync_database.py --config my_config.json
   ```

### 方法二：使用命令行参数

```bash
python sync_database.py \
    --source-host 192.168.1.100 \
    --source-user root \
    --source-password remote_password \
    --source-database g1_edu_system \
    --target-user root \
    --target-password local_password \
    --target-database g1_edu_system_local
```

## 命令行参数说明

### 基本参数
- `--config, -c`: 配置文件路径（默认：sync_config.json）
- `--create-config`: 创建示例配置文件

### 源数据库参数
- `--source-host`: 源数据库主机地址
- `--source-port`: 源数据库端口（默认：3306）
- `--source-user`: 源数据库用户名
- `--source-password`: 源数据库密码
- `--source-database`: 源数据库名

### 目标数据库参数
- `--target-host`: 目标数据库主机地址（默认：localhost）
- `--target-port`: 目标数据库端口（默认：3306）
- `--target-user`: 目标数据库用户名
- `--target-password`: 目标数据库密码
- `--target-database`: 目标数据库名

### 同步选项
- `--exclude-tables`: 排除的表名列表
- `--include-tables`: 包含的表名列表（如果指定，只同步这些表）
- `--no-drop`: 不删除目标表（默认会先删除再创建）

## 使用示例

### 示例1：完整同步
```bash
python sync_database.py \
    --source-host 192.168.1.100 \
    --source-user admin \
    --source-password admin123 \
    --source-database g1_edu_system \
    --target-user root \
    --target-password root123 \
    --target-database g1_edu_local
```

### 示例2：排除特定表
```bash
python sync_database.py \
    --source-host 192.168.1.100 \
    --source-user admin \
    --source-password admin123 \
    --source-database g1_edu_system \
    --target-user root \
    --target-password root123 \
    --target-database g1_edu_local \
    --exclude-tables user_sessions login_attempts
```

### 示例3：只同步特定表
```bash
python sync_database.py \
    --source-host 192.168.1.100 \
    --source-user admin \
    --source-password admin123 \
    --source-database g1_edu_system \
    --target-user root \
    --target-password root123 \
    --target-database g1_edu_local \
    --include-tables users equipment courseware
```

### 示例4：增量同步（不删除目标表）
```bash
python sync_database.py \
    --source-host 192.168.1.100 \
    --source-user admin \
    --source-password admin123 \
    --source-database g1_edu_system \
    --target-user root \
    --target-password root123 \
    --target-database g1_edu_local \
    --no-drop
```

## 配置文件详解

### source（源数据库配置）
- `host`: 远程数据库服务器IP地址
- `port`: 数据库端口，通常为3306
- `username`: 数据库用户名
- `password`: 数据库密码
- `database`: 要同步的数据库名

### target（目标数据库配置）
- `host`: 本地数据库服务器地址，通常为localhost
- `port`: 本地数据库端口
- `username`: 本地数据库用户名
- `password`: 本地数据库密码
- `database`: 目标数据库名

### sync_options（同步选项）
- `exclude_tables`: 要排除的表名数组
- `include_tables`: 要包含的表名数组（如果为空，则同步所有表）
- `drop_target_tables`: 是否在同步前删除目标表

## 日志文件

同步过程中的所有操作都会记录到 `sync_database.log` 文件中，包括：
- 连接状态
- 同步进度
- 错误信息
- 性能统计

## 注意事项

1. **数据安全**：同步操作会完全覆盖目标数据库的数据，请确保备份重要数据
2. **网络连接**：确保网络连接稳定，大数据量同步可能需要较长时间
3. **权限要求**：数据库用户需要有足够的权限进行表的创建、删除和数据插入操作
4. **字符编码**：脚本使用UTF-8编码，确保数据库支持中文字符
5. **事务处理**：每个表的同步都在独立事务中进行，失败时会自动回滚

## 故障排除

### 常见错误及解决方案

1. **连接失败**
   - 检查IP地址、端口、用户名、密码是否正确
   - 确认远程数据库允许外部连接
   - 检查防火墙设置

2. **权限不足**
   - 确保数据库用户有CREATE、DROP、INSERT、SELECT权限
   - 检查数据库级别的权限设置

3. **表同步失败**
   - 查看日志文件了解具体错误
   - 检查表结构是否兼容
   - 确认目标数据库有足够的存储空间

4. **数据插入失败**
   - 检查数据类型兼容性
   - 确认没有主键冲突
   - 检查外键约束

## 性能优化建议

1. **网络优化**：在网络条件良好的环境下进行同步
2. **分批同步**：对于大型数据库，可以使用include_tables分批同步
3. **排除不必要的表**：使用exclude_tables排除临时表和日志表
4. **本地网络**：尽量在同一局域网内进行同步操作


---

**版本**: 1.0.0  
**更新时间**: 2025-01-03  
**适用系统**: 宇树G1 EDU机器人管理系统