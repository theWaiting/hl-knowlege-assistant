import os
from typing import List
import docx2txt
from pypdf import PdfReader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # 兼容较老的 LangChain 版本
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            length_function=len,
        )
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """加载目录下的所有文档"""
        all_documents = []
        
        if not os.path.exists(directory_path):
            print(f"⚠️ 目录不存在: {directory_path}")
            return all_documents
        
        files = [f for f in os.listdir(directory_path) 
                if f.endswith(('.pdf', '.txt', '.docx'))]
        
        if not files:
            print(f"⚠️ 目录中没有文档: {directory_path}")
            return all_documents
        
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            
            try:
                if filename.endswith('.pdf'):
                    documents = self._load_pdf(file_path, filename)
                elif filename.endswith('.txt'):
                    documents = self._load_txt(file_path, filename)
                elif filename.endswith('.docx'):
                    documents = self._load_docx(file_path, filename)
                else:
                    continue

                all_documents.extend(documents)
                print(f"✓ 已加载: {filename}")
                
            except Exception as e:
                print(f"✗ 加载失败 {filename}: {str(e)}")
        
        return all_documents

    def _load_pdf(self, file_path: str, filename: str) -> List[Document]:
        reader = PdfReader(file_path)
        documents = []
        for idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": filename, "page": idx + 1},
                )
            )
        return documents

    def _load_txt(self, file_path: str, filename: str) -> List[Document]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().strip()
        if not text:
            return []
        return [Document(page_content=text, metadata={"source": filename})]

    def _load_docx(self, file_path: str, filename: str) -> List[Document]:
        text = (docx2txt.process(file_path) or "").strip()
        if not text:
            return []
        return [Document(page_content=text, metadata={"source": filename})]
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """切分文档为小块"""
        if not documents:
            return []
        return self.text_splitter.split_documents(documents)
