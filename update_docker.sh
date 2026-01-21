#!/bin/bash

# MCP 服务器 Docker 更新脚本
# 用于快速更新已部署的 Docker 服务

set -e  # 遇到错误立即退出

echo "=================================================="
echo "MCP 服务器 Docker 更新脚本"
echo "=================================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查当前服务状态
echo -e "${YELLOW}[1/7] 检查当前服务状态...${NC}"
if sudo docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ 服务正在运行${NC}"
else
    echo -e "${RED}⚠ 警告: 服务未运行${NC}"
fi
echo ""

# 2. 备份配置文件
echo -e "${YELLOW}[2/7] 备份配置文件...${NC}"
if [ -f "config.json" ]; then
    backup_file="config.json.backup.$(date +%Y%m%d_%H%M%S)"
    cp config.json "$backup_file"
    echo -e "${GREEN}✓ 配置已备份到: $backup_file${NC}"
else
    echo -e "${RED}✗ 错误: config.json 文件不存在${NC}"
    exit 1
fi
echo ""

# 3. 停止当前容器
echo -e "${YELLOW}[3/7] 停止当前容器...${NC}"
sudo docker-compose down
echo -e "${GREEN}✓ 容器已停止${NC}"
echo ""

# 4. 清理旧镜像（可选）
read -p "是否清理旧的未使用镜像？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[4/7] 清理旧镜像...${NC}"
    sudo docker image prune -f
    echo -e "${GREEN}✓ 旧镜像已清理${NC}"
else
    echo -e "${YELLOW}[4/7] 跳过清理旧镜像${NC}"
fi
echo ""

# 5. 重新构建镜像
echo -e "${YELLOW}[5/7] 重新构建镜像...${NC}"
read -p "是否使用 --no-cache 强制重建？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo docker-compose build --no-cache
else
    sudo docker-compose build
fi
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# 6. 启动新容器
echo -e "${YELLOW}[6/7] 启动新容器...${NC}"
sudo docker-compose up -d
echo -e "${GREEN}✓ 容器已启动${NC}"
echo ""

# 7. 验证服务状态
echo -e "${YELLOW}[7/7] 验证服务状态...${NC}"
sleep 5  # 等待容器完全启动

if sudo docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ 服务启动成功！${NC}"
    echo ""
    echo "容器状态:"
    sudo docker-compose ps
    echo ""
    echo "最近日志:"
    sudo docker-compose logs --tail=20
else
    echo -e "${RED}✗ 服务启动失败！${NC}"
    echo "详细日志:"
    sudo docker-compose logs
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}更新完成！${NC}"
echo "=================================================="
echo ""
echo "服务地址: http://localhost:4567/sse"
echo "日志位置: /data/logs/stock_arbitrade_notify_mcp/"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
