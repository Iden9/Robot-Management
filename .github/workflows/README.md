# GitHub Actions 自动部署配置说明

## 概述

本项目使用GitHub Actions实现自动化部署到服务器 `8.153.175.16`。当代码推送到主分支时，会自动触发构建和部署流程。

## 部署架构

- **前端**: Vue.js应用构建后部署到Nginx静态文件目录
- **后端**: Flask应用作为systemd服务运行在5000端口
- **反向代理**: Nginx处理静态文件并代理API请求到后端
- **数据库**: MySQL（需要单独配置）

## 必需的GitHub Secrets配置

在GitHub仓库的 `Settings > Secrets and variables > Actions` 中添加以下secrets：

### 必需的Secrets

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `SERVER_HOST` | 服务器IP地址 | `8.153.175.16` |
| `SERVER_USER` | SSH登录用户名 | `ubuntu` 或 `root` |
| `SERVER_SSH_KEY` | SSH私钥内容 | 完整的私钥文件内容 |
| `SERVER_PORT` | SSH端口（可选） | `22`（默认值） |

### 如何获取SSH私钥

1. **生成SSH密钥对**（如果还没有）：
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@yourdomain.com"
   ```

2. **将公钥添加到服务器**：
   ```bash
   # 复制公钥到服务器
   ssh-copy-id -i ~/.ssh/id_rsa.pub user@8.153.175.16
   
   # 或者手动添加到服务器的 ~/.ssh/authorized_keys
   ```

3. **复制私钥内容**：
   ```bash
   cat ~/.ssh/id_rsa
   ```
   将完整输出（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）复制到GitHub Secrets中。

## 服务器预配置要求

在首次部署前，确保服务器已安装以下软件：

### 1. 基础软件
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nginx python3 python3-pip git

# CentOS/RHEL
sudo yum install -y nginx python3 python3-pip git
```

### 2. Python包管理
```bash
# 升级pip
python3 -m pip install --upgrade pip

# 安装虚拟环境（可选但推荐）
pip3 install virtualenv
```

### 3. MySQL数据库
```bash
# Ubuntu/Debian
sudo apt install -y mysql-server

# CentOS/RHEL
sudo yum install -y mysql-server

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

### 4. 创建数据库和用户
```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE g1_edu_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'g1_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- 授权
GRANT ALL PRIVILEGES ON g1_edu_system.* TO 'g1_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## 部署流程说明

### 自动触发条件
- 推送到 `main` 或 `master` 分支
- 创建Pull Request到主分支
- 手动触发（在GitHub Actions页面）

### 部署步骤
1. **代码检出**: 获取最新代码
2. **环境准备**: 设置Node.js和Python环境
3. **前端构建**: 安装依赖并构建Vue.js应用
4. **后端准备**: 安装Python依赖
5. **打包部署**: 创建部署包并传输到服务器
6. **服务配置**: 配置systemd服务和Nginx
7. **服务启动**: 启动应用服务

### 部署后的服务结构
```
/opt/g1-edu-system/
├── backend/          # Flask后端应用
├── frontend/         # Vue.js前端构建文件
└── mysql/           # 数据库相关脚本

/etc/systemd/system/g1-edu-system.service  # 系统服务配置
/etc/nginx/sites-available/g1-edu-system   # Nginx配置
```

## 访问地址

部署成功后，可以通过以下地址访问：

- **前端应用**: http://8.153.175.16
- **API接口**: http://8.153.175.16/api

## 手动部署

如果需要手动部署，可以在服务器上执行：

```bash
# 克隆仓库
git clone <your-repo-url>
cd Robot-Management

# 构建前端
cd front
npm install
npm run build
cd ..

# 执行部署脚本（需要先从workflow中提取）
bash deploy.sh
```

## 故障排除

### 1. 检查服务状态
```bash
# 检查应用服务
sudo systemctl status g1-edu-system

# 检查Nginx状态
sudo systemctl status nginx

# 查看应用日志
sudo journalctl -u g1-edu-system -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 2. 常见问题

**问题**: SSH连接失败
- 检查服务器IP地址和端口
- 确认SSH密钥配置正确
- 检查服务器防火墙设置

**问题**: 服务启动失败
- 检查Python依赖是否安装完整
- 确认数据库连接配置
- 查看systemd服务日志

**问题**: 前端无法访问
- 检查Nginx配置语法
- 确认静态文件路径正确
- 检查文件权限

### 3. 重新部署
```bash
# 停止服务
sudo systemctl stop g1-edu-system

# 重新启动
sudo systemctl start g1-edu-system

# 重新加载Nginx
sudo systemctl reload nginx
```

## 安全建议

1. **SSH密钥安全**:
   - 使用强密码保护私钥
   - 定期轮换SSH密钥
   - 限制SSH访问IP

2. **服务器安全**:
   - 配置防火墙规则
   - 定期更新系统
   - 使用非root用户运行应用

3. **数据库安全**:
   - 使用强密码
   - 限制数据库访问权限
   - 定期备份数据

## 监控和维护

### 日志监控
```bash
# 实时查看应用日志
sudo journalctl -u g1-edu-system -f

# 查看最近的错误
sudo journalctl -u g1-edu-system --since "1 hour ago" -p err
```

### 性能监控
```bash
# 检查系统资源
top
htop
df -h
free -h

# 检查网络连接
netstat -tlnp | grep :5000
netstat -tlnp | grep :80
```

### 备份策略
```bash
# 备份应用文件
sudo tar -czf /backup/g1-edu-system-$(date +%Y%m%d).tar.gz /opt/g1-edu-system

# 备份数据库
mysqldump -u g1_user -p g1_edu_system > /backup/g1_edu_system-$(date +%Y%m%d).sql
```

---

**注意**: 首次部署前请确保所有预配置步骤已完成，并且GitHub Secrets已正确设置。