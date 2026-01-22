import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# 添加父目录到系统路径，以便导入 config 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 配置日志
from config.logging_config import setup_logging
logger = setup_logging()

# 加载配置
# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(ROOT_DIR, "config.json")

try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error(f"❌ 配置文件未找到: {config_path}")
    logger.error("请确保从项目根目录运行脚本，或 config.json 文件存在")
    sys.exit(1)

# 使用 DeepSeek 配置
client = OpenAI(
    api_key=config["deepseek_api_key"],
    base_url=config["deepseek_base_url"]
)

# MCP 服务器地址
# MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:4567/sse")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://175.24.206.252:4567/sse")



async def get_available_tools() -> List[Dict[str, Any]]:
    """
    获取 MCP 服务器提供的所有可用工具
    
    Returns:
        工具列表，每个工具包含 name, description, inputSchema
    """
    async with sse_client(MCP_SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化会话
            await session.initialize()
            
            # 列出所有工具
            tools_list = await session.list_tools()
            
            # 转换为字典列表
            tools = []
            for tool in tools_list.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            return tools


async def call_mcp_tool(tool_name: str, arguments: dict = None):
    """
    调用 MCP 工具
    
    Args:
        tool_name: 工具名称
        arguments: 工具参数
        
    Returns:
        工具调用结果
    """
    async with sse_client(MCP_SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化会话
            await session.initialize()
            
            # 调用工具
            result = await session.call_tool(tool_name, arguments=arguments or {})
            
            # 解析结果
            if result.content:
                return json.loads(result.content[0].text)
            return None


def format_tools_for_llm(tools: List[Dict[str, Any]]) -> str:
    """
    将工具列表格式化为适合 LLM 理解的文本
    
    Args:
        tools: 工具列表
        
    Returns:
        格式化后的工具描述文本
    """
    formatted = "可用的 MCP 工具列表:\n\n"
    for i, tool in enumerate(tools, 1):
        formatted += f"{i}. 工具名称: {tool['name']}\n"
        formatted += f"   描述: {tool['description']}\n"
        formatted += f"   参数: {json.dumps(tool['inputSchema'], ensure_ascii=False, indent=2)}\n\n"
    return formatted


def ask_deepseek_with_tools(user_query: str, tools_info: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    使用 DeepSeek API 生成回复，支持工具调用
    
    Args:
        user_query: 用户查询
        tools_info: 工具信息
        conversation_history: 对话历史
        
    Returns:
        包含 action（"tool_call" 或 "final_answer"）、tool_name、arguments 或 answer 的字典
    """
    system_prompt = f"""你是一个专业的金融分析助手,能够使用提供的 MCP 工具来获取数据并进行分析。

{tools_info}

**重要规则:**
1. 你必须完成用户要求的所有任务步骤,不能遗漏任何一个
2. 如果用户要求发送通知,你必须在完成数据分析后调用 send_wechat 工具
3. 只有在完成所有任务步骤后,才能返回 final_answer
4. 每次只能调用一个工具,多个任务需要分多轮完成

**工作流程:**
- 第一步:分析用户需求,列出需要完成的所有任务步骤
- 第二步:按顺序执行每个步骤,每次调用一个工具
- 第三步:确认所有步骤都已完成后,再给出最终答案

**返回格式:**
- 如果需要调用工具:
{{
  "action": "tool_call",
  "tool_name": "工具名称",
  "arguments": {{"参数名": "参数值"}},
  "reason": "为什么选择这个工具和参数"
}}

- 如果所有任务步骤都已完成,可以给出最终答案:
{{
  "action": "final_answer",
  "answer": "你的分析报告或回答"
}}

请只返回 JSON,不要包含其他文字。"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)
    
    # 添加用户查询
    messages.append({"role": "user", "content": user_query})
    
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
    )
    
    content = resp.choices[0].message.content.strip()
    
    # 尝试解析 JSON
    try:
        # 移除可能的代码块标记
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"⚠️  解析 LLM 响应失败: {e}")
        logger.debug(f"原始响应: {content}")
        return {
            "action": "final_answer",
            "answer": f"抱歉，我无法正确解析响应。原始内容：{content}"
        }


async def main():
    """主函数 - AI Agent 模式"""
    logger.info("🤖 启动 AI Agent 模式...")
    logger.info("=" * 60)
    
    # 1) 获取可用工具列表
    logger.info("📋 正在获取 MCP 服务器工具列表...")
    tools = await get_available_tools()
    logger.info(f"✅ 发现 {len(tools)} 个可用工具:")
    for tool in tools:
        logger.info(f"   - {tool['name']}: {tool['description']}")
    
    tools_info = format_tools_for_llm(tools)
    
    # 2) 用户查询
    user_query = """请完成以下任务:
1. 获取当前QDII基金的溢价套利候选列表
2. 分析这些基金的溢价情况
3. 将分析结果通过微信通知发送给我

注意:必须完成所有3个步骤,不能遗漏发送微信通知。"""
    logger.info(f"💬 用户查询: {user_query}")
    logger.info("=" * 60)
    
    # 3) AI Agent 循环
    conversation_history = []
    max_iterations = 5  # 最多迭代5次，避免无限循环
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"🔄 第 {iteration} 轮思考...")
        
        # 让 LLM 决定下一步行动
        decision = ask_deepseek_with_tools(
            user_query if iteration == 1 else "请根据已获得的信息,继续执行下一个未完成的任务步骤。如果所有步骤都已完成,请给出最终答案。",
            tools_info,
            conversation_history
        )
        
        logger.info(f"💡 LLM 决策: {decision.get('action')}")
        
        if decision.get("action") == "tool_call":
            # 调用工具
            tool_name = decision.get("tool_name")
            arguments = decision.get("arguments", {})
            reason = decision.get("reason", "")
            
            logger.info(f"🔧 调用工具: {tool_name}")
            logger.info(f"   参数: {json.dumps(arguments, ensure_ascii=False)}")
            logger.info(f"   原因: {reason}")
            
            try:
                result = await call_mcp_tool(tool_name, arguments)
                logger.info(f"✅ 工具调用成功")
                
                # 将工具调用结果添加到对话历史
                conversation_history.append({
                    "role": "assistant",
                    "content": json.dumps(decision, ensure_ascii=False)
                })
                conversation_history.append({
                    "role": "user",
                    "content": f"工具 {tool_name} 执行结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
                })
                
            except Exception as e:
                logger.error(f"❌ 工具调用失败: {e}")
                conversation_history.append({
                    "role": "user",
                    "content": f"工具调用失败: {str(e)}"
                })
        
        elif decision.get("action") == "final_answer":
            # 给出最终答案
            answer = decision.get("answer", "")
            logger.info("\n" + "=" * 60)
            logger.info("📊 最终分析报告:")
            logger.info("=" * 60)
            logger.info(answer)
            logger.info("=" * 60)
            break
        
        else:
            logger.warning(f"⚠️  未知的 action: {decision.get('action')}")
            break
    
    if iteration >= max_iterations:
        logger.warning("⚠️  达到最大迭代次数，终止执行")


if __name__ == "__main__":
    asyncio.run(main())