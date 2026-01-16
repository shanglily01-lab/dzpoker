# 德州扑克系统 - 修复部署脚本
# 用途：部署手牌数据保存修复

Write-Host "================================" -ForegroundColor Cyan
Write-Host "德州扑克系统 - 部署修复补丁" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 停止现有容器
Write-Host "[1/4] 停止现有容器..." -ForegroundColor Yellow
docker compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 停止容器时出现错误，继续执行..." -ForegroundColor Yellow
}
Write-Host ""

# 2. 重新构建前端和后端
Write-Host "[2/4] 重新构建前端和后端容器（这可能需要几分钟）..." -ForegroundColor Yellow
docker compose build --no-cache frontend backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. 启动所有服务
Write-Host "[3/4] 启动所有服务..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 启动失败！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. 等待服务启动
Write-Host "[4/4] 等待服务启动（10秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查容器状态
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "容器状态:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000" -ForegroundColor White
Write-Host "  后端API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "查看后端日志:" -ForegroundColor Cyan
Write-Host "  docker compose logs backend --tail=50 -f" -ForegroundColor White
Write-Host ""
Write-Host "测试步骤:" -ForegroundColor Cyan
Write-Host "  1. 访问 http://localhost:3000" -ForegroundColor White
Write-Host "  2. 创建新游戏并开启自动模式" -ForegroundColor White
Write-Host "  3. 等待游戏结束" -ForegroundColor White
Write-Host "  4. 查看数据分析页面，手牌数应该不再是0" -ForegroundColor White
Write-Host ""
