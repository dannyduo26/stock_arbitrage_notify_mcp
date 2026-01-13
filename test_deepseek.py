import json
from openai import OpenAI
import os

def test_deepseek():
    print("Loading config...")
    if not os.path.exists("config.json"):
        print("config.json not found")
        return

    with open("config.json", "r") as f:
        config = json.load(f)
    
    print(f"Config loaded. Base URL: {config.get('deepseek_base_url')}")

    client = OpenAI(
        api_key=config["deepseek_api_key"],
        base_url=config["deepseek_base_url"]
    )

    print("Sending request to DeepSeek...")
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say Hello DeepSeek!"},
            ],
            max_tokens=50,
        )
        print("Response received:")
        print(resp.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_deepseek()
