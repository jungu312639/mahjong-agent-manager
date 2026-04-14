#include "MahjongAI.h"
#include <algorithm>
#include <iostream>
#include <chrono> // 🎯 新增：用來精準計時
#include <vector>
#include <cstdlib>
using namespace std;

// ==========================================
// 1. 結構定義：記錄一個花色的最佳狀態
// ==========================================
// max_t[是否有雀頭 0~1][面子數量 0~5] = 搭子數量
struct SuitResult {
    int8_t max_t[2][6]; 
};

// 建立 195 萬的萬筒條查表，以及 7.8 萬的字牌查表
// 總計約消耗 25 MB 記憶體，非常輕量
SuitResult table_suit[1953125];
SuitResult table_z[78125];

// ==========================================
// 2. 查表生成器：動態規劃 (Dynamic Programming)
// ==========================================
void init_tables() {
    // ---- A. 初始化萬筒條 (包含順子、刻子、搭子) ----
    for(int p=0; p<2; ++p) for(int m=0; m<6; ++m) table_suit[0].max_t[p][m] = -1;
    table_suit[0].max_t[0][0] = 0; // 0張牌的基礎狀態

    int pow5[9];
    pow5[8] = 1;
    for(int i=7; i>=0; --i) pow5[i] = pow5[i+1] * 5;

    // 從 1 張牌慢慢往上推導到 14 張牌 (Topological DP)
    for (int code = 1; code < 1953125; ++code) {
        int counts[9];
        int temp = code;
        for (int i = 8; i >= 0; --i) { counts[i] = temp % 5; temp /= 5; }

        SuitResult res;
        for(int p=0; p<2; ++p) for(int m=0; m<6; ++m) res.max_t[p][m] = -1;

        // 嘗試從這個狀態「抽掉」特定的牌型，看看剩下牌的最佳狀態是什麼
        for (int i = 0; i < 9; ++i) {
            // 情況 1: 當作廢牌丟掉
            if (counts[i] >= 1) { 
                int sub_code = code - pow5[i];
                const SuitResult& sub = table_suit[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<6; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], (int)sub.max_t[p][m]);
            }
            // 情況 2: 抽出一組對子
            if (counts[i] >= 2) { 
                int sub_code = code - 2 * pow5[i];
                const SuitResult& sub = table_suit[sub_code];
                for(int m=0; m<6; ++m) {
                    if(sub.max_t[0][m] != -1) res.max_t[1][m] = max((int)res.max_t[1][m], (int)sub.max_t[0][m]); // 當雀頭
                    for(int p=0; p<2; ++p)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], sub.max_t[p][m] + 1); // 當搭子
                }
            }
            // 情況 3: 抽出一組刻子
            if (counts[i] >= 3) { 
                int sub_code = code - 3 * pow5[i];
                const SuitResult& sub = table_suit[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<5; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m+1] = max((int)res.max_t[p][m+1], (int)sub.max_t[p][m]);
            }
            // 情況 4: 抽出一組順子
            if (i <= 6 && counts[i] >= 1 && counts[i+1] >= 1 && counts[i+2] >= 1) { 
                int sub_code = code - pow5[i] - pow5[i+1] - pow5[i+2];
                const SuitResult& sub = table_suit[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<5; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m+1] = max((int)res.max_t[p][m+1], (int)sub.max_t[p][m]);
            }
            // 情況 5: 抽出兩面/邊張搭子
            if (i <= 7 && counts[i] >= 1 && counts[i+1] >= 1) { 
                int sub_code = code - pow5[i] - pow5[i+1];
                const SuitResult& sub = table_suit[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<6; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], sub.max_t[p][m] + 1);
            }
            // 情況 6: 抽出嵌張搭子
            if (i <= 6 && counts[i] >= 1 && counts[i+2] >= 1) { 
                int sub_code = code - pow5[i] - pow5[i+2];
                const SuitResult& sub = table_suit[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<6; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], sub.max_t[p][m] + 1);
            }
        }
        table_suit[code] = res;
    }

    // ---- B. 初始化字牌 (無順子、搭子) ----
    for(int p=0; p<2; ++p) for(int m=0; m<6; ++m) table_z[0].max_t[p][m] = -1;
    table_z[0].max_t[0][0] = 0;

    int pow5_z[7];
    pow5_z[6] = 1;
    for(int i=5; i>=0; --i) pow5_z[i] = pow5_z[i+1] * 5;

    for (int code = 1; code < 78125; ++code) {
        int counts[7];
        int temp = code;
        for (int i = 6; i >= 0; --i) { counts[i] = temp % 5; temp /= 5; }

        SuitResult res;
        for(int p=0; p<2; ++p) for(int m=0; m<6; ++m) res.max_t[p][m] = -1;

        for (int i = 0; i < 7; ++i) {
            if (counts[i] >= 1) {
                int sub_code = code - pow5_z[i];
                const SuitResult& sub = table_z[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<6; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], (int)sub.max_t[p][m]);
            }
            if (counts[i] >= 2) {
                int sub_code = code - 2 * pow5_z[i];
                const SuitResult& sub = table_z[sub_code];
                for(int m=0; m<6; ++m) {
                    if(sub.max_t[0][m] != -1) res.max_t[1][m] = max((int)res.max_t[1][m], (int)sub.max_t[0][m]);
                    for(int p=0; p<2; ++p)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m] = max((int)res.max_t[p][m], sub.max_t[p][m] + 1);
                }
            }
            if (counts[i] >= 3) {
                int sub_code = code - 3 * pow5_z[i];
                const SuitResult& sub = table_z[sub_code];
                for(int p=0; p<2; ++p)
                    for(int m=0; m<5; ++m)
                        if(sub.max_t[p][m] != -1) res.max_t[p][m+1] = max((int)res.max_t[p][m+1], (int)sub.max_t[p][m]);
            }
        }
        table_z[code] = res;
    }
}

