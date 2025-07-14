# 宇树G1 EDU机器人管理系统 - 后端

## 项目简介

本项目是宇树G1 EDU机器人管理系统的后端服务，基于 **Python Flask** 框架开发，旨在提供稳定、高效的API接口，支持前端界面的各项功能，包括设备管理、教育培训、自主导览、机器人控制、用户与权限管理、系统设置以及数据统计等。

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: MySQL (通过 SQLAlchemy 2.0.23 ORM)
- **数据库连接**: PyMySQL 1.1.0
- **认证**: JWT (PyJWT 2.8.0)
- **数据库迁移**: Flask-Migrate 4.0.5
- **数据处理**: pandas 2.0.3, openpyxl 3.1.2
- **配置管理**: python-dotenv 1.0.0
- **容器化**: Docker

## 项目结构

```
backend/
├── app/                          # Flask 应用核心目录
│   ├── __init__.py               # 应用初始化，注册蓝图，配置数据库
│   ├── auth.py                   # 认证相关逻辑，JWT处理
│   ├── config/                   # 配置文件
│   │   └── __init__.py           # 数据库配置、密钥等
│   ├── models/                   # 数据库模型定义 (SQLAlchemy ORM)
│   │   ├── __init__.py           # 模型导入汇总
│   │   ├── user.py               # 用户模型
│   │   ├── user_session.py       # 用户会话模型
│   │   ├── role.py               # 角色模型
│   │   ├── permission.py         # 权限模型
│   │   ├── menu.py               # 菜单模型
│   │   ├── equipment.py          # 设备模型
│   │   ├── equipment_log.py      # 设备日志模型
│   │   ├── equipment_status_history.py # 设备状态历史模型
│   │   ├── courseware.py         # 课件模型
│   │   ├── courseware_category.py# 课件分类模型
│   │   ├── courseware_usage.py   # 课件使用记录模型
│   │   ├── education_settings.py # 教育设置模型
│   │   ├── navigation_settings.py# 导航设置模型
│   │   ├── navigation_point.py   # 导航点位模型
│   │   ├── operation_log.py      # 操作日志模型
│   │   ├── system_settings.py    # 系统设置模型
│   │   ├── dashboard_statistics.py # 看板统计模型
│   │   └── result.py             # API返回结果封装
│   └── routes/                   # API 路由定义 (蓝图)
│       ├── __init__.py           # 注册所有路由蓝图
│       ├── auth_routes.py        # 认证相关API (登录、注册)
│       ├── user_routes.py        # 用户管理API
│       ├── equipment_routes.py   # 设备管理API
│       ├── courseware_routes.py  # 课件管理API
│       ├── navigation_routes.py  # 导航设置API
│       ├── education_routes.py   # 教育模块API
│       ├── system_routes.py      # 系统设置API
│       ├── dashboard_routes.py   # 系统看板API
│       ├── log_routes.py         # 日志管理API
│       ├── role_routes.py        # 角色管理API
│       ├── permission_routes.py  # 权限管理API
│       └── menu_routes.py        # 菜单管理API
├── db/                           # 数据库相关文件
│   └── init.sql                  # 数据库初始化SQL脚本
├── migrations/                   # 数据库迁移文件 (Alembic)
├── init_rbac.py                  # RBAC初始化脚本 (角色、权限、菜单)
├── requirements.txt              # Python 依赖列表
├── run.py                        # Flask 应用启动文件
├── .env.example                  # 环境变量配置文件示例
├── Dockerfile                    # Docker 容器化配置
├── .dockerignore                 # Docker 忽略文件
└── .gitignore                    # Git 忽略文件
```

## 功能模块

### 核心功能
- **用户管理**: 用户注册、登录、权限控制
- **设备管理**: 机器人设备的监控、控制和状态管理
- **课件管理**: 教育课件的上传、分类、使用统计
- **导航管理**: 机器人导航路径和点位设置
- **教育模块**: 教育内容和设置管理
- **系统看板**: 实时数据统计和可视化
- **日志管理**: 操作日志和设备日志记录

### RBAC权限系统
- **角色管理**: 系统管理员、操作员、查看者等角色
- **权限管理**: 细粒度的API、菜单、按钮权限控制
- **菜单管理**: 动态菜单配置和权限绑定

## 安装与运行

### 1. 环境准备

确保您的系统已安装以下软件：

- **Python 3.9+**
- **MySQL 8.0+**
- **Git**

### 2. 克隆项目

```bash
git clone <您的项目仓库地址>
cd Robot-Management/backend
```

### 3. 创建并激活虚拟环境

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后根据您的实际情况修改其中的配置项：

```bash
cp .env.example .env
```

编辑 `.env` 文件的关键配置：

```ini
# Flask应用配置
SECRET_KEY=your-secret-key-here-please-change-this

# 数据库配置
DATABASE_URL=mysql+pymysql://g1_user:your_password@localhost:3306/g1_edu_system
DB_HOST=localhost
DB_PORT=3306
DB_USER=g1_user
DB_PASSWORD=your_database_password
DB_NAME=g1_edu_system

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

### 6. 数据库初始化

首先，请确保您的MySQL服务器已启动，并创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS g1_edu_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'g1_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON g1_edu_system.* TO 'g1_user'@'localhost';
FLUSH PRIVILEGES;
```

