import os
import requests
import json
from openai import OpenAI

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Use DeepSeek configuration
client = OpenAI(
    api_key=config["deepseek_api_key"],
    base_url=config["deepseek_base_url"]
)

MCP_BASE = os.getenv("MCP_BASE", "http://127.0.0.1:4096")


def call_mcp_tool(tool_name: str, params: dict = None):
    payload = {"tool": tool_name, "params": params or {}}
    res = requests.post(f"{MCP_BASE}/call", json=payload, timeout=10)
    res.raise_for_status()
    return res.json()


def ask_chatgpt(system_prompt: str, user_prompt: str):
    # Use DeepSeek via OpenAI compatible API
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    # 1) 调用本地 MCP server
    data = call_mcp_tool("get_items")
    items = data.get("result", [])

    # 2) 构建 prompt
    system = "You are an assistant that summarizes a list of items with id/title/value into a short report."
    user = f"Here are the items from the MCP server:\n{items}\nPlease summarize the list and highlight the highest value."

    # 3) 调用 ChatGPT
    out = ask_chatgpt(system, user)
    print("\n=== MODEL RESPONSE ===\n")
    print(out)