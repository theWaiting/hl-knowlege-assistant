import streamlit as st
import requests
import os

# 页面配置
st.set_page_config(
    page_title="个人知识库问答助手",
    page_icon="📚",
    layout="wide"
)

# API配置
API_URL = "http://localhost:8002"

st.title("📚 个人知识库问答助手")

# 侧边栏 - 文档管理
with st.sidebar:
    st.header("📁 知识库管理")
    
    # 上传文件
    uploaded_files = st.file_uploader(
        "上传文档 (PDF/TXT/DOCX)",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("处理文档"):
        with st.spinner("正在处理文档..."):
            files = [("files", file) for file in uploaded_files]
            response = requests.post(f"{API_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error("处理失败")
    
    st.divider()
    
    # 系统状态
    st.subheader("📊 系统状态")
    try:
        status = requests.get(f"{API_URL}/status").json()
        if status["vectorstore_loaded"]:
            st.success("✅ 知识库已加载")
        else:
            st.warning("⚠️ 知识库为空")
    except:
        st.error("❌ 无法连接到后端服务")
    
    # 清空对话
    if st.button("🗑️ 清空对话历史"):
        requests.post(f"{API_URL}/clear")
        st.success("已清空")
        st.rerun()

# 主界面 - 对话区域
st.header("💬 智能问答")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📖 参考来源"):
                for source in message["sources"]:
                    st.caption(f"📄 {source['file']}")
                    st.text(source['preview'][:200] + "...")

# 输入框
if prompt := st.chat_input("请输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 调用API
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": prompt}
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📖 参考来源"):
                            for source in sources:
                                st.caption(f"📄 {source['file']}")
                                st.text(source['preview'][:200] + "...")
                    
                    # 保存消息
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error("抱歉，处理出错了，请稍后重试")
            except Exception as e:
                st.error(f"连接失败: {str(e)}")