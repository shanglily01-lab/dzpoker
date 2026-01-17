# 德州扑克系统 - 完整修复部署脚本
# 用途：重新部署系统并修复历史数据

Write-Host "================================" -ForegroundColor Cyan
Write-Host "德州扑克系统 - 完整修复部署" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 停止现有容器
Write-Host "[1/5] 停止现有容器..." -ForegroundColor Yellow
docker compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 停止容器时出现错误，继续执行..." -ForegroundColor Yellow
}
Write-Host ""

# 2. 重新构建前端（强制无缓存）
Write-Host "[2/5] 重新构建前端容器（无缓存，这可能需要几分钟）..." -ForegroundColor Yellow
docker compose build --no-cache frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 前端构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. 重新构建后端
Write-Host "[3/5] 重新构建后端容器..." -ForegroundColor Yellow
docker compose build --no-cache backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 后端构建失败！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. 启动所有服务
Write-Host "[4/5] 启动所有服务..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 启动失败！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 5. 等待服务启动
Write-Host "[5/5] 等待服务启动（15秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

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

# 询问是否修复历史数据
Write-Host "是否需要修复历史游戏数据？(Y/N)" -ForegroundColor Yellow
$fix = Read-Host

if ($fix -eq "Y" -or $fix -eq "y") {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "修复历史游戏数据" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "正在修复历史游戏..." -ForegroundColor Yellow
    docker compose exec backend python /app/fix_old_games.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 历史数据修复完成！" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️ 历史数据修复失败，请检查日志" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000" -ForegroundColor White
Write-Host "  后端API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "查看后端日志:" -ForegroundColor Cyan
Write-Host "  docker compose logs backend --tail=50 -f" -ForegroundColor White
Write-Host ""
Write-Host "测试步骤:" -ForegroundColor Cyan
Write-Host "  1. 访问 http://localhost:3000" -ForegroundColor White
Write-Host "  2. 创建新游戏并开启自动模式" -ForegroundColor White
Write-Host "  3. 打开浏览器控制台（F12）查看是否有 [Finish] 日志" -ForegroundColor White
Write-Host "  4. 等待游戏结束" -ForegroundColor White
Write-Host "  5. 查看数据分析页面，确认:" -ForegroundColor White
Write-Host "     - 游戏状态为 '已完成'" -ForegroundColor White
Write-Host "     - 手牌数不为 0" -ForegroundColor White
Write-Host ""
