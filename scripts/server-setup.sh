#!/bin/bash

# 宇树G1 EDU机器人管理系统 - 服务器环境配置脚本
# 适用于Ubuntu 18.04+ / Debian 10+ / CentOS 7+
# 使用方法: bash server-setup.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update && sudo apt upgrade -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum update -y
    else
        log_warning "未知的操作系统，跳过系统更新"
    fi
    
    log_success "系统包更新完成"
}

# 安装基础软件
install_basic_packages() {
    log_info "安装基础软件包..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt install -y \
            nginx \
            python3 \
            python3-pip \
            python3-venv \
            git \
            curl \
            wget \
            unzip \
            htop \
            vim \
            ufw \
            certbot \
            python3-certbot-nginx
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install -y \
            nginx \
            python3 \
            python3-pip \
            git \
            curl \
            wget \
            unzip \
            htop \
            vim \
            firewalld
    fi
    
    log_success "基础软件包安装完成"
}

# 安装Node.js
install_nodejs() {
    log_info "安装Node.js..."
    
    # 使用NodeSource仓库安装Node.js 18.x
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt install -y nodejs
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install -y nodejs npm
    fi
    
    # 验证安装
    node_version=$(node --version)
    npm_version=$(npm --version)
    
    log_success "Node.js安装完成: $node_version"
    log_success "npm版本: $npm_version"
}

# 安装MySQL
install_mysql() {
    log_info "安装MySQL数据库..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt install -y mysql-server mysql-client
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install -y mysql-server mysql
    fi
    
    # 启动MySQL服务
    sudo systemctl start mysql
    sudo systemctl enable mysql
    
    log_success "MySQL安装完成"
    log_warning "请运行 'sudo mysql_secure_installation' 来配置MySQL安全设置"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # 配置UFW
        sudo ufw --force reset
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        
        # 允许SSH
        sudo ufw allow ssh
        
        # 允许HTTP和HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # 启用防火墙
        sudo ufw --force enable
        
        log_success "UFW防火墙配置完成"
        
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # 配置firewalld
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        
        # 允许HTTP和HTTPS
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --permanent --add-service=ssh
        
        # 重新加载配置
        sudo firewall-cmd --reload
        
        log_success "firewalld防火墙配置完成"
    fi
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 启动并启用Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # 创建默认配置备份
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    
    # 测试Nginx配置
    sudo nginx -t
    
    log_success "Nginx配置完成"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    
    # 创建g1edu用户（如果不存在）
    if ! id "g1edu" &>/dev/null; then
        sudo useradd -m -s /bin/bash g1edu
        sudo usermod -aG sudo g1edu
        log_success "用户g1edu创建完成"
    else
        log_info "用户g1edu已存在"
    fi
    
    # 创建应用目录
    sudo mkdir -p /opt/g1-edu-system
    sudo chown g1edu:g1edu /opt/g1-edu-system
    
    log_success "应用目录创建完成"
}

# 配置Python环境
setup_python() {
    log_info "配置Python环境..."
    
    # 升级pip
    python3 -m pip install --upgrade pip --user
    
    # 安装常用Python包
    pip3 install --user \
        virtualenv \
        flask \
        gunicorn \
        pymysql \
        sqlalchemy
    
    log_success "Python环境配置完成"
}

# 配置SSH密钥（可选）
setup_ssh_keys() {
    read -p "是否要配置SSH密钥认证？(y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "配置SSH密钥认证..."
        
        # 创建.ssh目录
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh
        
        # 如果authorized_keys不存在，创建它
        if [ ! -f ~/.ssh/authorized_keys ]; then
            touch ~/.ssh/authorized_keys
            chmod 600 ~/.ssh/authorized_keys
        fi
        
        log_info "请将您的公钥添加到 ~/.ssh/authorized_keys 文件中"
        log_info "或者使用 ssh-copy-id 命令从客户端复制公钥"
        
        # 配置SSH安全设置
        sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
        
        # 禁用密码认证（可选）
        read -p "是否禁用SSH密码认证？(y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
            sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
            sudo systemctl restart sshd
            log_warning "SSH密码认证已禁用，请确保密钥认证正常工作"
        fi
        
        log_success "SSH密钥配置完成"
    fi
}

