import json
import os
import sys
from openai import OpenAI

# 添加父目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 配置日志
from config.logging_config import setup_logging
logger = setup_logging()

def test_deepseek_reasoner_response():
    """测试 deepseek-reasoner 的响应格式"""
    logger.info("🧪 测试 deepseek-reasoner 响应格式...")
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    if not os.path.exists(config_path):
        logger.error(f"❌ 配置文件未找到: {config_path}")
        return
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    client = OpenAI(
        api_key=config["deepseek_api_key"],
        base_url=config["deepseek_base_url"]
    )
    
    # 测试请求
    system_prompt = """你是一个专业的助手。请以 JSON 格式返回你的回答。

返回格式:
{
  "action": "final_answer",
  "answer": "你的回答内容"
}

请只返回 JSON,不要包含其他文字。"""
    
    logger.info("📤 发送请求到 deepseek-reasoner...")
    try:
        resp = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请用一句话介绍你自己"},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        logger.info("✅ 收到响应")
        logger.info("=" * 60)
        
        # 提取响应字段
        message = resp.choices[0].message
        
        # 检查 reasoning_content 字段
        reasoning_content = getattr(message, 'reasoning_content', None)
        content = message.content
        
        logger.info("📋 响应结构:")
        logger.info(f"  - 是否有 reasoning_content: {'是' if reasoning_content else '否'}")
        logger.info(f"  - 是否有 content: {'是' if content else '否'}")
        logger.info("=" * 60)
        
        if reasoning_content:
            logger.info("🧠 推理过程 (reasoning_content):")
            logger.info(reasoning_content)
            logger.info("=" * 60)
        
        if content:
            logger.info("💬 最终答案 (content):")
            logger.info(content)
            logger.info("=" * 60)
            
            # 尝试解析 JSON
            try:
                # 移除可能的代码块标记
                clean_content = content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:]
                if clean_content.startswith("```"):
                    clean_content = clean_content[3:]
                if clean_content.endswith("```"):
                    clean_content = clean_content[:-3]
                clean_content = clean_content.strip()
                
                parsed = json.loads(clean_content)
                logger.info("✅ JSON 解析成功:")
                logger.info(json.dumps(parsed, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️  JSON 解析失败: {e}")
        
        # 打印完整的响应对象(用于调试)
        logger.info("=" * 60)
        logger.info("🔍 完整响应对象属性:")
        for attr in dir(message):
            if not attr.startswith('_'):
                try:
                    value = getattr(message, attr)
                    if not callable(value):
                        logger.info(f"  - {attr}: {type(value).__name__}")
                except:
                    pass
        
    except Exception as e:
        logger.error(f"❌ 请求失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_deepseek_reasoner_response()
