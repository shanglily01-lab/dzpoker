# 本地重启脚本 - 不拉取代码，仅重新构建和重启
Write-Host "=== 本地重启部署 ===" -ForegroundColor Green

# 清理 Python 缓存
Write-Host "1. 清理 Python 缓存..." -ForegroundColor Yellow
Get-ChildItem -Path "backend" -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "backend" -Filter "*.pyc" -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue

# 停止服务
Write-Host "2. 停止服务..." -ForegroundColor Yellow
docker compose down

# 重新构建前端
Write-Host "3. 重新构建前端..." -ForegroundColor Yellow
docker compose build --no-cache frontend

# 启动所有服务
Write-Host "4. 启动服务..." -ForegroundColor Yellow
docker compose up -d

# 等待服务启动
Write-Host "5. 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 检查服务状态
Write-Host "6. 检查服务状态..." -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "=== 部署完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "检查日志:" -ForegroundColor Cyan
Write-Host "  docker logs poker-api --tail 50"
Write-Host "  docker logs poker-frontend --tail 50"
Write-Host ""
Write-Host "访问:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000"
Write-Host "  API文档: http://localhost:8000/docs"