// ==========================================
// 3. 靜態啟動器：程式開啟瞬間自動產生查表
// ==========================================
struct TableInitializer {
    TableInitializer() {
        // 記錄開始時間
        auto start = std::chrono::high_resolution_clock::now();
        
        init_tables(); // 執行 195 萬次窮舉
        
        // 記錄結束時間並計算毫秒差
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> elapsed = end - start;
        
        std::cout << "======================================\n";
        std::cout << "[init report] shanten table finished！\n";
        std::cout << "[tome] " << elapsed.count() << " ms\n";
        std::cout << "======================================\n\n";
    }
};
static TableInitializer initializer;

// ==========================================
// 4. 合併器：將四個花色的結果疊加
// ==========================================
inline SuitResult merge_results(const SuitResult& a, const SuitResult& b) {
    SuitResult res;
    for(int p=0; p<2; ++p) for(int m=0; m<6; ++m) res.max_t[p][m] = -1;

    for (int p1 = 0; p1 <= 1; ++p1) {
        for (int m1 = 0; m1 <= 5; ++m1) {
            if (a.max_t[p1][m1] == -1) continue;
            for (int p2 = 0; p2 <= 1 - p1; ++p2) {  // 台灣麻將最多只能有 1 個雀頭
                for (int m2 = 0; m2 <= 5 - m1; ++m2) { // 台灣麻將最多只需要 5 個面子
                    if (b.max_t[p2][m2] == -1) continue;
                    int p = p1 + p2;
                    int m = m1 + m2;
                    res.max_t[p][m] = max((int)res.max_t[p][m], a.max_t[p1][m1] + b.max_t[p2][m2]);
                }
            }
        }
    }
    return res;
}

