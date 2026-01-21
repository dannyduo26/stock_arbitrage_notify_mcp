# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（lxml 需要）
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY mcp_server.py .
COPY logging_config.py .
COPY config.json .
COPY modules/ modules/

# 暴露端口（默认 4567）
EXPOSE 4567

# 创建日志目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PORT=4567
ENV PYTHONUNBUFFERED=1
ENV ENV=prod

# 运行 MCP 服务器
CMD ["python", "mcp_server.py"]
