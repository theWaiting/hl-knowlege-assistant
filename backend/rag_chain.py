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
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
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
        self.documents =  None
        
    def create_vectorstore(self, documents):
        self.documents = documents
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "l2"}  # 使用 L2 距离，适合已归一化的向量;cosine 距离等价于 L2 距离,且更快,适合大规模数据;IP 点积距离不适合已归一化的向量,且在某些实现中可能更慢,不推荐使用
        )
        return self.vectorstore
    
    def load_vectorstore(self):
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
        collection = getattr(self.vectorstore, "_collection", None)
        if collection is None:
            client = getattr(self.vectorstore, "client", None)
            collection_name = getattr(self.vectorstore, "collection_name", None)
            if client is not None and collection_name is not None:
                collection = client.get_collection(collection_name)
    
        if collection is None:
            print("⚠️ 无法访问 Chroma collection")
            return False
    
        try:
            data = collection.get(include=["documents", "metadatas"])
            self.documents = []
            raw_docs = data.get("documents", [])
            raw_metas = data.get("metadatas", [])
            for doc, meta in zip(raw_docs, raw_metas):
                self.documents.append(Document(page_content=str(doc), metadata=meta or {}))
        except Exception as e:
            print(f"⚠️ 恢复文档失败: {e}")
            self.documents = []
            return False
    
        return len(self.documents) > 0
    def get_retriever(self):
        # 配置你的向量检索器（语义相似度）
        similarity_retriever = self.vectorstore.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
      )
        # 配置你的 MMR 检索器
        mmr_retriever = self.vectorstore.as_retriever(
        search_type="mmr", 
        search_kwargs={
                    "k": 4,  # 返回的文档数量，MMR 搜索通常需要返回更多文档以实现多样性
                    "fetch_k": 20, # 从向量数据库中检索的候选文档数量，MMR 搜索需要更多候选文档来选择最相关且多样化的结果
                    "lambda_mult": 0.5 # 平衡相关性和多样性的参数，值越大越注重相关性，值越小越注重多样性;需要根据实际情况调整以获得最佳效果
                }
      )
        if not self.documents:
         raise ValueError("获取检索器失败: 没有可用的文档，请先创建或加载向量数据库")
        # 配置 BM25 检索器，适合处理大规模文本数据，能够根据词频和逆文档频率进行检索;需要安装额外的依
        bm25_retriever = BM25Retriever.from_documents(self.documents)
        bm25_retriever.k = 4
        # 将它们组合成集成检索器，并设置权重
        ensemble_retriever = EnsembleRetriever(
        retrievers=[similarity_retriever, mmr_retriever, bm25_retriever],
        weights=[0.4, 0.3, 0.3]  # 根据你的实际效果调整权重
     )
        return ensemble_retriever
    

    def get_chain(self):
        if not self.vectorstore:
          raise ValueError("请先创建或加载向量数据库")
        retriever = self.get_retriever()
        PROMPT = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
        )
    
        self.chain = RetrievalQA.from_chain_type(
          llm=self.llm,
          chain_type="stuff",
          retriever=retriever,
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