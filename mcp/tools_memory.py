import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_core.tools import tool

# ==============================================================
# 建立持久化向量資料庫 Client (這會在你專案層開一個 data 資料夾)
# ==============================================================
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vector_db")
client = chromadb.PersistentClient(path=DB_PATH)

# 延遲加載 (Lazy Loading) 機制，避免 import 時就卡住
_theory_coll = None
_history_coll = None

def get_collections():
    global _theory_coll, _history_coll
    if _theory_coll is None or _history_coll is None:
        print("[*] 正在初始化向量資料庫與 Embedding 模型...")
        # 使用完全本機端不依懶網路的 Sentence-Transformer 模型
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _theory_coll = client.get_or_create_collection(name="mahjong_knowledge", embedding_function=emb_fn)
        _history_coll = client.get_or_create_collection(name="evolution_history", embedding_function=emb_fn)
    return _theory_coll, _history_coll

# ==============================================================
# 給 Agent 使用的工具：提取知識 (Retrieval)
# ==============================================================
@tool
def tool_retrieve_context(query_text: str) -> str:
    """
    Search both the Mahjong Theory database and the AI Evolution History database 
    using Semantic Vector Search. Use this tool BEFORE making any algorithmic decisions.
    """
    result_str = f"=== Vector Search Results for '{query_text}' ===\n\n"
    coll_theory, coll_history = get_collections()
    
    # 搜尋 1: 靜態理論
    theory_res = coll_theory.query(query_texts=[query_text], n_results=2)
    result_str += "[Mahjong Cognitive Theory]:\n"
    if theory_res and theory_res['documents'] and theory_res['documents'][0]:
        for doc, meta in zip(theory_res['documents'][0], theory_res['metadatas'][0]):
            result_str += f"- [{meta.get('source', 'Unknown')}] {doc}\n"
    else:
        result_str += "- No theory found.\n"
        
    result_str += "\n[AI Evolution & Failure History]:\n"
    # 搜尋 2: 演化歷史
    hist_res = coll_history.query(query_texts=[query_text], n_results=3)
    if hist_res and hist_res['documents'] and hist_res['documents'][0]:
        for doc, meta in zip(hist_res['documents'][0], hist_res['metadatas'][0]):
            win_rate = meta.get('win_rate', 'N/A')
            status = meta.get('status', 'Unknown')
            result_str += f"- (Status: {status}, WinRate: {win_rate}%) {doc}\n"
    else:
        result_str += "- No historical experiments found.\n"
        
    return result_str

# ==============================================================
# 給 Agent 使用的工具：歷史覆寫 (Commit Experience)
# ==============================================================
@tool
def tool_commit_experience(summary: str, win_rate: float, compiler_status: str) -> str:
    """
    Commit an experiment result to the Evolution History Vector Database.
    Call this tool whenever you receive a report from the QA Agent.
    Args:
        summary: The detailed breakdown of why the modification failed or succeeded.
        win_rate: The tested win rate percentage. Output 0 if compilation failed.
        compiler_status: 'success' or 'failed'.
    """
    import uuid
    doc_id = f"exp_{uuid.uuid4().hex[:8]}"
    
    metadata = {
        "win_rate": win_rate,
        "status": compiler_status,
        "type": "post_mortem"
    }
    
    _, coll_history = get_collections()
    coll_history.add(
        documents=[summary],
        metadatas=[metadata],
        ids=[doc_id]
    )
    
    return f"Successfully embedded and saved experiment {doc_id} to ChromaDB."
