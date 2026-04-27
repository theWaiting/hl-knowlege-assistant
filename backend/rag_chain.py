import os
import warnings
import numpy as np
from typing import List

# 导入 langchain 组件
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from prompts import RAG_PROMPT_TEMPLATE
warnings.filterwarnings("ignore")

# 环境变量已在 app.py 中提前设置，这里只作为备份
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", "false")
os.environ.setdefault("CHROMA_DISABLE_TELEMETRY", "true")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

class RAGChain:
    def __init__(self, llm, persist_directory="./chroma_db"):
        self.llm = llm
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
        self.chain = None
    
    def create_vectorstore(self, documents):
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return self.vectorstore
    
    def load_vectorstore(self):
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        return True
    
    

    def get_chain(self):
        if not self.vectorstore:
          raise ValueError("请先创建或加载向量数据库")
    
        PROMPT = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
        self.chain = RetrievalQA.from_chain_type(
          llm=self.llm,
          chain_type="stuff",
          retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
          return_source_documents=True,
          verbose=True,
          chain_type_kwargs={"prompt": PROMPT}
    )
        return self.chain
    
    def ask(self, question: str):
        if not self.chain:
            self.get_chain()
        
        result = self.chain.invoke({"query": question})
        
        # 格式化输出以保持兼容性
        sources = []
        for doc in result.get("source_documents", []):
            sources.append({
                "file": doc.metadata.get('source', '未知'),
                "preview": doc.page_content[:150]
            })
        
        return {
            "answer": result.get("result", ""),
            "sources": sources
        }