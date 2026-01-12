#!/bin/bash
# 获取后端日志

echo "======================================"
echo "  后端日志 - 最近 100 行"
echo "======================================"
echo ""

# 如果在本地，使用 docker logs
# 如果在远程，使用 ssh
if [ "$1" == "remote" ]; then
    ssh user@13.212.252.171 "cd dzpoker && docker logs api --tail 100"
else
    # 尝试使用 api 或 poker-api 容器名
    if docker ps | grep -q "poker-api"; then
        docker logs poker-api --tail 100
    else
        docker logs api --tail 100
    fi
fi
