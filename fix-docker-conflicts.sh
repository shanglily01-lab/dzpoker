#!/bin/bash

################################################################################
# Docker 依赖冲突修复脚本
# 用于解决 Amazon Linux 上的包冲突问题
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
echo -e "${GREEN}  Docker 依赖冲突修复工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否为root
if [[ $EUID -ne 0 ]]; then
    log_error "此脚本需要root权限"
    log_info "请使用: sudo bash $0"
    exit 1
fi

# 检测系统版本
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    log_info "系统: $OS $VER"
else
    log_error "无法检测系统版本"
    exit 1
fi

# 方案选择
echo ""
echo "请选择修复方案:"
echo "1) 使用 --allowerasing (允许删除冲突包)"
echo "2) 使用 --skip-broken (跳过冲突包)"
echo "3) 清理并重试"
echo "4) 使用 Docker 官方仓库"
echo "5) 全部尝试 (推荐)"
read -p "请选择 [1-5]: " -n 1 -r
echo ""

case $REPLY in
    1)
        log_info "方案1: 使用 --allowerasing"
        yum install -y docker --allowerasing
        ;;
    2)
        log_info "方案2: 使用 --skip-broken"
        yum install -y docker --skip-broken
        ;;
    3)
        log_info "方案3: 清理并重试"
        log_info "清理YUM缓存..."
        yum clean all
        rm -rf /var/cache/yum

        log_info "更新系统..."
        yum update -y --allowerasing

        log_info "重新安装Docker..."
        yum install -y docker --allowerasing
        ;;
    4)
        log_info "方案4: 使用Docker官方仓库"

        # 卸载旧版本
        log_info "卸载旧版本..."
        yum remove -y docker docker-client docker-client-latest docker-common \
            docker-latest docker-latest-logrotate docker-logrotate docker-engine \
            podman runc 2>/dev/null || true

        # 安装依赖
        log_info "安装必要工具..."
        yum install -y yum-utils device-mapper-persistent-data lvm2

        # 添加Docker官方仓库
        log_info "添加Docker官方仓库..."
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

        # 安装Docker
        log_info "安装Docker CE..."
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ;;
    5)
        log_info "方案5: 全部尝试"

        # 尝试1: allowerasing
        log_info "尝试1: 使用 --allowerasing"
        if yum install -y docker --allowerasing 2>/dev/null; then
            log_info "✓ 方案1成功"
        else
            log_warn "✗ 方案1失败，尝试方案2..."

            # 尝试2: skip-broken
            if yum install -y docker --skip-broken 2>/dev/null; then
                log_info "✓ 方案2成功"
            else
                log_warn "✗ 方案2失败，尝试方案3..."

                # 尝试3: 清理后重试
                yum clean all
                rm -rf /var/cache/yum
                yum update -y --allowerasing

                if yum install -y docker --allowerasing 2>/dev/null; then
                    log_info "✓ 方案3成功"
                else
                    log_warn "✗ 方案3失败，尝试方案4(Docker官方仓库)..."

                    # 尝试4: Docker官方仓库
                    yum remove -y docker docker-client docker-client-latest docker-common \
                        docker-latest docker-latest-logrotate docker-logrotate docker-engine \
                        podman runc 2>/dev/null || true

                    yum install -y yum-utils device-mapper-persistent-data lvm2
                    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

                    if yum install -y docker-ce docker-ce-cli containerd.io; then
                        log_info "✓ 方案4成功"
                    else
                        log_error "✗ 所有方案都失败了"
                        exit 1
                    fi
                fi
            fi
        fi
        ;;
    *)
        log_error "无效选择"
        exit 1
        ;;
esac

# 验证安装
echo ""
log_info "验证Docker安装..."

if command -v docker &> /dev/null; then
    log_info "✓ Docker安装成功: $(docker --version)"

    # 启动Docker
    log_info "启动Docker服务..."
    systemctl start docker
    systemctl enable docker

    # 测试Docker
    log_info "测试Docker..."
    if docker run --rm hello-world &> /dev/null; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ✓ Docker 安装并测试成功！${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "Docker版本: $(docker --version)"
        echo ""
        echo "下一步:"
        echo "1. 添加用户到docker组: sudo usermod -aG docker \$USER"
        echo "2. 重新登录或运行: newgrp docker"
        echo "3. 安装Docker Compose (如需要)"
        echo "4. 继续部署应用"
    else
        log_warn "Docker已安装但测试失败"
        log_info "请检查Docker日志: journalctl -u docker"
    fi
else
    log_error "Docker安装失败"
    echo ""
    echo "建议:"
    echo "1. 检查系统日志: journalctl -xe"
    echo "2. 查看YUM日志: cat /var/log/yum.log"
    echo "3. 手动安装: yum install -y docker --allowerasing"
    exit 1
fi

# 询问是否安装Docker Compose
echo ""
read -p "是否安装Docker Compose? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "安装Docker Compose..."

    # 下载最新版本
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")' || echo "v2.24.0")
    log_info "下载Docker Compose $COMPOSE_VERSION"

    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    log_info "✓ Docker Compose安装完成: $(docker-compose --version)"
fi

echo ""
log_info "修复完成！"
