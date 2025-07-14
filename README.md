# 宇树G1 EDU机器人管理系统

## 项目简介

宇树G1 EDU机器人管理系统是一个专为教育场景设计的机器人管理平台，提供设备管理、教育培训、自主导览、用户权限管理等功能。系统采用前后端分离架构，支持多用户角色管理和权限控制。

## 技术栈

### 后端
- **框架**: Flask 2.3.3
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0.23 + Flask-SQLAlchemy 3.0.5
- **数据库迁移**: Flask-Migrate 4.0.5
- **身份认证**: PyJWT 2.8.0
- **数据处理**: pandas 2.0.3, openpyxl 3.1.2
- **数据库连接**: PyMySQL 1.1.0
- **配置管理**: python-dotenv 1.0.0

### 前端
- **框架**: Vue 3.5.17
- **构建工具**: Vite 7.0.0
- **路由**: Vue Router 4.5.1
- **状态管理**: Pinia 3.0.3
- **HTTP客户端**: Axios 1.10.0
- **包管理**: pnpm

### 部署
- **容器化**: Docker + Docker Compose
- **数据库**: MySQL 8.0 容器
- **反向代理**: 支持容器网络

## 系统功能

### 核心模块

1. **系统仪表板**
   - 设备状态概览
   - 系统运行统计
   - 实时监控数据

2. **设备管理**
   - 机器人设备注册和配置
   - 设备状态监控（在线/离线/故障/维护）
   - 设备日志和诊断
   - 设备健康评分

3. **教育培训**
   - 课件资源管理
   - 课件分类和标签
   - AI平台集成配置
   - 教学模式设置
   - 语音和动作配置

4. **自主导览**
   - 导览路径规划
   - 导览点位管理
   - 导览模式配置

5. **机器人控制**
   - 远程控制界面
   - 实时状态监控
   - 指令发送和执行

6. **用户管理**
   - 多角色权限体系（管理员/操作员/查看者）
   - 用户账户管理
   - 登录认证和会话管理

7. **角色权限管理**
   - RBAC权限模型
   - 角色和权限配置
   - 菜单权限控制

8. **系统设置**
   - 系统参数配置
   - 日志管理
   - 数据备份和恢复

### 用户角色

- **管理员 (admin)**: 拥有所有权限，可以管理用户、设备、系统设置
- **操作员 (operator)**: 可以操作设备、管理课件、查看数据
- **查看者 (viewer)**: 只能查看数据，无法进行修改操作

## 项目结构

```
Robot-Management/
├── backend/                 # 后端服务
│   ├── app/                # Flask应用
│   │   ├── __init__.py     # 应用工厂
│   │   ├── auth.py         # 认证模块
│   │   ├── config/         # 配置文件
│   │   ├── models/         # 数据模型
│   │   │   ├── user.py     # 用户模型
│   │   │   ├── equipment.py # 设备模型
│   │   │   ├── courseware.py # 课件模型
│   │   │   └── ...
│   │   └── routes/         # API路由
│   ├── db/                 # 数据库脚本
│   │   └── init.sql        # 初始化SQL
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt    # Python依赖
│   ├── run.py             # 启动文件
│   └── Dockerfile         # Docker配置
├── front/                  # 前端应用
│   ├── src/
│   │   ├── components/     # 公共组件
│   │   ├── views/          # 页面组件
│   │   │   ├── SystemDashboard/     # 系统仪表板
│   │   │   ├── EquipmentManagement/ # 设备管理
│   │   │   ├── EducationTraining/   # 教育培训
│   │   │   ├── SelfGuidedNavigation/ # 自主导览
│   │   │   ├── RobotControl/        # 机器人控制
│   │   │   ├── AccountManagement/   # 账户管理
│   │   │   ├── RoleManagement/      # 角色管理
│   │   │   └── SystemSettings/      # 系统设置
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   ├── api/           # API接口
│   │   └── utils/         # 工具函数
│   ├── package.json       # 前端依赖
│   └── Dockerfile         # Docker配置
├── database_schema.sql     # 完整数据库结构
├── docker-compose.yml      # Docker编排
└── README.md              # 项目文档
```

## 快速开始

### 环境要求

- Docker 20.0+
- Docker Compose 2.0+
- Node.js 16+ (本地开发)
- Python 3.8+ (本地开发)
- MySQL 8.0+ (本地开发)

