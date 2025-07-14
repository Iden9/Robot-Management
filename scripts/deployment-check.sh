#!/bin/bash

# 宇树G1 EDU机器人管理系统 - 部署检查脚本
# 用于验证系统部署是否成功

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
SERVER_IP="8.153.175.16"
APP_DIR="/opt/g1-edu-system"
SERVICE_NAME="g1-edu-system"
API_PORT="5000"
WEB_PORT="80"

# 计数器
PASSED=0
FAILED=0
WARNINGS=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAILED++))
}

# 检查函数
check_service_status() {
    local service=$1
    local description=$2
    
    if systemctl is-active --quiet $service; then
        log_success "$description 服务运行正常"
    else
        log_error "$description 服务未运行"
        systemctl status $service --no-pager -l
    fi
}

check_port() {
    local port=$1
    local description=$2
    
    if netstat -tlnp | grep -q ":$port "; then
        log_success "端口 $port ($description) 正在监听"
    else
        log_error "端口 $port ($description) 未在监听"
    fi
}

check_url() {
    local url=$1
    local description=$2
    local expected_code=${3:-200}
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$response_code" = "$expected_code" ]; then
        log_success "$description 响应正常 (HTTP $response_code)"
    else
        log_error "$description 响应异常 (HTTP $response_code)"
    fi
}

check_file_exists() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        log_success "$description 文件存在"
    else
        log_error "$description 文件不存在: $file"
    fi
}

check_directory_exists() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        log_success "$description 目录存在"
    else
        log_error "$description 目录不存在: $dir"
    fi
}

check_database_connection() {
    log_info "检查数据库连接..."
    
    # 尝试连接数据库
    if command -v mysql >/dev/null 2>&1; then
        if mysql -u g1_user -p -e "USE g1_edu_system; SHOW TABLES;" >/dev/null 2>&1; then
            log_success "数据库连接正常"
        else
            log_error "数据库连接失败"
        fi
    else
        log_warning "MySQL客户端未安装，跳过数据库连接检查"
    fi
}

check_python_dependencies() {
    log_info "检查Python依赖..."
    
    cd "$APP_DIR/backend" 2>/dev/null || {
        log_error "无法进入后端目录"
        return
    }
    
    if [ -f "requirements.txt" ]; then
        local missing_deps=0
        while IFS= read -r line; do
            # 跳过空行和注释
            [[ "$line" =~ ^[[:space:]]*$ ]] && continue
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            
            # 提取包名（去掉版本号）
            local package=$(echo "$line" | sed 's/[>=<].*//' | sed 's/==.*//')
            
            if python3 -c "import $package" 2>/dev/null; then
                log_success "Python包 $package 已安装"
            else
                log_error "Python包 $package 未安装"
                ((missing_deps++))
            fi
        done < requirements.txt
        
        if [ $missing_deps -eq 0 ]; then
            log_success "所有Python依赖已安装"
        else
            log_error "缺少 $missing_deps 个Python依赖包"
        fi
    else
        log_warning "requirements.txt 文件不存在"
    fi
}

check_nginx_config() {
    log_info "检查Nginx配置..."
    
    if nginx -t 2>/dev/null; then
        log_success "Nginx配置语法正确"
    else
        log_error "Nginx配置语法错误"
        nginx -t
    fi
    
    local config_file="/etc/nginx/sites-available/g1-edu-system"
    if [ -f "$config_file" ]; then
        log_success "Nginx站点配置文件存在"
        
        if [ -L "/etc/nginx/sites-enabled/g1-edu-system" ]; then
            log_success "Nginx站点已启用"
        else
            log_error "Nginx站点未启用"
        fi
    else
        log_error "Nginx站点配置文件不存在"
    fi
}

check_logs() {
    log_info "检查应用日志..."
    
    # 检查systemd日志
    local recent_errors=$(journalctl -u $SERVICE_NAME --since "10 minutes ago" -p err --no-pager -q | wc -l)
    
    if [ "$recent_errors" -eq 0 ]; then
        log_success "最近10分钟内无错误日志"
    else
        log_warning "最近10分钟内有 $recent_errors 条错误日志"
        echo "最近的错误日志:"
        journalctl -u $SERVICE_NAME --since "10 minutes ago" -p err --no-pager -n 5
    fi
    
    # 检查Nginx日志
    if [ -f "/var/log/nginx/error.log" ]; then
        local nginx_errors=$(tail -n 100 /var/log/nginx/error.log | grep "$(date '+%Y/%m/%d')" | wc -l)
        if [ "$nginx_errors" -eq 0 ]; then
            log_success "今日无Nginx错误日志"
        else
            log_warning "今日有 $nginx_errors 条Nginx错误日志"
        fi
    fi
}

check_disk_space() {
    log_info "检查磁盘空间..."
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        log_success "磁盘空间充足 (使用率: ${usage}%)"
    elif [ "$usage" -lt 90 ]; then
        log_warning "磁盘空间紧张 (使用率: ${usage}%)"
    else
        log_error "磁盘空间不足 (使用率: ${usage}%)"
    fi
}

