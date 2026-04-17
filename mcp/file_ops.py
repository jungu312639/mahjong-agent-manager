from langchain_core.tools import tool
import os
from config import TW_BOT_PATH

@tool
def read_cpp_code(filename: str) -> str:
    """Reads the content of a C++ file inside Akagi/tw_bot directory.
       Provide the filename, e.g. 'tw_ukeire.cpp'.
    """
    file_path = os.path.join(TW_BOT_PATH, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filename}: {e}"

@tool
def write_cpp_code(filename: str, content: str) -> str:
    """Overwrites a C++ file inside the core directory with the provided content.
       WARNING: This will replace the ENTIRE file. Only use for small config files.
    """
    file_path = os.path.join(TW_BOT_PATH, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully updated {filename}."
    except Exception as e:
        return f"Error writing file {filename}: {e}"

@tool
def edit_code_segment(filename: str, target_content: str, replacement_content: str) -> str:
    """Finds a specific segment of code in a file and replaces it with new content.
       Use this for large logic files to avoid full-file overwrites.
       The 'target_content' MUST match a unique part of the file exactly.
    """
    file_path = os.path.join(TW_BOT_PATH, filename)
    try:
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