然后，运行数据库迁移命令：

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. 初始化系统数据

运行以下命令初始化默认数据：

```bash
# 初始化数据库表和基础数据
flask init

# 初始化RBAC权限系统
python init_rbac.py

# 创建默认管理员用户 (用户名: admin, 密码: admin123)
flask create-user admin admin123 admin@example.com --role admin
```

### 8. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:5001` 启动。

## Docker 部署

### 构建镜像

```bash
docker build -t g1-edu-backend .
```

### 运行容器

```bash
docker run -d \
  --name g1-edu-backend \
  -p 5001:5001 \
  --env-file .env \
  g1-edu-backend
```

## API 接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新Token

### 用户管理
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `GET /api/users/{id}` - 获取用户详情
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户

### 设备管理
- `GET /api/equipment` - 获取设备列表
- `POST /api/equipment` - 添加设备
- `GET /api/equipment/{id}` - 获取设备详情
- `PUT /api/equipment/{id}` - 更新设备信息
- `DELETE /api/equipment/{id}` - 删除设备

### 课件管理
- `GET /api/courseware` - 获取课件列表
- `POST /api/courseware/upload` - 上传课件
- `GET /api/courseware/{id}` - 获取课件详情
- `PUT /api/courseware/{id}` - 更新课件信息
- `DELETE /api/courseware/{id}` - 删除课件

### 其他接口
- `GET /api/dashboard` - 系统看板数据
- `GET /api/logs` - 操作日志
- `GET /api/navigation` - 导航设置
- `GET /api/system` - 系统设置

## 数据库设计

主要数据库表包括：

- `users`: 用户信息表
- `user_sessions`: 用户会话表
- `roles`: 角色信息表
- `permissions`: 权限信息表
- `role_permissions`: 角色与权限关联表
- `menus`: 菜单信息表
- `equipment`: 设备信息表
- `equipment_logs`: 设备日志表
- `equipment_status_history`: 设备状态历史表
- `courseware`: 课件信息表
- `courseware_categories`: 课件分类表
- `courseware_usage`: 课件使用记录表
- `navigation_settings`: 导航设置表
- `navigation_points`: 导航点位表
- `operation_logs`: 操作日志表
- `system_settings`: 系统设置表
- `dashboard_statistics`: 看板统计数据表

详细的数据库结构请参考 `db/init.sql` 文件。

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask应用密钥 | 必须设置 |
| `DATABASE_URL` | 数据库连接URL | 必须设置 |
| `JWT_SECRET_KEY` | JWT密钥 | 必须设置 |
| `HOST` | 服务器地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 5000 |
| `LOG_LEVEL` | 日志级别 | INFO |
| `UPLOAD_FOLDER` | 文件上传目录 | uploads |

### Flask CLI 命令

```bash
# 初始化数据库和基础数据
flask init

# 重置管理员密码
flask reset-admin

# 创建用户
flask create-user <username> <password> <email> [--role <role_code>]
```

## 开发指南

### 代码结构

- **模型层** (`app/models/`): 使用SQLAlchemy ORM定义数据模型
- **路由层** (`app/routes/`): 使用Flask蓝图组织API路由
- **认证层** (`app/auth.py`): JWT认证和权限验证装饰器
- **配置层** (`app/config/`): 应用配置管理

### 权限控制

使用装饰器进行权限控制：

```python
from app.auth import require_auth, require_permission

@require_auth
@require_permission('user:list')
def get_users():
    # 需要登录且有用户查看权限
    pass
```

### 添加新功能

1. 在 `app/models/` 中定义数据模型
2. 在 `app/routes/` 中创建路由文件
3. 在 `app/routes/__init__.py` 中注册蓝图
4. 在 `init_rbac.py` 中添加相关权限

## 维护与故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `.env` 中的数据库配置
   - 确认MySQL服务正常运行
   - 验证数据库用户权限

2. **JWT Token 验证失败**
   - 检查 `JWT_SECRET_KEY` 配置
   - 确认Token未过期
   - 验证请求头格式

3. **权限验证失败**
   - 确认用户角色和权限配置
   - 检查权限代码是否正确
   - 验证RBAC初始化是否完成

### 日志查看

应用日志输出到控制台，可通过以下方式查看：

```bash
# 查看应用日志
tail -f logs/app.log

# 调整日志级别
export LOG_LEVEL=DEBUG
```

### 性能监控

- 数据库查询性能监控
- API响应时间统计
- 内存和CPU使用率监控

## 安全考虑

- JWT Token 有效期控制
- 密码加密存储
- SQL注入防护
- XSS攻击防护
- CORS跨域配置
- 文件上传安全检查

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如果您有任何问题或建议，请联系项目维护者。

---

**注意**: 请确保在生产环境中修改所有默认密钥和敏感配置信息。