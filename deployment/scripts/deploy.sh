#!/bin/bash

# Web计算器蓝绿部署脚本
# 使用方法: ./deploy.sh <镜像标签>

set -e  # 遇到错误时停止执行

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取参数
IMAGE_TAG=${1:-"latest"}

# 检查Docker Compose是否可用
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose 未安装"
    exit 1
fi

# 检查当前目录
if [ ! -f "docker-compose.prod.yml" ]; then
    log_error "请在包含 docker-compose.prod.yml 的目录中运行此脚本"
    exit 1
fi

# 确定当前活跃的环境
determine_current_color() {
    # 检查哪个容器正在运行
    if docker ps --format "{{.Names}}" | grep -q "webcalc_blue"; then
        if docker ps --format "{{.Names}} {{.Status}}" | grep "webcalc_blue" | grep -q "Up"; then
            echo "blue"
            return
        fi
    fi
    
    if docker ps --format "{{.Names}}" | grep -q "webcalc_green"; then
        if docker ps --format "{{.Names}} {{.Status}}" | grep "webcalc_green" | grep -q "Up"; then
            echo "green"
            return
        fi
    fi
    
    # 如果没有运行的服务，默认使用蓝色
    echo "blue"
}

# 部署到指定颜色
deploy_to_color() {
    local color=$1
    local port=""
    
    if [ "$color" = "blue" ]; then
        port="5001"
        export BLUE_IMAGE="ghcr.io/$GITHUB_REPOSITORY:$IMAGE_TAG"
        log_info "部署到蓝色环境 (端口: $port)"
    else
        port="5002"
        export GREEN_IMAGE="ghcr.io/$GITHUB_REPOSITORY:$IMAGE_TAG"
        log_info "部署到绿色环境 (端口: $port)"
    fi
    
    # 拉取新镜像
    log_info "拉取镜像: ghcr.io/$GITHUB_REPOSITORY:$IMAGE_TAG"
    docker-compose -f docker-compose.prod.yml pull "app_$color" || {
        log_error "拉取镜像失败"
        return 1
    }
    
    # 启动新服务
    log_info "启动 $color 服务..."
    docker-compose -f docker-compose.prod.yml up -d "app_$color"
    
    # 等待健康检查
    log_info "等待 $color 服务健康..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml ps "app_$color" | grep -q "healthy"; then
            log_info "$color 服务健康检查通过!"
            return 0
        fi
        
        log_info "尝试 $attempt/$max_attempts: $color 服务尚未就绪，等待5秒..."
        sleep 5
        ((attempt++))
    done
    
    log_error "$color 服务在 $max_attempts 次尝试后仍未健康"
    return 1
}

# 切换Nginx配置
switch_nginx_config() {
    local active_color=$1
    
    log_info "切换到 $active_color 环境..."
    
    # 创建新的Nginx配置
    cat > nginx/conf.d/default.conf << EOF
upstream webcalc_upstream {
    server app_${active_color}:$([ "$active_color" = "blue" ] && echo "5001" || echo "5002") max_fails=1 fail_timeout=5s;
}

server {
    listen 80;
    server_name _;
    
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    location /health {
        proxy_pass http://webcalc_upstream;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        access_log off;
    }
    
    location / {
        proxy_pass http://webcalc_upstream;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 5s;
        proxy_read_timeout 10s;
        proxy_send_timeout 10s;
    }
}
EOF
    
    # 重新加载Nginx
    log_info "重新加载Nginx配置..."
    docker-compose -f docker-compose.prod.yml exec -T proxy nginx -s reload
    
    log_info "流量已切换到 $active_color 环境"
}

# 停止旧服务
stop_old_service() {
    local active_color=$1
    local old_color=""
    
    if [ "$active_color" = "blue" ]; then
        old_color="green"
    else
        old_color="blue"
    fi
    
    log_info "停止旧的 $old_color 服务..."
    docker-compose -f docker-compose.prod.yml stop "app_$old_color" || log_warn "停止 $old_color 服务失败"
}

# 主部署流程
main() {
    log_info "开始部署流程..."
    log_info "镜像标签: $IMAGE_TAG"
    log_info "GitHub仓库: $GITHUB_REPOSITORY"
    
    # 1. 确定当前活跃的颜色
    local current_color=$(determine_current_color)
    local new_color=""
    
    if [ "$current_color" = "blue" ]; then
        new_color="green"
    else
        new_color="blue"
    fi
    
    log_info "当前活跃环境: $current_color"
    log_info "新部署环境: $new_color"
    
    # 2. 部署到新环境
    if ! deploy_to_color "$new_color"; then
        log_error "部署到 $new_color 环境失败"
        exit 1
    fi
    
    # 3. 切换Nginx配置
    switch_nginx_config "$new_color"
    
    # 4. 停止旧服务
    stop_old_service "$new_color"
    
    log_info "部署完成!"
    log_info "当前活跃环境: $new_color"
    log_info "应用可通过 http://localhost 访问"
}

# 执行主函数
main "$@"