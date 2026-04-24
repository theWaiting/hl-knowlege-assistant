# 问答系统错误诊断报告

## 错误总结

启动后调用 `/ask` 接口返回 500 错误，堆栈跟踪显示：
```
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## 根本原因

### 1️⃣ **主要错误：HuggingFace API 响应无效**

**错误位置**：
- `backend/rag_chain.py` 第 112 行
- `langchain_community/llms/huggingface_endpoint.py` 第 133 行

**问题**：HuggingFace API 返回了空的或格式不正确的响应，导致 JSON 解析失败。

**可能的原因**：
- ❌ `HUGGINGFACE_API_TOKEN` 未设置或无效
- ❌ API Token 过期或无访问权限
- ❌ 模型 `Qwen/Qwen2.5-7B-Instruct` 暂不可用或正在加载
- ❌ 网络连接问题
- ❌ HuggingFace API 服务故障

### 2️⃣ **次要错误：Chroma Telemetry 兼容性问题**

**错误信息**：
```
Failed to send telemetry event CollectionQueryEvent: capture() takes 1 positional argument but 3 were given
```

**原因**：Chroma DB 的 telemetry 模块与当前版本不兼容

---

## 已应用的修复

### ✅ 修复 1：增强 LLM 配置诊断（`backend/llm_config_a.py`）

添加了 API Token 验证功能，在启动时检查 Token 是否有效：

```python
# 验证 API Token 是否有效
try:
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=5)
    if response.status_code != 200:
        print(f"⚠️ HuggingFace API Token 验证失败，状态码: {response.status_code}")
except Exception as e:
    print(f"⚠️ 无法验证 HuggingFace 连接: {e}")
```

### ✅ 修复 2：禁用 Chroma Telemetry（`backend/app.py`）

添加环境变量禁用 Chroma 的 telemetry：

```python
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
```

### ✅ 修复 3：RAG 链错误处理（`backend/rag_chain.py`）

在 `ask()` 方法中添加了完整的异常处理和诊断信息：

```python
try:
    result = self.llm.invoke(prompt_text)
except Exception as llm_error:
    error_msg = str(llm_error)
    print(f"❌ LLM 调用错误: {error_msg}")
    
    if "JSONDecodeError" in str(type(llm_error).__name__):
        print("   错误原因：HuggingFace API 返回了无效的响应")
        print("   可能的解决方案:")
        print("   1. 检查 HUGGINGFACE_API_TOKEN 是否设置正确")
        print("   2. 确保 token 有访问权限")
        print("   3. 检查网络连接")
        print("   4. 模型可能正在加载中，请稍后重试")
    result = f"【系统错误】LLM 服务暂不可用: {error_msg}"
```

---

## 故障排查步骤

### 第一步：检查 API Token

```bash
# 设置 HuggingFace API Token
export HUGGINGFACE_API_TOKEN="hf_your_token_here"

# 验证设置
echo $HUGGINGFACE_API_TOKEN
```

[获取 API Token](https://huggingface.co/settings/tokens)

### 第二步：运行诊断工具

使用新增的诊断脚本检查所有问题：

```bash
cd backend
python diagnose_hf.py
```

此脚本会检查：
1. ✓ 环境变量是否设置
2. ✓ API Token 是否有效
3. ✓ 模型是否可用
4. ✓ API 调用是否成功

### 第三步：验证修复

```bash
# 重启应用
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8002

# 在另一个终端测试
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "你好"}'
```

---

## 模型加载状态检查

如果看到这个警告：
```
⚠️ 模型正在加载中，请稍候（通常需要 5-10 分钟）
```

这是正常的。HuggingFace Inference API 在首次使用模型时会加载它，可能需要等待几分钟。

---

## 常见问题解决

### 问题：Token 无效
**解决**：
1. 访问 https://huggingface.co/settings/tokens
2. 创建新的 API Token（或使用现有的有效 Token）
3. 复制 Token 并重新设置：`export HUGGINGFACE_API_TOKEN='hf_...'`

### 问题：模型不可用
**解决**：
1. 访问 https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
2. 检查模型是否被接受的 License 遮挡
3. 可以尝试替换为其他模型，例如：
   - `meta-llama/Llama-2-7b-chat-hf`
   - `mistralai/Mistral-7B-Instruct-v0.1`

### 问题：网络超时
**解决**：
1. 检查网络连接
2. 尝试使用代理（如需要）
3. 增加超时时间设置

---

## 后续改进建议

1. **使用本地模型**：避免依赖在线 API，考虑用 Ollama 或其他本地 LLM
2. **添加重试机制**：对临时性错误进行自动重试
3. **模型缓存**：缓存模型响应以加快响应速度
4. **错误监控**：集成日志系统以更好地追踪问题

---

## 文件修改记录

| 文件 | 修改内容 |
|------|--------|
| `backend/llm_config_a.py` | 添加 API Token 验证 |
| `backend/app.py` | 禁用 Chroma Telemetry |
| `backend/rag_chain.py` | 添加详细的错误处理和诊断 |
| `backend/diagnose_hf.py` | ✨ 新增诊断工具脚本 |
