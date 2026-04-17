import os
from dotenv import load_dotenv

# 執行前確保入載 .env 內的所有變數
load_dotenv()

# --- 目錄配置 (Directory Configuration) ---
# 後續若專案更迭，只需在這裡修改路徑即可
AKAGI_BASE_PATH = r"C:\Users\superidol\Documents\projects\mahjong-agent-manager"
TW_BOT_PATH = os.path.join(AKAGI_BASE_PATH, "core")
TW_DATA_PATH = os.path.join(AKAGI_BASE_PATH, "tw_data")

# --- 模型與執行期配置 (Model & Runtime Configuration) ---
# 如果你想更換模型，例如改成 anthropic 或是較小的 gemini-1.5-flash，統一在此處更改
LLM_MODEL_NAME = "gemini-3.1-flash-lite-preview"
LLM_TEMPERATURE = 0.0

# 迴圈設定防呆機置：避免 LLM 與 Tools 出現死循環
MAX_ITERATIONS = 5 
