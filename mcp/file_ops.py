from langchain_core.tools import tool
import os
from config import TW_BOT_PATH

def _get_safe_path(filename: str) -> str:
    """
    解析路徑並實作安全邊界檢查 (Boundary Check)。
    1. 容許大模型誤加 core/ 前綴。
    2. 防止大模型利用 ../ 進行路徑穿越攻擊 (Path Traversal)。
    """
    if filename.startswith("core/") or filename.startswith("core\\"):
        filename = filename[5:]
        
    # 取得絕對路徑
    safe_base = os.path.abspath(TW_BOT_PATH)
    target_path = os.path.abspath(os.path.join(safe_base, filename))
    
    # 檢查目標路徑是否依然在基準目錄之下
    if not target_path.startswith(safe_base):
        raise ValueError(f"Permission Denied: 檔案路徑 '{filename}' 超出了允許的沙盒範圍。")
        
    return target_path

@tool
def read_cpp_code(filename: str) -> str:
    """Reads the content of a C++ file.
       You can provide either 'sandbox/tactics.cpp' or 'core/sandbox/tactics.cpp'.
    """
    try:
        file_path = _get_safe_path(filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filename}: {e}"

@tool
def write_cpp_code(filename: str, content: str) -> str:
    """Overwrites a C++ file inside the core directory with the provided content.
       WARNING: This will replace the ENTIRE file. Only use for small config files.
    """
    try:
        file_path = _get_safe_path(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully updated {filename}."
    except Exception as e:
        return f"Error writing file {filename}: {e}"

@tool
def edit_code_segment(filename: str, target_content: str, replacement_content: str) -> str:
    """Finds a specific segment of code in a file and replaces it with new content.
       You can provide either 'sandbox/tactics.cpp' or 'core/sandbox/tactics.cpp'.
       The 'target_content' MUST match a unique part of the file exactly.
    """
    try:
        file_path = _get_safe_path(filename)
        with open(file_path, "r", encoding="utf-8") as f:
            full_content = f.read()
        
        # 檢查是否存在且唯一
        count = full_content.count(target_content)
        if count == 0:
            return f"ERROR: Could not find the target_content in {filename}. Please check your spelling and spacing."
        if count > 1:
            return f"ERROR: Found {count} occurrences of target_content. Please provide a more unique segment to replace."
        
        new_content = full_content.replace(target_content, replacement_content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Successfully updated a segment in {filename}."
    except Exception as e:
        return f"Error editing file {filename}: {e}"