### 使用Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd Robot-Management
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **初始化数据库**
   ```bash
   # 进入后端容器
   docker exec -it yushu_backend bash
   
   # 初始化数据库和创建默认用户
   flask init
   ```

4. **访问系统**
   - 前端地址: http://localhost:3000
   - 后端API: http://localhost:5001
   - 数据库: localhost:3306

### 本地开发部署

#### 后端设置

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置数据库**
   - 创建MySQL数据库 `g1_edu`
   - 修改配置文件中的数据库连接信息

3. **初始化数据库**
   ```bash
   flask init
   ```

4. **启动后端服务**
   ```bash
   python run.py
   ```

#### 前端设置

1. **安装依赖**
   ```bash
   cd front
   pnpm install
   ```

2. **启动开发服务器**
   ```bash
   pnpm dev
   ```

## 默认账户

系统初始化后会创建以下默认账户：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 系统管理员，拥有所有权限 |
| operator | operator123 | 操作员 | 设备操作员，可操作设备和课件 |
| viewer | viewer123 | 查看者 | 只读用户，仅可查看数据 |

> ⚠️ **安全提示**: 生产环境部署前请务必修改默认密码！

## API文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息

### 设备管理
- `GET /api/equipment` - 获取设备列表
- `POST /api/equipment` - 创建设备
- `PUT /api/equipment/{id}` - 更新设备
- `DELETE /api/equipment/{id}` - 删除设备

### 用户管理
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `PUT /api/users/{id}` - 更新用户
- `DELETE /api/users/{id}` - 删除用户

## 数据库设计

系统采用MySQL数据库，主要数据表包括：

- `users` - 用户账户表
- `equipment` - 设备管理表
- `courseware` - 课件资源表
- `courseware_categories` - 课件分类表
- `education_settings` - 教育培训配置表
- `navigation_settings` - 导览系统配置表
- `roles` - 角色表
- `permissions` - 权限表
- `operation_logs` - 操作日志表

详细的数据库结构请参考 `database_schema.sql` 文件。

## 配置说明

### 环境变量

后端支持以下环境变量配置：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=g1_edu

# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key

# JWT配置
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### Docker配置

`docker-compose.yml` 文件包含了完整的服务编排配置，包括：
- MySQL数据库服务
- Python后端服务
- Node.js前端服务
- 网络和数据卷配置

## 开发指南

### 后端开发

1. **添加新的API接口**
   - 在 `app/routes/` 目录下创建新的路由文件
   - 在 `app/__init__.py` 中注册新的蓝图

2. **添加新的数据模型**
   - 在 `app/models/` 目录下创建模型文件
   - 使用Flask-Migrate生成和应用数据库迁移

3. **数据库迁移**
   ```bash
   flask db migrate -m "描述信息"
   flask db upgrade
   ```

### 前端开发

1. **添加新页面**
   - 在 `src/views/` 目录下创建页面组件
   - 在 `src/router/index.js` 中添加路由配置

2. **添加新组件**
   - 在 `src/components/` 目录下创建公共组件
   - 在需要的页面中引入和使用

3. **状态管理**
   - 使用Pinia进行状态管理
   - 在 `src/stores/` 目录下创建store文件

## 部署说明

### 生产环境部署

1. **环境准备**
   - 确保服务器安装了Docker和Docker Compose
   - 配置防火墙规则，开放必要端口

2. **配置修改**
   - 修改 `docker-compose.yml` 中的环境变量
   - 设置强密码和安全的密钥
   - 配置数据卷持久化

3. **启动服务**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **数据备份**
   - 定期备份MySQL数据
   - 备份上传的课件文件

### 监控和维护

- 监控容器运行状态
- 定期查看应用日志
- 监控数据库性能
- 定期更新系统和依赖

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否正常运行
   - 验证数据库连接配置
   - 确认网络连通性

2. **前端无法访问后端API**
   - 检查后端服务是否启动
   - 验证API地址配置
   - 检查跨域设置

3. **用户无法登录**
   - 确认用户账户状态
   - 检查密码是否正确
   - 验证JWT配置

### 日志查看

```bash
# 查看容器日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql

# 实时查看日志
docker-compose logs -f backend
```

---

**宇树G1 EDU机器人管理系统** - 让机器人教育更简单、更智能！