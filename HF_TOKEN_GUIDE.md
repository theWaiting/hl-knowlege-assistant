# HuggingFace Token 401 错误解决指南

## 问题现象
```
❌ Token 验证失败，状态码: 401
```

这表示您的 Token 无效或已过期。

---

## 🔧 解决步骤

### 第1步：检查并生成新的 Token

1. 访问 **[HuggingFace Settings → Tokens](https://huggingface.co/settings/tokens)**

2. 查看现有的 Token：
   - 检查是否有已过期的 Token
   - 如果有旧的 Token，删除或禁用它们

3. **创建新的 API Token**：
   - 点击 "New token"
   - **Token 名称**：可以取为 `hl-knowledge-assistant`
   - **Token 类型**：选择 `Fine-grained` 或 `Read`
   - **权限**：勾选 "Make calls to the Inference API"
   - 点击 "Generate token"

4. **复制完整的 Token**：
   ```
   hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   确保：
   - ✓ 完整复制整个 Token（包括 `hf_` 前缀）
   - ✓ 没有多余的空格或换行符

### 第2步：正确设置环境变量

```bash
# 方法1：临时设置（仅当前终端有效）
export HUGGINGFACE_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 方法2：永久设置（添加到 ~/.zshrc 或 ~/.bashrc）
echo 'export HUGGINGFACE_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
source ~/.zshrc

# 验证设置
echo $HUGGINGFACE_API_TOKEN
```

### 第3步：验证模型权限

部分模型需要在 HuggingFace 上先接受 License 协议：

1. 访问 [Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
2. 检查是否需要接受 License（通常会有蓝色的"接受"按钮）
3. 如果有，点击接受

### 第4步：重新诊断

```bash
cd /Users/huanglu/projects/hl-knowlege-assistant/backend
python test_hf_inference.py
```

---

## 如果仍然失败

### 情况1：404 错误（模型不存在）

这表示您的账户可能对该模型无权限。

**解决方案**：
- 确保已接受模型的 License 协议
- 尝试其他开源模型（不需要特殊权限的）

### 情况2：503 错误（模型正在加载）

这是正常的。HuggingFace 首次使用模型时需要加载（5-10 分钟）。

**解决方案**：
- 等待 5-10 分钟
- 重新运行诊断脚本

### 情况3：其他错误

运行诊断脚本时会显示具体的错误代码和建议。

---

## 🎯 快速验证方案

如果想快速验证您的 Token 是否有效，可以运行这个简单的 Python 脚本：

```python
import requests
import os

api_token = os.getenv("HUGGINGFACE_API_TOKEN")
headers = {"Authorization": f"Bearer {api_token}"}

# 验证用户信息
response = requests.get("https://huggingface.co/api/user", headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

if response.status_code == 200:
    print("\n✓ Token 有效！")
else:
    print("\n❌ Token 无效或已过期")
```

---

## 📝 常见问题

**Q: 我能在网页上看到 Token，但诊断工具说 401 是什么意思？**

A: Token 在网页上显示并不代表它是有效的。它可能：
- 已过期（通常默认 30 天或更短）
- 权限不足（没有 Inference API 访问权限）
- 格式不正确（复制时丢失了字符）

**Q: 生成了新 Token 后需要做什么？**

A: 
1. 完整复制新 Token
2. 更新环境变量：`export HUGGINGFACE_API_TOKEN="新token"`
3. 如果是永久设置，需要重启终端或运行 `source ~/.zshrc`
4. 重新运行诊断

**Q: 为什么替代模型也返回 404？**

A: 可能是：
- 这些模型需要特殊权限（需要先在网页上接受 License）
- 您的账户权限不足
- 模型名称不正确

---

## 🆘 如果仍需帮助

请提供以下信息：
1. 诊断脚本的完整输出
2. Token 是否刚创建还是旧的
3. 是否在网页上接受了模型的 License 协议
4. 运行诊断脚本时是否在同一个终端会话中设置了环境变量
