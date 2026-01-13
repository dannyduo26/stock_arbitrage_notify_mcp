'''
Author: duyulin@kingsoft.com
Date: 2025-11-24 18:05:08
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-12-05 16:52:41
'''
from typing import Any, Dict, List
from mcp.server import FastMCP
import httpx
import jisilu_mcp_server as j
import wechat_server as w

mcp = FastMCP("arbitrage-suite", json_response=True, port=4567)

@mcp.tool(description="获取QDII溢价套利候选列表")
def fetch_qdii_candidates(threshold: float = 2.0) -> str:
    """
    获取QDII溢价套利候选列表

    Args:
        threshold: 溢价率阈值，默认为2.0%
    """
    import json
    result = j.qdii_candidates(threshold)
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="发送微信通知")
def send_wechat(title: str, desp: str) -> str:
    """
    发送微信通知

    Args:
        title: 通知的标题
        desp: 通知的详细内容
    """
    import json
    result = w.send_wechat(title, desp)
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    print(f"Starting MCP server with args: {sys.argv}", file=sys.stderr)
    mcp.run(transport="sse")  # 使用SSE传输方式