check_memory() {
    log_info "检查内存使用..."
    
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$mem_usage" -lt 80 ]; then
        log_success "内存使用正常 (使用率: ${mem_usage}%)"
    elif [ "$mem_usage" -lt 90 ]; then
        log_warning "内存使用较高 (使用率: ${mem_usage}%)"
    else
        log_error "内存使用过高 (使用率: ${mem_usage}%)"
    fi
}

check_api_endpoints() {
    log_info "检查API端点..."
    
    local base_url="http://localhost:$API_PORT"
    
    # 检查健康检查端点
    check_url "$base_url/api/health" "健康检查API"
    
    # 检查认证端点
    check_url "$base_url/api/auth/login" "登录API" "405"
    
    # 检查用户端点
    check_url "$base_url/api/users" "用户API" "401"
}

check_frontend_files() {
    log_info "检查前端文件..."
    
    local frontend_dir="$APP_DIR/frontend"
    
    check_directory_exists "$frontend_dir" "前端文件目录"
    check_file_exists "$frontend_dir/index.html" "前端入口文件"
    
    # 检查静态资源
    if [ -d "$frontend_dir/assets" ]; then
        log_success "前端静态资源目录存在"
    else
        log_warning "前端静态资源目录不存在"
    fi
}

run_performance_test() {
    log_info "运行性能测试..."
    
    # 简单的响应时间测试
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" "http://localhost/" || echo "999")
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        log_success "前端响应时间正常 (${response_time}s)"
    elif (( $(echo "$response_time < 5.0" | bc -l) )); then
        log_warning "前端响应时间较慢 (${response_time}s)"
    else
        log_error "前端响应时间过慢 (${response_time}s)"
    fi
}

show_summary() {
    echo
    echo "======================================"
    echo "           部署检查总结"
    echo "======================================"
    echo -e "${GREEN}通过检查: $PASSED${NC}"
    echo -e "${YELLOW}警告项目: $WARNINGS${NC}"
    echo -e "${RED}失败项目: $FAILED${NC}"
    echo
    
    if [ $FAILED -eq 0 ]; then
        if [ $WARNINGS -eq 0 ]; then
            log_success "🎉 部署检查完全通过！系统运行正常。"
        else
            log_warning "⚠️  部署基本成功，但有 $WARNINGS 个警告项需要关注。"
        fi
    else
        log_error "❌ 部署检查发现 $FAILED 个严重问题，需要立即修复。"
    fi
    
    echo
    echo "访问地址:"
    echo "  前端: http://$SERVER_IP"
    echo "  API:  http://$SERVER_IP/api"
    echo
    
    if [ $FAILED -gt 0 ]; then
        echo "故障排除建议:"
        echo "  1. 检查服务日志: sudo journalctl -u $SERVICE_NAME -f"
        echo "  2. 检查Nginx日志: sudo tail -f /var/log/nginx/error.log"
        echo "  3. 重启服务: sudo systemctl restart $SERVICE_NAME nginx"
        echo "  4. 检查配置文件: sudo nginx -t"
        echo
    fi
}

# 主检查函数
main() {
    echo "======================================"
    echo "宇树G1 EDU机器人管理系统"
    echo "部署状态检查"
    echo "======================================"
    echo
    
    log_info "开始检查系统部署状态..."
    echo
    
    # 基础服务检查
    echo "=== 基础服务检查 ==="
    check_service_status "nginx" "Nginx"
    check_service_status "$SERVICE_NAME" "应用"
    check_service_status "mysql" "MySQL"
    echo
    
    # 端口检查
    echo "=== 端口检查 ==="
    check_port "$WEB_PORT" "HTTP"
    check_port "$API_PORT" "API"
    check_port "3306" "MySQL"
    echo
    
    # 文件和目录检查
    echo "=== 文件和目录检查 ==="
    check_directory_exists "$APP_DIR" "应用根目录"
    check_directory_exists "$APP_DIR/backend" "后端目录"
    check_file_exists "$APP_DIR/backend/run.py" "后端入口文件"
    check_frontend_files
    echo
    
    # 配置检查
    echo "=== 配置检查 ==="
    check_nginx_config
    check_python_dependencies
    echo
    
    # 网络检查
    echo "=== 网络检查 ==="
    check_url "http://localhost/" "前端页面"
    check_api_endpoints
    echo
    
    # 数据库检查
    echo "=== 数据库检查 ==="
    check_database_connection
    echo
    
    # 系统资源检查
    echo "=== 系统资源检查 ==="
    check_disk_space
    check_memory
    echo
    
    # 日志检查
    echo "=== 日志检查 ==="
    check_logs
    echo
    
    # 性能测试
    echo "=== 性能测试 ==="
    run_performance_test
    echo
    
    # 显示总结
    show_summary
}

# 检查是否有必要的命令
command -v curl >/dev/null 2>&1 || { log_error "curl 命令未找到，请安装 curl"; exit 1; }
command -v bc >/dev/null 2>&1 || { log_warning "bc 命令未找到，某些检查可能不准确"; }

# 运行主函数
main "$@"