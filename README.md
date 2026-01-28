# MCP Arbitrage Suite

基于 MCP (Model Context Protocol) 的 QDII/LOF 溢价套利和微信通知服务套件。

## 📖 项目简介

本项目提供了一个基于 SSE 传输的 MCP 服务器，集成了以下功能：

- **QDII/LOF 溢价套利**：从集思录抓取 QDII 和 LOF 基金数据，筛选满足溢价条件的套利机会
- **微信通知**：通过 Server 酱发送微信消息通知
- **A股行情**：获取A股实时和历史行情数据
- **期货行情**：获取国内期货实时行情和主力合约列表
- **Docker 部署**：支持 Docker Compose 一键部署
- **生产级日志**：环境变量控制的日志系统

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

创建 `config.json` 文件，填入必要的配置信息：

```json
{
  "deepseek_base_url": "https://api.deepseek.com",
  "deepseek_api_key": "你的DeepSeek API Key",
  "qwen_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "qwen_api_key": "你的Qwen API Key",
  "SCT_KEY": "你的Server酱Key"
}
```

**配置说明：**

- `SCT_KEY`: Server 酱的推送 Key，用于发送微信通知（在 [Server 酱官网](https://sct.ftqq.com/) 获取）
- `deepseek_api_key`: DeepSeek API 密钥（如需使用 AI 功能）
- `deepseek_base_url`: DeepSeek API 服务地址
- `qwen_api_key`: 通义千问 API 密钥（可选）
- `qwen_base_url`: 通义千问 API 服务地址（可选）

### 环境变量（可选）

可以通过环境变量覆盖配置文件中的设置：

- **ENV**: 运行环境，可选值 `prod`（生产）或 `dev`（开发）
  - `prod`: 日志同时输出到文件（`/app/logs/`）和控制台
  - `dev`: 日志仅输出到控制台（默认）
- **PORT**: 服务端口，默认 `4567`
- **SCT_KEY**: Server 酱推送密钥，优先级高于配置文件

```bash
# 生产环境启动（启用文件日志）
ENV=prod python server/mcp_server.py

# 开发环境启动（仅控制台日志）
ENV=dev python server/mcp_server.py
```

### 启动 MCP 服务器

```bash
python server/mcp_server.py
# 或者从项目根目录
python .\server\mcp_server.py
```

服务器将在 `http://127.0.0.1:4567` 启动，使用 SSE 传输方式。

## 🔧 可用工具

### 1. fetch_qdii_candidates

获取 QDII/LOF 溢价套利候选列表。

**参数：**

- `threshold` (float, optional): 溢价率阈值，默认为 2.0%

**数据来源：**

- QDII 基金数据（集思录 QDII API）
- LOF 基金数据（集思录 LOF API）

**返回：**
返回满足以下条件的基金列表：

- T-1 溢价率 > threshold
- 申购状态不是"暂停申购"或"开放申购"（通常是"限额申购"）

**示例：**

```python
# 获取溢价率大于2%的基金
candidates = fetch_qdii_candidates(threshold=2.0)
```

**返回数据格式：**

```json
[
  {
    "代码": "159920",
    "名称": "恒生ETF",
    "T-1溢价率": 2.5,
    "申购状态": "限额申购"
  }
]
```

### 2. send_wechat

发送微信通知消息。

**参数：**

- `title` (str, required): 通知的标题
- `desp` (str, required): 通知的详细内容

**示例：**

```python
send_wechat(
    title="QDII套利提醒",
    desp="发现3只满足条件的套利基金"
)
```

### 3. get_stock_realtime

获取A股单只股票的实时行情数据。

**参数：**

- `symbol` (str, required): 股票代码，6位数字，如 "000001" 或 "600000"

**返回数据格式：**

```json
{
  "success": true,
  "symbol": "000001",
  "data": {
    "代码": "000001",
    "名称": "平安银行",
    "最新价": 12.34,
    "涨跌幅": 1.23,
    "涨跌额": 0.15,
    "成交量": 1234567,
    "成交额": 15234567890,
    "振幅": 2.5,
    "最高": 12.5,
    "最低": 12.2,
    "今开": 12.25,
    "昨收": 12.19
  }
}
```

### 4. get_stock_hist

获取A股单只股票的历史行情数据（最近10条记录）。

**参数：**

- `symbol` (str, required): 股票代码，6位数字，如 "000001" 或 "600000"
- `period` (str, optional): 周期，可选 "daily"(日K), "weekly"(周K), "monthly"(月K)，默认为 "daily"
- `adjust` (str, optional): 复权类型，可选 ""(不复权), "qfq"(前复权), "hfq"(后复权)，默认为 ""

**返回数据格式：**

```json
{
  "success": true,
  "symbol": "000001",
  "period": "daily",
  "adjust": "qfq",
  "count": 10,
  "data": [
    {
      "日期": "2024-01-15",
      "开盘": 12.25,
      "收盘": 12.34,
      "最高": 12.5,
      "最低": 12.2,
      "成交量": 1234567,
      "成交额": 15234567890
    }
  ]
}
```

### 5. get_futures_realtime

获取国内期货单只合约的实时行情数据。

**参数：**

- `symbol` (str, required): 期货代码，如 "RB2505" 或 "AG2604"

**返回数据格式：**

```json
{
  "success": true,
  "symbol": "RB2505",
  "name": "螺纹钢2505",
  "price": 3850.0,
  "open": 3840.0,
  "high": 3860.0,
  "low": 3835.0,
  "volume": 123456,
  "position": 234567,
  "time": "15:00:00"
}
```

### 6. get_futures_main_list

获取国内期货主力合约行情列表（全部数据）。

**参数：** 无

**返回数据格式：**

```json
{
  "success": true,
  "count": 50,
  "data": [
    {
      "代码": "RB2505",
      "名称": "螺纹钢2505",
      "最新价": 3850.0,
      "涨跌": 15.0,
      "成交量": 123456
    }
  ]
}
```

## 📁 项目结构

```
mcp/
├── README.md                          # 项目说明文档
├── DOCKER.md                          # Docker 部署文档
├── LOGGING.md                         # 日志配置文档
├── requirements.txt                   # Python 依赖列表
├── config.json                        # 配置文件（需自行创建）
├── Dockerfile                         # Docker 镜像构建文件
├── docker-compose.yml                 # Docker Compose 配置
├── .dockerignore                      # Docker 构建排除文件
├── deploy.sh                          # 自动部署脚本
├── config/                            # 配置模块目录
│   ├── __init__.py                    # Python 包初始化文件
│   └── logging_config.py              # 日志配置模块
├── server/                            # 服务器模块目录
│   ├── mcp_server.py                  # MCP 服务器主程序（SSE 传输）
│   └── modules/                       # 业务逻辑模块
│       ├── __init__.py                # Python 包初始化文件
│       ├── jisilu_mcp_server.py       # 集思录数据抓取模块（QDII + LOF）
│       ├── wechat_server.py           # 微信通知模块
│       ├── stock_server.py            # A股行情数据模块
│       └── futures_server.py          # 期货行情数据模块
├── client/                            # 客户端脚本目录
│   ├── __init__.py                    # Python 包初始化文件
│   ├── notify_arbitrage_mcp_client.py # AI Agent 模式客户端
│   └── deepseek_client.py             # DeepSeek API 客户端
└── tests/                             # 测试脚本目录
    ├── __init__.py                    # Python 包初始化文件
    ├── test_mcp_server.py             # MCP 服务器测试脚本
    ├── test_mcp_server_demo.py        # MCP 服务器演示测试
    ├── test_stock_server.py           # A股行情模块测试脚本
    ├── test_deepseek.py               # DeepSeek 客户端测试脚本
    └── test_deepseek_reasoner.py      # DeepSeek Reasoner 测试脚本
```

## 💻 使用示例

### 基本调用示例

```python
import requests

MCP_BASE = "http://127.0.0.1:4096"

# 调用QDII候选工具
def call_mcp_tool(tool_name: str, params: dict = None):
    payload = {"tool": tool_name, "params": params or {}}
    res = requests.post(f"{MCP_BASE}/call", json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

# 获取溢价率≥3%的基金
candidates = call_mcp_tool("fetch_qdii_candidates", {"threshold": 3.0})
print(candidates)

# 发送微信通知
result = call_mcp_tool("send_wechat", {
    "title": "套利提醒",
    "desp": f"发现 {len(candidates)} 只满足条件的基金"
})
print(result)
```

### 使用配置文件

项目提供了 `mcp_http_config.json` 配置文件示例，您可以在支持 MCP 协议的客户端中使用：

```json
{
  "mcpServers": {
    "arbitrage-suite": {
      "type": "http",
      "url": "http://127.0.0.1:4096",
      "description": "QDII溢价套利和微信通知服务"
    }
  }
}
```

## 🔍 数据来源

基金数据从以下来源抓取（按优先级）：

### QDII 和 LOF 数据

1. **集思录 QDII API**：`https://www.jisilu.cn/data/qdii/qdii_list/`
2. **集思录 LOF API**：`https://www.jisilu.cn/data/lof/index_lof_list/`
3. **AKShare 数据接口**（备用）：当 API 失败时自动切换

## ⚙️ 技术栈

- **MCP 框架**: FastMCP 2.14+ - 快速构建 MCP 服务器
- **传输协议**: SSE (Server-Sent Events)
- **HTTP 客户端**: httpx - 异步 HTTP 请求
- **数据解析**: BeautifulSoup4 + lxml
- **金融数据**: AKShare（集思录 API + AKShare 备用）
- **容器化**: Docker + Docker Compose
- **Web 服务器**: Uvicorn（FastMCP 内置）

## 📝 依赖说明

```txt
httpx>=0.28.1           # HTTP 客户端
beautifulsoup4>=4.14.2  # HTML 解析
lxml>=6.0.2             # XML/HTML 处理
akshare>=1.17.87        # 金融数据接口
mcp>=1.21.2             # MCP 协议框架
fastmcp                 # FastMCP 服务器框架
```

## 🐳 Docker 部署

### 快速开始

```bash
# 使用 Docker Compose（推荐）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 更新 Docker 服务

**方式一：使用自动更新脚本（推荐）**

```bash
# Linux/Mac
chmod +x update_docker.sh
./update_docker.sh

# Windows PowerShell
.\update_docker.ps1
```

**方式二：手动更新**

```bash
# 停止并删除旧容器
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 启动新容器
docker-compose up -d
```

详细的更新步骤和故障排查请查看项目中的 `update_docker.sh` 或 `update_docker.ps1` 脚本。

### 部署文档

详细部署说明请查看 [DOCKER.md](DOCKER.md)

### 端口配置

- **服务端口**: 4567（可通过环境变量 `PORT` 修改）
- **SSE 端点**: `http://localhost:4567/sse`

## 🔬 测试

### 运行测试脚本

```bash
# 确保服务器正在运行
python server/mcp_server.py

# 在另一个终端运行测试
python tests/test_mcp_server.py
```

### AI Agent 客户端示例

项目提供了一个完整的 AI Agent 客户端示例，它结合了 DeepSeek 大模型和 MCP 工具调用：

```bash
# 运行 AI Agent 客户端
python client/notify_arbitrage_mcp_client.py
```

该客户端会：

1. 连接到 MCP 服务器获取可用工具
2. 使用 DeepSeek 分析用户需求并决策调用哪些工具
3. 自动执行工具调用并生成分析报告
4. 通过微信发送通知

### 测试输出示例

```
✅ 已成功建立连接并初始化。
[可用工具]: ['fetch_qdii_candidates', 'send_wechat', 'get_stock_realtime', 'get_stock_hist', 'get_futures_realtime', 'get_futures_main_list']

共 7 只基金:
  1. 国投白银LOF (161226)
     溢价率: 50.86%
     申购状态: 限100
  2. 黄金主题LOF (161116)
     溢价率: 13.82%
     申购状态: 限10
  ...
```

## 🛠️ 开发说明

### MCP 传输方式

本项目使用 **SSE (Server-Sent Events) 传输方式**：

```python
# mcp_server.py
mcp.run(transport="sse", host="0.0.0.0", port=4567)
```

### 扩展新工具

在 `mcp_server.py` 中添加新的 MCP 工具：

```python
@mcp.tool(description="工具描述")
def your_tool_name(param1: str, param2: int) -> dict:
    """
    工具说明文档

    Args:
        param1: 参数1说明
        param2: 参数2说明
    """
    # 实现逻辑
    return {"result": "success"}
```

## 📄 许可证

本项目遵循 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 注意事项

1. **配置安全**：请勿将 `config.json` 提交到版本控制系统，注意保护 API 密钥
2. **频率限制**：抓取集思录数据时请注意访问频率，避免被封 IP
3. **Server 酱额度**：免费版 Server 酱有推送次数限制，请合理使用
4. **网络连接**：首次运行需要下载数据，请确保网络连接稳定
5. **反向代理**：如使用 Nginx/Apache 代理，需特殊配置 SSE 支持（参见 SSE_TROUBLESHOOTING.md）
6. **日志文件**：生产环境（`ENV=prod`）会在 `/app/logs/` 生成日志文件

## 📚 相关文档

### 项目文档

- [Docker 部署指南](DOCKER.md)
- [日志配置说明](LOGGING.md)
- [SSE 故障排查](SSE_TROUBLESHOOTING.md)

### 外部资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://gofastmcp.com)
- [Server 酱文档](https://sct.ftqq.com/sendkey)
- [集思录 QDII 页面](https://www.jisilu.cn/data/qdii/)
- [集思录 LOF 页面](https://www.jisilu.cn/data/lof/)
- [AKShare 文档](https://akshare.akfamily.xyz/)

## 🌟 特性亮点

- ✅ **多数据源**：同时支持 QDII 和 LOF 基金数据
- ✅ **行情数据**：提供 A股实时/历史行情和期货主力合约数据
- ✅ **自动切换**：API 失败时自动切换到备用数据源
- ✅ **生产就绪**：Docker 部署 + 环境变量配置 + 日志管理
- ✅ **实时通知**：Server 酱微信推送
- ✅ **易于扩展**：基于 FastMCP 框架，轻松添加新工具
- ✅ **完整测试**：提供完整的测试脚本和示例
