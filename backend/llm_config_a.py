
import os
from langchain_openai import ChatOpenAI

def get_llm():
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    
    if not api_token:
        print("❌ 未设置 HUGGINGFACE_API_TOKEN 环境变量")
        return None
    
    try:
        llm = ChatOpenAI(
            api_key=api_token,
            base_url="https://router.huggingface.co/v1",
            model="Qwen/Qwen2.5-7B-Instruct",
            temperature=0.3,
            max_tokens=512,
        )
        print("✓ LLM 初始化成功")
        return llm
    except Exception as e:
        print(f"❌ LLM 初始化失败: {e}")
        return None