# 创建数据库
setup_database() {
    read -p "是否要创建应用数据库？(y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "创建应用数据库..."
        
        # 提示输入数据库信息
        read -p "请输入MySQL root密码: " -s mysql_root_password
        echo
        read -p "请输入应用数据库名 (默认: g1_edu_system): " db_name
        db_name=${db_name:-g1_edu_system}
        
        read -p "请输入应用数据库用户名 (默认: g1_user): " db_user
        db_user=${db_user:-g1_user}
        
        read -p "请输入应用数据库密码: " -s db_password
        echo
        
        # 创建数据库和用户
        mysql -u root -p"$mysql_root_password" << EOF
CREATE DATABASE IF NOT EXISTS $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$db_user'@'localhost' IDENTIFIED BY '$db_password';
GRANT ALL PRIVILEGES ON $db_name.* TO '$db_user'@'localhost';
FLUSH PRIVILEGES;
EOF
        
        if [ $? -eq 0 ]; then
            log_success "数据库创建完成"
            log_info "数据库名: $db_name"
            log_info "用户名: $db_user"
            
            # 保存数据库配置到文件
            cat > /tmp/db_config.txt << EOF
数据库配置信息:
数据库名: $db_name
用户名: $db_user
密码: $db_password
EOF
            log_info "数据库配置已保存到 /tmp/db_config.txt"
        else
            log_error "数据库创建失败"
        fi
    fi
}

# 显示安装总结
show_summary() {
    log_success "=== 服务器环境配置完成 ==="
    echo
    log_info "已安装的软件:"
    echo "  ✓ Nginx Web服务器"
    echo "  ✓ Python 3 和 pip"
    echo "  ✓ Node.js 和 npm"
    echo "  ✓ MySQL 数据库"
    echo "  ✓ Git 版本控制"
    echo "  ✓ 防火墙配置"
    echo
    log_info "服务状态:"
    echo "  ✓ Nginx: $(sudo systemctl is-active nginx)"
    echo "  ✓ MySQL: $(sudo systemctl is-active mysql)"
    echo
    log_info "下一步操作:"
    echo "  1. 配置GitHub Actions Secrets"
    echo "  2. 推送代码到GitHub触发自动部署"
    echo "  3. 访问 http://8.153.175.16 查看应用"
    echo
    log_warning "重要提醒:"
    echo "  - 请运行 'sudo mysql_secure_installation' 配置MySQL安全设置"
    echo "  - 请确保防火墙规则符合您的安全要求"
    echo "  - 建议配置SSL证书以启用HTTPS"
    echo
}

# 主函数
main() {
    echo "======================================"
    echo "宇树G1 EDU机器人管理系统"
    echo "服务器环境自动配置脚本"
    echo "======================================"
    echo
    
    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        log_info "请使用普通用户（具有sudo权限）运行"
        exit 1
    fi
    
    # 检查sudo权限
    if ! sudo -n true 2>/dev/null; then
        log_error "当前用户没有sudo权限"
        exit 1
    fi
    
    log_info "开始配置服务器环境..."
    echo
    
    # 执行配置步骤
    detect_os
    update_system
    install_basic_packages
    install_nodejs
    install_mysql
    setup_firewall
    setup_nginx
    create_app_user
    setup_python
    setup_ssh_keys
    setup_database
    
    # 显示总结
    show_summary
    
    log_success "服务器环境配置完成！"
}

# 错误处理
trap 'log_error "脚本执行过程中发生错误，请检查日志"' ERR

# 运行主函数
main "$@"