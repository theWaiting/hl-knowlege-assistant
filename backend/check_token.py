import os
from huggingface_hub import HfApi

# 从环境变量获取 Token
token = os.getenv("HUGGINGFACE_API_TOKEN")

if not token:
    print("❌ 环境变量 HUGGINGFACE_API_TOKEN 未设置")
    exit(1)

api = HfApi()

try:
    # 尝试调用 whoami API 来验证用户身份
    user = api.whoami(token=token)
    print(f"✅ 认证成功！当前登录用户: {user['name']}")

    # 额外测试：尝试获取一个公开模型的信息
    repo_id = "Qwen/Qwen2.5-7B-Instruct"
    info = api.model_info(repo_id, token=token)
    print(f"✅ 成功访问模型 '{repo_id}'")
    
    # 检查模型是否需要额外授权
    if hasattr(info, 'gated') and info.gated:
        print(f"   (注意：'Qwen/Qwen2.5-7B-Instruct' 是需要单独授权的门控模型，你还需要访问它的页面点击同意协议)")
        
except Exception as e:
    print(f"❌ 认证或请求失败: {e}")
    # 根据错误代码给出提示
    if "401" in str(e):
        print("   这表示你提供的 Token 无效或已过期，请检查是否完整复制了新生成的 Token。")
    elif "403" in str(e):
        print("   这表示你的 Token 权限不足。可能的原因：")
        print("   1. Token 是 'Read' 类型，但你尝试了需要 'Write' 权限的操作。")
        print("   2. 你试图访问的模型要求你先在网页上点击'同意'接受其协议。")
        print("   3. 你使用的是细粒度权限 Token，但其针对该仓库的权限未打开。")