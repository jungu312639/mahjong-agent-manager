import os
import sys
import json

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TILES_34 = [
    '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
    '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
    '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
    '1z', '2z', '3z', '4z', '5z', '6z', '7z'
]

def print_board(turn_data):
    os.system('cls' if os.name == 'nt' else 'clear')
    turn = turn_data["turn"]
    player = turn_data["player"]
    hand_str = " ".join([TILES_34[t] for t in turn_data["hand"]])
    decision_str = TILES_34[turn_data['decision']]
    
    print("=" * 50)
    print(f" 🎬 第 {turn} 巡 | 玩家 {player} (AI 主視角)")
    print("=" * 50)
    print(f"[手牌] 🀄: {hand_str} ({len(turn_data['hand'])}張)")
    print("\n[AI 腦內演算報告]")
    
    for sug in turn_data["suggestions"]:
        rank = sug["rank"]
        tile = TILES_34[sug["discard_tile"]]
        shanten = sug["shanten"]
        dp_prob = sug["dp_prob"]
        score = sug["score"]
        count = sug["count"]
        
        if shanten >= 2:
            print(f"  {rank}. 切 [{tile}] | 向聽: {shanten} | 大局演算: 進張廣度 {score:.2f}")
        else:
            print(f"  {rank}. 切 [{tile}] | 向聽: {shanten} | 勝率: {dp_prob*100:.2f}% (期望廣度: {score:.2f})")
            
    print(f"\n[決定] AI 選擇打出 👉 [{decision_str}]")
    print("=" * 50)

def replay():
    log_path = os.path.join(os.path.dirname(__file__), "game_replay.json")
    if not os.path.exists(log_path):
        print(f"找不到錄影檔：{log_path}")
        return
        
    with open(log_path, "r", encoding="utf-8") as f:
        log_data = json.load(f)
        
    print(f"▶️ 載入對局 #{log_data.get('game_idx', 0)}，勝者是玩家 {log_data.get('winner', 'None')}")
    print(f"準備開始播放... (按 Enter 進入下一巡，輸入 'q' 離開)")
    input()
    
    for turn_data in log_data["turns"]:
        print_board(turn_data)
        cmd = input("\n[Enter]下一巡 | [q]退出: ")
        if cmd.strip().lower() == 'q':
            break
            
    print("🎬 播放結束。")

if __name__ == "__main__":
    replay()
