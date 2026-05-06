import os
from dotenv import load_dotenv

# 執行前確保入載 .env 內的所有變數
load_dotenv()

# --- 目錄配置 (Directory Configuration) ---
# 後續若專案更迭，只需在這裡修改路徑即可
AKAGI_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TW_BOT_PATH = os.path.join(AKAGI_BASE_PATH, "core")
TW_DATA_PATH = os.path.join(AKAGI_BASE_PATH, "tw_data")

# --- 模型與執行期配置 (Model & Runtime Configuration) ---
LLM_MODEL_NAME_PRO = "gemini-2.5-pro"
LLM_MODEL_NAME_FLASH = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.0

# 迴圈設定防呆機置：避免 LLM 與 Tools 出現死循環
MAX_ITERATIONS = 20
