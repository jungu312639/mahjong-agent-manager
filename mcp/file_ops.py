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
    """Overwrites a C++ file inside Akagi/tw_bot with the provided content.
       Use this to update the algorithm.
    """
    file_path = os.path.join(TW_BOT_PATH, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully updated {filename}."
    except Exception as e:
        return f"Error writing file {filename}: {e}"
