# 日志配置说明

## 环境变量控制

通过 `ENV` 环境变量控制日志输出行为：

### 开发环境（dev）

```bash
ENV=dev python server/mcp_server.py
```

- ✅ 日志输出到控制台
- ❌ 不写入日志文件
- 适用于本地开发和调试

### 生产环境（prod）

```bash
ENV=prod python server/mcp_server.py
```

- ✅ 日志输出到控制台
- ✅ 日志写入文件：`/app/logs/mcp_server_YYYYMMDD.log`
- 适用于生产部署

## Docker 部署

### docker-compose.yml 配置

```yaml
environment:
  - ENV=prod # 生产环境，启用文件日志
```

### 修改环境

```yaml
environment:
  - ENV=dev # 开发环境，仅控制台日志
```

## 日志文件说明

### 文件位置

- **容器内**: `/app/logs/mcp_server_YYYYMMDD.log`
- **宿主机**: `/data/logs/stock_arbitrade_notify_mcp/mcp_server_YYYYMMDD.log`

### 日志格式

```
2026-01-14 15:05:30 - mcp_server - INFO - 启动 MCP 服务器: arbitrage-suite
2026-01-14 15:05:30 - mcp_server - INFO - 监听端口: 4567
2026-01-14 15:05:30 - mcp_server - INFO - 传输协议: SSE
```

### 日志内容

- 服务器启动信息
- 工具调用记录（函数名、参数）
- 执行结果统计
- 错误和异常信息

## 本地开发建议

本地开发时推荐使用开发环境：

```bash
# 设置环境变量
export ENV=dev

# 启动服务器
python server/mcp_server.py
```

这样可以避免生成不必要的日志文件，保持项目目录整洁。

## 生产部署建议

生产环境建议启用文件日志：

```bash
# Docker 部署（默认已配置为 prod）
docker-compose up -d

# 查看应用日志
tail -f /data/logs/stock_arbitrade_notify_mcp/mcp_server_$(date +%Y%m%d).log
```

便于问题追踪和日志审计。
