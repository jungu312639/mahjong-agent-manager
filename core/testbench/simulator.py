import os
import sys
import random
import time
import json

# 確保 Testbench 能夠往上載入 core/ 裡面的 C++ 編譯模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tw_ukeire_cpp as tw_ukeire

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_win(hand_17):
    # 由於 C++ 沒有匯出單純的 calculate_shanten，我可以透過檢測 Analyze 返回的集合中
    # shanten 的狀態來決定。不過更好的作法是直接讓 C++ 暴露 calculate_shanten 給 Python()
    pass

def simulate_games(num_games=100, record_replay=False):
    p0_wins = 0
    total_turns = 0
    start_time = time.time()
    
    # 用來存放待回傳/寫檔的 replay
    match_logs = []
    
    print(f"啟動 Agentic 壓力測試：共 {num_games} 場對局... (錄影模式: {'ON' if record_replay else 'OFF'})")

    for game_idx in range(num_games):
        wall = [i // 4 for i in range(136)] 
        random.shuffle(wall)
        
        hands = {0: [], 1: [], 2: [], 3: []}
        rivers = {0: [], 1: [], 2: [], 3: []}
        
        dealer = 0 
        
        for p in range(4):
            count = 17 if p == dealer else 16
            for _ in range(count):
                hands[p].append(wall.pop())
                
        turn = 1
        current_p = dealer
        game_over = False
        winner = -1
        
        game_log = {"game_idx": game_idx, "winner": -1, "turns": []}

        while len(wall) > 16:  
            if len(hands[current_p]) % 3 == 1:
                hands[current_p].append(wall.pop())
                
            if tw_ukeire.is_winning_hand(hands[current_p]):
                winner = current_p
                game_over = True
                break
            
            visible = []
            for r in rivers.values():
                visible.extend(r)
                
            suggestions = tw_ukeire.analyze(hands[current_p], visible, min(turn, 18), 0)
            
            if not suggestions:
                game_over = True
                break

            if current_p == 0:
                best_suggestion = suggestions[0]  
                
                # --- [REPLAY 錄影核心] ---
                if record_replay and game_idx == 0: # 為了避免檔案過大，我們只錄製第一場的 P0 視角
                    turn_data = {
                        "turn": turn,
                        "player": 0,
                        "hand": sorted(list(hands[0])),
                        "suggestions": [],
                        "decision": best_suggestion.discard_tile
                    }
                    # 擷取前 3 個最佳建議
                    for s_idx, s in enumerate(suggestions[:3]):
                        dp_prob = s.dp_result.final_win_prob
                        score = s.deep_result.sum_score
                        count = s.base_ukeire.count 
                        turn_data["suggestions"].append({
                            "rank": s_idx + 1,
                            "discard_tile": s.discard_tile,
                            "shanten": s.shanten,
                            "dp_prob": dp_prob,
                            "score": score,
                            "count": count
                        })
                    game_log["turns"].append(turn_data)
            else:
                best_suggestion = min(suggestions, key=lambda s: (s.shanten, -s.base_ukeire.count))
                
            discard_tile = best_suggestion.discard_tile
            
            hands[current_p].remove(discard_tile)
            rivers[current_p].append(discard_tile)
            
            someone_ron = False
            for p in range(4):
                if p == current_p: continue
                if tw_ukeire.is_winning_hand(hands[p] + [discard_tile]):
                    winner = p
                    someone_ron = True
                    break
            
            if someone_ron:
                game_over = True
                break
            
            current_p = (current_p + 1) % 4
            if current_p == dealer:
                turn += 1
                
        game_log["winner"] = winner
        if record_replay and game_idx == 0:
            match_logs.append(game_log)
                
        if game_over and winner == 0:
            p0_wins += 1
        total_turns += turn
            
    end_time = time.time()
    
    if record_replay and match_logs:
        log_path = os.path.join(os.path.dirname(__file__), "game_replay.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(match_logs[0], f, indent=4, ensure_ascii=False)
        print(f"✅ 對局錄影已存檔至: {log_path}")
            
    end_time = time.time()
    
    result = {
        "games_played": num_games,
        "p0_wins": p0_wins,
        "win_rate_percentage": (p0_wins / num_games) * 100 if num_games else 0,
        "avg_turns_to_win": (total_turns / num_games) if num_games else 0,
        "time_elapsed_seconds": round(end_time - start_time, 2),
        "ms_per_game": round(((end_time - start_time) / num_games) * 1000, 2) if num_games else 0
    }
    
    print("\n--- 測試報告 ---")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    games = 100
    record = False
    if len(sys.argv) > 1:
        games = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "--record":
        record = True
    simulate_games(games, record_replay=record)
