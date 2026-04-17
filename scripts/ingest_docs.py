import os
import sys
import io

# 強制 Windows 終端機使用 UTF-8 編碼輸出，避免 Emoji 導致報測
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 確保可以 import 專案模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from mcp.tools_memory import collection_theory
import uuid

# ==============================================================
# RAG 知識庫灌注引擎 (Document Ingestion Engine)
# 解析 docs/mahjong_theory/ 的 txt/md，切塊並壓入 ChromaDB
# ==============================================================

def ingest_all_docs():
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "mahjong_theory")
    
    # JD 要求： Chunk 500, Overlap 10% (50)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n- ", "\n", " ", ""]
    )
    
    print(f"掃描知識庫目錄: {docs_path}")
    count = 0
    
    for filename in os.listdir(docs_path):
        if filename.endswith(".md") or filename.endswith(".txt"):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 切塊
            chunks = text_splitter.split_text(content)
            
            # 將每一個塊寫入 ChromaDB
            docs = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_chunk_{i}"
                docs.append(chunk)
                metadatas.append({"source": filename, "chunk": i})
                ids.append(chunk_id)
                count += 1
                
            collection_theory.add(documents=docs, metadatas=metadatas, ids=ids)
            print(f"✅ 文件 {filename} 處理完畢，產生了 {len(chunks)} 個向量塊。")

    print(f"\n知識庫灌注完成！共寫入 {count} 條理論記錄至 ChromaDB_mahjong_knowledge。")

if __name__ == "__main__":
    ingest_all_docs()
