# 玉树Web项目 Docker 部署指南

本项目包含前端（Vue.js + Vite）、后端（Flask）和数据库（MySQL）三个服务，使用 Docker Compose 进行容器化部署。

## 项目结构

```
Yushu_Web/
├── docker-compose.yml     # Docker Compose 配置文件
├── backend/               # Python Flask 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── front/                 # Vue.js 前端
│   ├── Dockerfile
│   ├── package.json
│   └── ...
└── g1_edu.sql            # 数据库初始化脚本
```

## 服务说明

### 1. MySQL 数据库服务
- **容器名**: yushu_mysql
- **端口**: 3306
- **数据库**: g1_edu
- **用户**: root / 密码: 123456
- **数据持久化**: mysql_data 卷

### 2. Python 后端服务
- **容器名**: yushu_backend
- **端口**: 5001
- **框架**: Flask
- **依赖**: MySQL 服务

### 3. Node.js 前端服务
- **容器名**: yushu_frontend
- **端口**: 3000
- **框架**: Vue.js + Vite
- **依赖**: 后端服务

## 快速开始

### 前置要求
- Docker
- Docker Compose

### 启动所有服务

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

### 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:5001
- **MySQL数据库**: localhost:3306

### 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs mysql

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec mysql mysql -u root -p
```

## 开发模式

项目配置为开发模式，支持热重载：

- **前端**: Vite 开发服务器，代码变更自动刷新
- **后端**: Flask 调试模式，代码变更自动重启
- **数据库**: 数据持久化到 Docker 卷

## 环境变量

后端服务支持以下环境变量配置：

- `MYSQL_HOST`: MySQL 主机地址（默认: mysql）
- `MYSQL_PORT`: MySQL 端口（默认: 3306）
- `MYSQL_USER`: MySQL 用户名（默认: root）
- `MYSQL_PASSWORD`: MySQL 密码（默认: 123456）
- `MYSQL_DATABASE`: 数据库名（默认: g1_edu）
- `FLASK_ENV`: Flask 环境（默认: development）

## 故障排除

### 1. 端口冲突
如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "3001:3000"  # 前端改为3001端口
  - "5002:5001"  # 后端改为5002端口
```

### 2. 数据库连接失败
确保 MySQL 服务完全启动后再启动后端服务：

```bash
# 先启动数据库
docker-compose up mysql

# 等待数据库就绪后启动其他服务
docker-compose up backend frontend
```

### 3. 前端无法访问后端API
检查前端的代理配置是否正确，确保 `vite.config.js` 中的代理指向正确的后端地址。

### 4. 清理和重置

```bash
# 停止所有容器并删除
docker-compose down

# 删除所有相关镜像
docker rmi $(docker images | grep yushu | awk '{print $3}')

# 删除数据卷（注意：会丢失数据库数据）
docker volume rm yushu_web_mysql_data

# 重新构建
docker-compose up --build
```

## 生产部署

生产环境部署时，建议：

1. 修改数据库密码
2. 设置合适的环境变量
3. 使用生产构建的前端
4. 配置反向代理（如 Nginx）
5. 启用 HTTPS
6. 配置日志收集
7. 设置健康检查

## 技术栈

- **前端**: Vue.js 3, Vite, Pinia, Vue Router, Axios
- **后端**: Flask, SQLAlchemy, PyMySQL, Flask-Migrate
- **数据库**: MySQL 8.0
- **容器化**: Docker, Docker Compose