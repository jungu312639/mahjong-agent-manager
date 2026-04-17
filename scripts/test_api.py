import requests
import json
import io
import sys

# 強制 Windows 終端機使用 UTF-8 編碼輸出，避免 Emoji 導致報測
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "http://localhost:8000/api/run"
# 優先讀取命令列參數，否則使用預設訊息
test_message = sys.argv[1] if len(sys.argv) > 1 else "請根據壁理論優化防守"
params = {"message": test_message}

print(f"[*] 正在連線至 API: {url} ...")

try:
    # 使用 stream=True 以接收 SSE 串流
    with requests.get(url, params=params, stream=True) as response:
        if response.status_code != 200:
            print(f"[FAIL] HTTP 錯誤: {response.status_code}")
            exit()
            
        print("[+] 連線成功，等待串流回應...\n")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    content = decoded_line[6:]
                    try:
                        data = json.loads(content)
                        if data.get("type") == "message":
                            print(f"[Agent]: {data.get('content')}")
                        elif data.get("type") == "error":
                            print(f"[ERROR]: {data.get('content')}")
                        else:
                            # 可能是其他類型的訊息 (例如步驟更新)
                            print(f"[Update]: {data}")
                    except:
                        print(f"[Raw Data]: {content}")
                        
except Exception as e:
    print(f"[FAIL] 執行過程發生異常: {str(e)}")

print("\n=== 測試結束 ===")
