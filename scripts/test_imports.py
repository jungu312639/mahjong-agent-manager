import sys
import os

print("--- Testing Imports ---")
try:
    import mcp
    print("mcp imported")
    from brain import agent_nodes
    print("agent_nodes imported")
    import langchain_mcp_adapters
    print("langchain_mcp_adapters imported")
except Exception as e:
    print(f"Import Error: {e}")

print("--- Testing Path ---")
print(f"CWD: {os.getcwd()}")
print(f"Python path: {sys.path}")

print("Done")
