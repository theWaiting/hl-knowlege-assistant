# ⚠️ 必须在任何其他导入之前设置环境变量
import os
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
os.environ["CHROMA_DISABLE_TELEMETRY"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
from pathlib import Path

from document_loader import DocumentProcessor
from rag_chain import RAGChain

# 使用方案A
from llm_config_a import get_llm

app = FastAPI(title="个人知识库问答助手")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
rag_chain = None
doc_processor = DocumentProcessor()
DATA_DIR = "./data"
UPLOAD_DIR = "./uploads"

# 创建必要目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    sources: List[dict] = []

@app.on_event("startup")
async def startup_event():
    """启动时加载已有知识库"""
    global rag_chain
    try:
        print("正在初始化 LLM...")
        llm = get_llm()
        
        if llm is None:
            print("❌ 无法初始化 LLM，请设置 API Key 后重启")
            rag_chain = None
            return
        
        print("正在初始化 RAG 链...")
        rag_chain = RAGChain(llm)
        
        if rag_chain.load_vectorstore():
            print("✓ 已加载现有知识库")
        else:
            print("⚠ 未找到知识库，请先上传文档")
            
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        rag_chain = None

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """上传并处理文档"""
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(status_code=500, detail="系统未初始化，请检查 API Key 设置")
    
    # 保存上传的文件
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)
    
    # 处理文档
    all_docs = []
    for file_path in saved_files:
        # 移动到data目录
        dest = os.path.join(DATA_DIR, os.path.basename(file_path))
        shutil.move(file_path, dest)
    
    # 加载所有文档
    all_docs = doc_processor.load_documents(DATA_DIR)
    
    if not all_docs:
        raise HTTPException(status_code=400, detail="没有有效文档")
    
    # 切分并创建向量库
    try:
        chunks = doc_processor.split_documents(all_docs)
        if not chunks:
            raise HTTPException(status_code=400, detail="文档切分后为空")
        
        rag_chain.create_vectorstore(chunks)
        return {"message": f"成功处理 {len(files)} 个文件，生成 {len(chunks)} 个文档块"}
    except Exception as e:
        print(f"创建向量库失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建向量库失败: {str(e)}")

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """提问"""
    if rag_chain is None:
        raise HTTPException(status_code=500, detail="系统未初始化，请检查 API Key 设置")
    
    if not rag_chain.vectorstore:
        raise HTTPException(status_code=400, detail="知识库为空，请先上传文档")
    
    result = rag_chain.ask(question.question)
    return Answer(answer=result["answer"], sources=result["sources"])

@app.post("/clear")
async def clear_memory():
    """清空对话历史"""
    if rag_chain:
        rag_chain.clear_memory()
    return {"message": "对话历史已清空"}

@app.get("/status")
async def get_status():
    """获取系统状态"""
    return {
        "vectorstore_loaded": rag_chain is not None and rag_chain.vectorstore is not None,
        "data_dir": DATA_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