// ==========================================
// 5. 最高機密：極速向聽數入口函式
// ==========================================
// ==========================================
// 5. 自動識別副露：極速向聽數入口函式
// ==========================================
int calculate_shanten(const Hand& hand) {
    int code_m = 0, code_p = 0, code_s = 0, code_z = 0;
    int total_tiles = 0; // 用來計算目前手上有幾張暗牌

    // 1. 壓縮編碼，同時計算總張數
    // 雖然多了一個累加動作，但在 C++ 中這對效能的影響幾乎為零
    for(int i=0; i<9; ++i) {
        code_m = code_m * 5 + hand.tiles[i];
        total_tiles += hand.tiles[i];
    }
    for(int i=0; i<9; ++i) {
        code_p = code_p * 5 + hand.tiles[9+i];
        total_tiles += hand.tiles[9+i];
    }
    for(int i=0; i<9; ++i) {
        code_s = code_s * 5 + hand.tiles[18+i];
        total_tiles += hand.tiles[18+i];
    }
    for(int i=0; i<7; ++i) {
        code_z = code_z * 5 + hand.tiles[27+i];
        total_tiles += hand.tiles[27+i];
    }

    // 2. 核心公式：根據總張數自動推算副露數量 f
    // 在 16 張麻將規則中，f = (17 - 總張數) / 3
    int f = (17 - total_tiles) / 3;

    // 3. 秒查表並合併
    SuitResult res = merge_results(
        merge_results(table_suit[code_m], table_suit[code_p]),
        merge_results(table_suit[code_s], table_z[code_z])
    );

    // 4. 套用台灣麻將向聽公式
    int min_shanten = 99;
    for (int p = 0; p <= 1; ++p) {
        for (int m = 0; m <= 5 - f; ++m) {
            int t = res.max_t[p][m];
            if (t != -1) {
                int use_t = min(t, 5 - f - m);
                // 最終公式：10 - 2*(面子+副露) - 有效搭子 - 雀頭
                int shanten = 10 - 2 * (m + f) - use_t - p;
                min_shanten = min(min_shanten, shanten);
            }
        }
    }
    return min_shanten;
}

// ==========================================
// 🎯 獨立測試區塊 (Unit Tests)
// ==========================================

// 輔助函式：幫我們把字串 (例如 "1m") 轉成 ID，方便寫測試案例
int get_tile_id(const std::string& s) {
    for (int i = 0; i < 34; ++i) {
        if (Mahjong::TILES_34[i] == s) return i;
    }
    return -1;
}

// 輔助函式：執行單一測試並印出結果
void run_test(const std::string& test_name, const std::vector<std::string>& tiles_str, int expected_shanten) {
    Hand h;
    std::vector<int> ids;
    for (const auto& s : tiles_str) ids.push_back(get_tile_id(s));
    
    // 將 ID 載入 C++ 手牌 (全部視為暗牌)
    h.loadFromInts(ids, false);
    
    // 呼叫黑盒子計算向聽數
    int actual_shanten = calculate_shanten(h);
    
    std::cout << "測試 [" << test_name << "]: ";
    if (actual_shanten == expected_shanten) {
        std::cout << "✅ 通過! (向聽數: " << actual_shanten << ")\n";
    } else {
        std::cout << "❌ 失敗! (預期: " << expected_shanten << ", 實際: " << actual_shanten << ")\n";
    }
}

// 主程式入口 (改名以供 PyBind11 編譯通過)
int test_main() {
    system("chcp 65001 > nul");
    std::cout << "=== 開始測試自動副露識別 ===\n";

    // 測試 A：16 張全暗牌 (0 組副露)
    run_test("16張全暗牌-聽牌", 
        {"1m","2m","3m", "4p","5p","6p", "7s","8s","9s", "1z","1z","1z", "2z","2z","2z", "3z"}, 
        0);

    // 測試 B：剩下 10 張暗牌 (自動識別為 2 組副露)
    // 假設已經吃了兩組面子，手上的 10 張是：3面子+1雀頭+1廢牌 -> 聽牌
    run_test("10張暗牌-自動識別2副露-聽牌", 
        {"1m","2m","3m", "4p","5p","6p", "1z","1z","1z", "2z"}, 
        0);

    // 測試 C：剩下 7 張暗牌 (自動識別為 3 組副露)
    // 假設已經副露三組，手上的 7 張是：2面子+1雀頭+1單張 -> 聽牌
    run_test("7張暗牌-自動識別3副露-聽牌", 
        {"1m","2m","3m", "4p","5p","6p", "1z"}, 
        0);

    // 測試 D：極端狀況 - 剩下 1 張暗牌 (自動識別為 5 組副露)
    // 全部都吃碰完了，單吊最後一張胡牌 -> 0 向聽
    run_test("1張暗牌-自動識別5副露-聽牌", 
        {"1z"}, 
        0);

    std::cout << "============================\n";
    return 0;
}