import os
import warnings
warnings.filterwarnings("ignore")

# 环境变量已在 app.py 中提前设置，这里只作为备份
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", "false")
os.environ.setdefault("CHROMA_DISABLE_TELEMETRY", "true")

# 直接使用 sentence_transformers，绕过 langchain 的封装
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

class DirectEmbeddings:
    """直接使用 sentence_transformers，不依赖 langchain_community.embeddings"""
    def __init__(self):
        self.model = None

    def _ensure_model(self):
        if self.model is None:
            print("正在加载 Embedding 模型...")
            self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5', device='cpu')
            print("✓ Embedding 模型加载成功")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        self._ensure_model()
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        self._ensure_model()
        embedding = self.model.encode([text], normalize_embeddings=True)[0]
        return embedding.tolist()

# 导入 langchain 组件
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class RAGChain:
    def __init__(self, llm, persist_directory="./chroma_db"):
        self.llm = llm
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.retriever = None
        self.prompt = None
        
        # 使用自定义的 embeddings
        self.embeddings = DirectEmbeddings()
    
    def create_vectorstore(self, documents):
        if not documents:
            raise ValueError("没有文档可以处理")
        
        print(f"正在创建向量数据库，处理 {len(documents)} 个文档块...")
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()
        print("✓ 向量数据库创建完成")
        return self.vectorstore
    
    def load_vectorstore(self):
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("✓ 加载已有向量数据库")
            return True
        return False
    
    def get_chain(self, k=4):
        if not self.vectorstore:
            raise ValueError("请先创建或加载向量数据库")
        
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        
        template = """你是一个专业的问答助手。请基于以下上下文内容回答用户的问题。

上下文信息：
{context}

用户问题：{question}

请基于上面的上下文回答问题。如果上下文中没有相关信息，请直接说"根据现有资料无法回答这个问题"。"""

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        return True
    
    def ask(self, question: str):
        if not self.retriever:
            self.get_chain()
        
        try:
            # 获取相关文档
            docs = self.retriever.invoke(question)
            
            # 组合文档内容
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # 格式化提示
            prompt_text = self.prompt.format(context=context, question=question)
            
            # 调用LLM，添加错误处理
            try:
                result = self.llm.invoke(prompt_text)
            except Exception as llm_error:
                error_msg = str(llm_error)
                print(f"❌ LLM 调用错误: {error_msg}")
                
                # 提供诊断信息
                if "JSONDecodeError" in str(type(llm_error).__name__):
                    print("   错误原因：HuggingFace API 返回了无效的响应")
                    print("   可能的解决方案:")
                    print("   1. 检查 HUGGINGFACE_API_TOKEN 是否设置正确")
                    print("   2. 确保 token 有访问权限")
                    print("   3. 检查网络连接")
                    print("   4. 模型可能正在加载中，请稍后重试")
                    result = f"【系统错误】LLM 服务暂不可用: {error_msg}"
                else:
                    result = f"【系统错误】{error_msg}"
            
            sources = []
            for doc in docs:
                source = doc.metadata.get('source', '未知')
                content = doc.page_content[:150]
                sources.append({"file": source, "preview": content})
            
            return {"answer": result, "sources": sources}
            
        except Exception as e:
            print(f"❌ RAG 链错误: {e}")
            return {"answer": f"【系统错误】处理问题时出现错误: {str(e)}", "sources": []}
    
    def clear_memory(self):
        pass
