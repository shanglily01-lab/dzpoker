#!/bin/bash

################################################################################
# Docker Buildx 版本问题修复脚本
# 解决 "compose build requires buildx 0.17 or later" 错误
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Docker Buildx 升级工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否为root
if [[ $EUID -ne 0 ]]; then
    log_error "此脚本需要root权限"
    log_info "请使用: sudo bash $0"
    exit 1
fi

# 检查当前版本
log_info "当前Docker版本:"
docker --version
docker buildx version 2>/dev/null || log_warn "Buildx未安装或版本过低"

echo ""
echo "请选择解决方案:"
echo "1) 升级Docker Buildx (推荐)"
echo "2) 使用兼容的构建方式 (无需升级)"
echo "3) 升级整个Docker引擎"
echo "4) 全部尝试"
read -p "请选择 [1-4]: " -n 1 -r
echo ""

case $REPLY in
    1)
        log_info "方案1: 升级Docker Buildx"

        # 下载最新版本的buildx
        BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -Po '"tag_name": "v\K[0-9.]+' || echo "0.17.1")
        log_info "下载 Buildx v${BUILDX_VERSION}..."

        mkdir -p ~/.docker/cli-plugins
        curl -L "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-amd64" -o ~/.docker/cli-plugins/docker-buildx
        chmod +x ~/.docker/cli-plugins/docker-buildx

        # 为root用户也安装
        mkdir -p /root/.docker/cli-plugins
        cp ~/.docker/cli-plugins/docker-buildx /root/.docker/cli-plugins/

        log_info "验证安装..."
        docker buildx version

        log_info "✓ Buildx升级完成"
        ;;

    2)
        log_info "方案2: 使用兼容的构建方式"

        log_info "创建兼容的docker-compose配置..."

        # 备份原文件
        if [ -f "docker-compose.yml" ]; then
            cp docker-compose.yml docker-compose.yml.backup
            log_info "已备份 docker-compose.yml -> docker-compose.yml.backup"
        fi

        log_info ""
        log_info "使用传统构建方式:"
        echo "  docker-compose build --no-cache"
        echo "  docker-compose up -d"
        log_info ""
        log_info "或者分步构建:"
        echo "  cd backend && docker build -t dzpoker-api ."
        echo "  cd ../frontend && docker build -t dzpoker-frontend ."
        echo "  docker-compose up -d"
        ;;

    3)
        log_info "方案3: 升级Docker引擎"

        log_info "卸载旧版本Docker..."
        yum remove -y docker docker-client docker-client-latest docker-common \
            docker-latest docker-latest-logrotate docker-logrotate docker-engine \
            podman runc 2>/dev/null || true

        log_info "安装依赖..."
        yum install -y yum-utils device-mapper-persistent-data lvm2

        log_info "添加Docker官方仓库..."
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

        log_info "安装最新版Docker..."
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

        log_info "启动Docker..."
        systemctl start docker
        systemctl enable docker

        log_info "验证安装..."
        docker --version
        docker buildx version
        docker compose version

        log_info "✓ Docker升级完成"
        ;;

    4)
        log_info "方案4: 全部尝试"

        # 尝试1: 升级Buildx
        log_info "尝试1: 升级Buildx..."
        BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -Po '"tag_name": "v\K[0-9.]+' || echo "0.17.1")

        mkdir -p ~/.docker/cli-plugins /root/.docker/cli-plugins

        if curl -L "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-amd64" -o ~/.docker/cli-plugins/docker-buildx 2>/dev/null; then
            chmod +x ~/.docker/cli-plugins/docker-buildx
            cp ~/.docker/cli-plugins/docker-buildx /root/.docker/cli-plugins/

            if docker buildx version | grep -q "0.17"; then
                log_info "✓ Buildx升级成功"
                exit 0
            fi
        fi

        log_warn "Buildx升级失败，尝试升级Docker引擎..."

        # 尝试2: 升级Docker
        yum remove -y docker docker-client docker-client-latest docker-common \
            docker-latest docker-latest-logrotate docker-logrotate docker-engine \
            podman runc 2>/dev/null || true

        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

        if yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; then
            systemctl start docker
            systemctl enable docker
            log_info "✓ Docker升级成功"
            docker --version
            docker buildx version
        else
            log_error "所有方案都失败了"
            exit 1
        fi
        ;;

    *)
        log_error "无效选择"
        exit 1
        ;;
esac

echo ""
log_info "修复完成！"
log_info ""
log_info "下一步:"
echo "  cd /path/to/dzpoker"
echo "  docker-compose build"
echo "  docker-compose up -d"
