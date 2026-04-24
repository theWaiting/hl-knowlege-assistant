
import os
import time
import requests
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from langchain_openai import ChatOpenAI

class HuggingFaceLLM:
    def __init__(self, api_token: str, repo_id: str = "Qwen/Qwen2.5-7B-Instruct"):
        self.api_token = api_token
        self.repo_id = repo_id
        # 使用已验证可用的 Router OpenAI 兼容接口
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        print(f"   API 端点: {self.api_url}")
    
    def invoke(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.repo_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.3),
        }
        
        try:
            print("   🤖 调用 Hugging Face API...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                choices = result.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    text = message.get("content", "")
                    if text:
                        return text.strip()
            elif response.status_code == 503:
                print("   ⚠️ 模型加载中，请稍后重试")
                return "【提示】模型正在加载中，请稍后重试（首次使用需要 2-3 分钟）"
            else:
                print(f"   ❌ API 错误: {response.status_code}")
                return f"【错误】API 返回 {response.status_code}"
                
        except Exception as e:
            print(f"   ❌ 调用失败: {str(e)[:100]}")
            return "【错误】API 调用失败"
        
        return "【错误】无法获取回答"

class MockLLM:
    def invoke(self, prompt: str, **kwargs) -> str:
        return "【模拟回答】知识库已加载。要获取真实回答，请配置 HUGGINGFACE_API_TOKEN"

def get_llm():

    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    
    if not api_token:
        print("⚠️ 未设置 HUGGINGFACE_API_TOKEN，使用模拟模式")
        print("提示: export HUGGINGFACE_API_TOKEN='hf_your_token'")
        return MockLLM()
    
    print("✓ 使用 Hugging Face Inference API")
    
    # 验证 token
    if not api_token.startswith("hf_"):
        print("⚠️ Token 格式错误，应以 hf_ 开头")
        return MockLLM()
    
    # 使用可配置模型，默认采用已验证可用的 7B 模型
    repo_id = os.getenv("HUGGINGFACE_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    print(f"   模型: {repo_id}")
    
    return HuggingFaceLLM(api_token=api_token, repo_id=repo_id)

