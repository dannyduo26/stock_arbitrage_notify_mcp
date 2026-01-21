# MCP 服务器 Docker 更新脚本 (Windows PowerShell)
# 用于快速更新已部署的 Docker 服务

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "MCP 服务器 Docker 更新脚本" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查当前服务状态
Write-Host "[1/7] 检查当前服务状态..." -ForegroundColor Yellow
$running = docker-compose ps 2>$null | Select-String "Up"
if ($running) {
    Write-Host "✓ 服务正在运行" -ForegroundColor Green
} else {
    Write-Host "⚠ 警告: 服务未运行" -ForegroundColor Red
}
Write-Host ""

# 2. 备份配置文件
Write-Host "[2/7] 备份配置文件..." -ForegroundColor Yellow
if (Test-Path "config.json") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "config.json.backup.$timestamp"
    Copy-Item "config.json" $backupFile
    Write-Host "✓ 配置已备份到: $backupFile" -ForegroundColor Green
} else {
    Write-Host "✗ 错误: config.json 文件不存在" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. 停止当前容器
Write-Host "[3/7] 停止当前容器..." -ForegroundColor Yellow
docker-compose down
Write-Host "✓ 容器已停止" -ForegroundColor Green
Write-Host ""

# 4. 清理旧镜像（可选）
$cleanOld = Read-Host "是否清理旧的未使用镜像？(y/n)"
if ($cleanOld -eq 'y' -or $cleanOld -eq 'Y') {
    Write-Host "[4/7] 清理旧镜像..." -ForegroundColor Yellow
    docker image prune -f
    Write-Host "✓ 旧镜像已清理" -ForegroundColor Green
} else {
    Write-Host "[4/7] 跳过清理旧镜像" -ForegroundColor Yellow
}
Write-Host ""

# 5. 重新构建镜像
Write-Host "[5/7] 重新构建镜像..." -ForegroundColor Yellow
$noCache = Read-Host "是否使用 --no-cache 强制重建？(y/n)"
if ($noCache -eq 'y' -or $noCache -eq 'Y') {
    docker-compose build --no-cache
} else {
    docker-compose build
}
Write-Host "✓ 镜像构建完成" -ForegroundColor Green
Write-Host ""

# 6. 启动新容器
Write-Host "[6/7] 启动新容器..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✓ 容器已启动" -ForegroundColor Green
Write-Host ""

# 7. 验证服务状态
Write-Host "[7/7] 验证服务状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # 等待容器完全启动

$running = docker-compose ps | Select-String "Up"
if ($running) {
    Write-Host "✓ 服务启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "容器状态:" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
    Write-Host "最近日志:" -ForegroundColor Cyan
    docker-compose logs --tail=20
} else {
    Write-Host "✗ 服务启动失败！" -ForegroundColor Red
    Write-Host "详细日志:" -ForegroundColor Yellow
    docker-compose logs
    exit 1
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "更新完成！" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务地址: http://localhost:4567/sse"
Write-Host "日志位置: /data/logs/stock_arbitrade_notify_mcp/"
Write-Host ""
Write-Host "常用命令:"
Write-Host "  查看日志: docker-compose logs -f"
Write-Host "  停止服务: docker-compose down"
Write-Host "  重启服务: docker-compose restart"
Write-Host ""
