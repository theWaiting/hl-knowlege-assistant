
# hl-knowlege-assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0-1C3C3C?logo=langchain)](https://www.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B?logo=streamlit)](https://streamlit.io/)


**项目详细介绍 (可选)**:本项目指在提供基于RAG技术依赖于huggingface 模型的全免费的本地知识库，支持多种文件格式，让你能够快速精准的从自己的文档中检索信息，获得精准可靠的答案。

## ✨ 特性

- **零成本私有知识库**：支持 PDF、DOCX、TXT 等多种格式文档上传，基于 Hugging Face 开源模型（embedding + chat），全程无付费 API 依赖，一次下载永久使用。

- **即开即用，状态持久化**：文档向量数据自动持久化到本地 Chroma 数据库，服务重启后毫秒级恢复，无需重复处理。内置 Streamlit 前端界面，无需额外配置，一条命令启动完整交互体验。

- **严格 RAG 架构，回答可溯源**：检索增强生成，回答严格基于您上传的文档内容，并提供引用来源，避免大模型幻觉，适合企业知识库、个人笔记问答等严肃场景。

- **灵活的大模型适配**：已封装 HuggingFace Inference API 与 DeepSeek API，可轻松切换至其他 OpenAI 兼容模型，满足不同网络环境与预算需求。


## 🛠️ 技术栈

- **大语言模型 (LLM)**: `HuggingFace` 或其他模型提供商
- **框架**: `FastAPI` (后端API), `LangChain` (RAG流程编排)
- **前端**: `Streamlit` (演示UI)
- **向量数据库**: `Chroma` (本地向量存储)
- **Embedding模型**: `BAAI/bge-small-zh-v1.5` (中文嵌入模型)
- **部署**: `Docker` (推荐, 可选)

## 🚀 快速开始

### 环境要求

- Python 3.11+
- pip

### 安装

1. 克隆项目
   ```bash
   git clone https://github.com/your_username/project-name.git
   cd project-name
2. 创建并激活虚拟环境
   pyton -m venv venv
   source venv/bin/active # Linux/macos
   venv\Scripts\active # Windows
3. 安装依赖
   cd backend
   pip install -r requirement
4. 配置huggingface token 
   export HUGGINGFACE_API_TOKEN="hf_XXXXXXXX" # Linux/macos
### 运行
1. 启动后端服务
   cd backend
   python app.py
2. 启动前端界面（Streamlit）
   cd frontend
   streamlit run streamlit_app.py
   浏览器会自动打开http://localhost:8501 
### 使用指南
1. 上传文档
   点击侧边栏的“上传文档”按钮，选择你需要查询的 PDF、TXT 或 Word 文件。
2. 处理文档
   文档上传后，系统会自动将其分块、生成向量并存入本地数据库。
3. 提问与问答
   在聊天界面输入你的问题，系统将从向量库中检索相关内容，并由大语言模型生成答案。
   💡 设计原则: 本项目默认严格遵循“检索增强”原则，回答仅基于你上传的文档。如果信息不足，会明确告知，避免模型产生幻觉。
### 路线图
1. 支持更多文档格式 (如 Markdown, HTML)
2. 引入对话记忆机制，支持多轮对话
3. 添加更多的 RAG 优化策略 (如混合搜索、重排序)
4. 提供 Docker 一键部署方案
5. (可选)集成在线搜索工具，当知识库无法回答时进行补充
### 🤝 如何贡献
我们欢迎所有形式的贡献！如果你有好的想法或发现了问题，请参考以下步骤：
1. Fork 本仓库
2. 创建你的特性分支 (git checkout -b feature/amazing-feature)
3. 提交你的更改 (git commit -m 'Add some amazing feature')
4. 推送到分支 (git push origin feature/amazing-feature)
5. 打开一个 Pull Request
在提交前，请确保你的代码符合项目的编码规范。
### 📜 许可证
该项目基于 AGPL-3.0 许可证进行发布——详情请查阅 LICENSE 文件。
### 💐 致谢
~感谢 LangChain 提供了强大的 RAG 开发框架。
~感谢所有为本项目做出贡献的开发者们。