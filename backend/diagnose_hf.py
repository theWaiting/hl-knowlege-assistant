#!/usr/bin/env python3
"""
诊断 HuggingFace API 连接问题的脚本
"""
import os
import requests
import sys

def check_env():
    """检查环境变量"""
    print("=" * 60)
    print("1️⃣  检查环境变量")
    print("=" * 60)
    
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_API_TOKEN 未设置")
        print("   请运行: export HUGGINGFACE_API_TOKEN='hf_...'")
        return False
    
    print(f"✓ Token 已设置: {token[:10]}...{token[-10:]}")
    return True

def check_hf_auth(token):
    """验证 HuggingFace Token"""
    print("\n" + "=" * 60)
    print("2️⃣  验证 HuggingFace Token")
    print("=" * 60)
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✓ Token 有效，用户: {user_info.get('name', '未知')}")
            return True
        else:
            print(f"❌ Token 验证失败，状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def check_model_availability(token):
    """检查模型是否可用"""
    print("\n" + "=" * 60)
    print("3️⃣  检查模型可用性")
    print("=" * 60)
    
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # 发送一个简单的请求来检查模型状态
        payload = {"inputs": "test"}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"模型: {model_name}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 模型在线且可用")
            return True
        elif response.status_code == 503:
            print("⚠️  模型正在加载中，请稍候（通常需要 5-10 分钟）")
            return False
        else:
            print(f"❌ 模型不可用")
            print(f"   响应: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_api_call(token):
    """测试完整的 API 调用"""
    print("\n" + "=" * 60)
    print("4️⃣  测试 API 调用")
    print("=" * 60)
    
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": "你好，请自我介绍",
            "parameters": {
                "max_length": 100,
                "temperature": 0.3,
            }
        }
        
        print("发送请求...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ API 调用成功")
            result = response.json()
            print(f"响应: {result}")
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"   响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 调用失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("🔧 HuggingFace API 诊断工具")
    print("=" * 60)
    
    # 检查环境
    if not check_env():
        print("\n❌ 环境配置不完整，请先设置 API Token")
        sys.exit(1)
    
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    
    # 验证 Token
    if not check_hf_auth(token):
        print("\n❌ API Token 无效，请检查 token 是否正确")
        sys.exit(1)
    
    # 检查模型
    model_ok = check_model_availability(token)
    if not model_ok:
        print("\n⚠️  模型暂不可用，请稍候或尝试其他模型")
    
    # 测试调用
    test_api_call(token)
    
    print("\n" + "=" * 60)
    print("✓ 诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
