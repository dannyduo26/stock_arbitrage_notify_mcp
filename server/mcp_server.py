'''
Author: duyulin@kingsoft.com
Date: 2025-11-24 18:05:08
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-12-05 16:52:41
'''
import os
import sys
import logging
from typing import Any, Dict, List
from fastmcp import FastMCP
import httpx

# 添加父目录到系统路径，以便导入 config 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules import jisilu_mcp_server as j
from modules import wechat_server as w
from modules import stock_server as s
from modules import futures_server as f

# 配置日志
from config.logging_config import setup_logging
logger = setup_logging()

# 初始化 MCP 服务器
mcp = FastMCP("arbitrage-suite")

@mcp.tool(description="获取QDII溢价套利候选列表")
def fetch_qdii_candidates(threshold: float = 2.0) -> str:
    """
    获取QDII溢价套利候选列表

    Args:
        threshold: 溢价率阈值，默认为2.0%
    """
    import json
    logger.info(f"调用 fetch_qdii_candidates, threshold={threshold}")
    result = j.qdii_candidates(threshold)
    logger.info(f"获取到 {len(result)} 只候选基金")
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="发送微信通知")
async def send_wechat(title: str, desp: str) -> str:
    """
    发送微信通知

    Args:
        title: 通知的标题
        desp: 通知的详细内容
    """
    import json
    logger.info(f"调用 send_wechat, title={title}")
    result = await w.send_wechat(title, desp)
    logger.info(f"微信通知发送完成: {result.get('status_code', 'unknown')}")
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="获取A股单只股票的实时行情数据")
def get_stock_realtime(symbol: str) -> str:
    """
    获取A股单只股票的实时行情数据

    Args:
        symbol: 股票代码，6位数字，如 "000001" 或 "600000"
    """
    import json
    logger.info(f"调用 get_stock_realtime, symbol={symbol}")
    result = s.get_stock_realtime(symbol)
    if result.get("success"):
        logger.info(f"成功获取股票 {symbol} 的实时行情数据")
    else:
        logger.warning(f"获取股票 {symbol} 实时行情失败: {result.get('error', 'unknown')}")
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="获取A股单只股票的历史行情数据")
def get_stock_hist(symbol: str, period: str = "daily", adjust: str = "") -> str:
    """
    获取A股单只股票的历史行情数据（最近10条记录）

    Args:
        symbol: 股票代码，6位数字，如 "000001" 或 "600000"
        period: 周期，可选 "daily"(日K), "weekly"(周K), "monthly"(月K)，默认为 "daily"
        adjust: 复权类型，可选 ""(不复权), "qfq"(前复权), "hfq"(后复权)，默认为 ""
    """
    import json
    logger.info(f"调用 get_stock_hist, symbol={symbol}, period={period}, adjust={adjust}")
    result = s.get_stock_hist(symbol, period, adjust)
    if result.get("success"):
        logger.info(f"成功获取股票 {symbol} 的历史行情数据，返回 {result.get('count', 0)} 条记录")
    else:
        logger.warning(f"获取股票 {symbol} 历史行情失败: {result.get('error', 'unknown')}")
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="获取国内期货单只合约的实时行情数据")
def get_futures_realtime(symbol: str) -> str:
    """
    获取国内期货单只合约的实时行情数据

    Args:
        symbol: 期货代码，如 "RB2505" 或 "AG2604"
    """
    import json
    logger.info(f"调用 get_futures_realtime, symbol={symbol}")
    result = f.get_futures_realtime(symbol)
    if result.get("success"):
        logger.info(f"成功获取期货 {symbol} 的实时行情数据")
    else:
        logger.warning(f"获取期货 {symbol} 实时行情失败: {result.get('error', 'unknown')}")
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="获取国内期货主力合约行情列表（全部数据）")
def get_futures_main_list() -> str:
    """
    获取国内期货主力合约行情列表（全部数据）
    """
    import json
    logger.info("调用 get_futures_main_list")
    result = f.get_futures_main_list()
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    # 获取端口，默认使用 4567
    port = int(os.getenv("PORT", 4567))
    
    logger.info(f"启动 MCP 服务器: arbitrage-suite")
    logger.info(f"监听端口: {port}")
    logger.info(f"传输协议: SSE")
    
    # 以 SSE 模式启动服务器，使其支持 HTTP 远程调用
    mcp.run(
        transport="sse", 
        host="0.0.0.0", 
        port=port
    )