"""
MCP服务器测试脚本
测试fetch_qdii_candidates和send_wechat工具
使用 SSE 传输方式
"""
import httpx
import json
import sys

# MCP 服务器配置
SERVER_URL = "http://127.0.0.1:4567"
request_id = 0

def get_next_request_id():
    """获取下一个请求ID"""
    global request_id
    request_id += 1
    return request_id

def mcp_call(method: str, params: dict = None):
    """
    发送MCP JSON-RPC请求（通过 HTTP/SSE）
    
    Args:
        method: JSON-RPC方法名
        params: 方法参数
    """
    payload = {
        "jsonrpc": "2.0",
        "id": get_next_request_id(),
        "method": method,
        "params": params or {}
    }
    
    try:
        # 发送HTTP POST请求到SSE服务器
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                SERVER_URL,  # FastMCP的SSE端点通常是根路径
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP请求失败: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析失败: {e}")

def test_server_health():
    """测试服务器健康状态"""
    print("=" * 50)
    print("测试1: 检查服务器健康状态")
    print("=" * 50)
    try:
        # 尝试初始化MCP连接
        result = mcp_call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        print(f"[OK] MCP服务器响应成功")
        print(f"[OK] 服务器信息: {result.get('result', {}).get('serverInfo', {})}")
        print(f"[OK] 协议版本: {result.get('result', {}).get('protocolVersion', 'unknown')}\n")
        return True
    except Exception as e:
        print(f"[ERROR] 服务器无响应: {e}\n")
        return False

def test_qdii_candidates():
    """测试QDII候选工具"""
    print("=" * 50)
    print("测试2: 获取QDII溢价套利候选")
    print("=" * 50)
    
    # 测试不同的阈值
    thresholds = [1.0, 2.0, 3.0]
    
    for threshold in thresholds:
        try:
            print(f"\n尝试获取溢价率 >= {threshold}% 的基金...")
            
            # 使用MCP JSON-RPC调用工具
            result = mcp_call("tools/call", {
                "name": "fetch_qdii_candidates",
                "arguments": {"threshold": threshold}
            })
            
            if "result" in result:
                content = result["result"].get("content", [])
                # 解析返回的内容
                if content and len(content) > 0:
                    candidates = content[0].get("text", "[]")
                    
                    # 处理FastMCP的json_response=True模式，可能直接返回Python对象
                    if isinstance(candidates, str):
                        try:
                            candidates = json.loads(candidates)
                        except json.JSONDecodeError as e:
                            print(f"[ERROR] JSON解析失败: {e}")
                            print(f"[DEBUG] 原始数据: {candidates[:200]}...")
                            candidates = []
                    elif isinstance(candidates, dict):
                        # 如果返回的是单个字典，将其包装成列表
                        candidates = [candidates]
                    elif isinstance(candidates, list):
                        # 已经是列表，直接使用
                        pass
                    else:
                        print(f"[ERROR] 数据类型错误: 期望list或dict，实际是{type(candidates)}")
                        print(f"[DEBUG] 数据内容: {str(candidates)[:200]}")
                        candidates = []
                    
                    print(f"[OK] 成功获取 {len(candidates)} 只基金")
                    
                    # 显示前3只基金
                    if candidates and isinstance(candidates, list):
                        print(f"\n前{min(3, len(candidates))}只基金:")
                        for i, fund in enumerate(candidates[:3], 1):
                            if isinstance(fund, dict):
                                print(f"  {i}. {fund.get('名称', 'N/A')} ({fund.get('代码', 'N/A')})")
                                print(f"     溢价率: {fund.get('T-1溢价率', 'N/A')}%")
                                print(f"     申购状态: {fund.get('申购状态', 'N/A')}")
                            else:
                                print(f"  {i}. [数据格式错误: {type(fund)}]")
                    else:
                        print(f"  暂无满足条件的基金")
                else:
                    print(f"[ERROR] 返回数据格式错误: {result}")
            elif "error" in result:
                print(f"[ERROR] MCP错误: {result['error']}")
            else:
                print(f"[ERROR] 未知响应格式: {result}")
                
        except TimeoutError:
            print(f"[ERROR] 请求超时")
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON解析错误: {e}")
        except Exception as e:
            print(f"[ERROR] 错误: {e}")
    
    print()

def test_send_wechat():
    """测试微信通知工具（需要配置SCT_KEY）"""
    print("=" * 50)
    print("测试3: 发送微信通知（可选）")
    print("=" * 50)
    
    # 询问是否测试微信通知
    print("\n注意: 这将发送真实的微信通知。")
    user_input = input("是否测试微信通知功能? (y/N): ").strip().lower()
    
    if user_input != 'y':
        print("跳过微信通知测试\n")
        return
    
    try:
        print("\n发送测试通知...")
        
        # 使用MCP JSON-RPC调用工具
        result = mcp_call("tools/call", {
            "name": "send_wechat",
            "arguments": {
                "title": "MCP Server 测试",
                "desp": "这是来自MCP服务器的测试通知。\n\n服务器运行正常！"
            }
        })
        
        if "result" in result:
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                response_text = content[0].get("text", "{}")
                if isinstance(response_text, str):
                    response_data = json.loads(response_text)
                else:
                    response_data = response_text
                print(f"[OK] 通知发送成功")
                print(f"  响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"[ERROR] 返回数据格式错误: {result}")
        elif "error" in result:
            print(f"[ERROR] MCP错误: {result['error']}")
        else:
            print(f"[ERROR] 未知响应格式: {result}")
            
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
    
    print()

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("MCP Server 测试套件")
    print("=" * 50 + "\n")
    
    print("[INFO] 连接到 MCP 服务器: " + SERVER_URL)
    print("[INFO] 请确保 MCP 服务器已在另一个终端启动: python mcp_server.py\n")
    
    # 测试1: 服务器健康检查
    if not test_server_health():
        print("[WARNING] 服务器初始化失败，请检查服务器是否正在运行")
        return
    
    # 测试2: QDII候选工具
    test_qdii_candidates()
    
    # 测试3: 微信通知工具（可选）
    # test_send_wechat()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()

