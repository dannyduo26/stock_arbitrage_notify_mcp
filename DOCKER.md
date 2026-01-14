# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 命令

#### 1. 构建镜像

```bash
docker build -t mcp-arbitrage-server .
```

#### 2. 运行容器

```bash
docker run -d \
  --name mcp-server \
  -p 4567:4567 \
  -v $(pwd)/config.json:/app/config.json:ro \
  mcp-arbitrage-server
```

## 环境变量配置

可以通过环境变量覆盖默认配置：

```bash
docker run -d \
  --name mcp-server \
  -p 4567:4567 \
  -e PORT=8080 \
  -e SCT_KEY=your_sct_key_here \
  mcp-arbitrage-server
```

## 访问服务

服务启动后，可以通过以下地址访问：

- **SSE 端点**: `http://localhost:4567/sse`
- **健康检查**: 运行测试脚本

```bash
# 在宿主机上运行测试
python test_mcp_server.py
```

## 常用命令

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs -f mcp-server

# 进入容器
docker exec -it mcp-server /bin/bash

# 停止容器
docker stop mcp-server

# 删除容器
docker rm mcp-server

# 删除镜像
docker rmi mcp-arbitrage-server
```

## 生产环境建议

### 1. 使用环境变量管理敏感信息

创建 `.env` 文件（不要提交到 Git）：

```env
SCT_KEY=your_sct_key_here
DEEPSEEK_API_KEY=your_api_key_here
```

修改 `docker-compose.yml`：

```yaml
services:
  mcp-server:
    env_file:
      - .env
```

### 2. 持久化日志

```yaml
services:
  mcp-server:
    volumes:
      - ./logs:/app/logs
```

### 3. 资源限制

```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
```

### 4. 健康检查

```yaml
services:
  mcp-server:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4567/sse"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker logs mcp-server

# 检查容器状态
docker inspect mcp-server
```

### 端口已被占用

修改端口映射：

```bash
docker run -p 8080:4567 mcp-arbitrage-server
```

### 配置文件找不到

确保 `config.json` 存在并且挂载路径正确：

```bash
# 检查配置文件
ls -la config.json

# 使用绝对路径挂载
docker run -v /absolute/path/to/config.json:/app/config.json:ro ...
```

## 更新部署

```bash
# 1. 停止并删除旧容器
docker-compose down

# 2. 重新构建镜像
docker-compose build

# 3. 启动新容器
docker-compose up -d
```
