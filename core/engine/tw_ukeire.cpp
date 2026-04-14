#include "MahjongAI.h" // 引入我們剛剛寫好的 Hand 結構
#include <vector>
#include <algorithm>
#include <iostream>
#include <vector>
#include <utility>
#include <string>
#include <algorithm> // 為了 max

using namespace std;

// ==========================================
// 引入我們剛剛寫好的 Hand 結構與沙盒系統
// ==========================================
#include "../include/MahjongAI.h" 
#include "../sandbox/tactics.h"

// 假設的黑盒子 (未來實作)：向聽數計算機
int calculate_shanten(const Hand &hand);

#include "../include/score_weights.h"

// ==========================================
// 2. 輔助函式：取得打出機率
// ==========================================
inline double get_discard_prob(int turn, int idx)
{
    // 防呆：確保巡目在 1~18 之間，轉為陣列索引 (0~17)
    int t_index = max(1, min(turn, 18)) - 1;

    if (idx >= 27)
    {                                // 字牌
        bool is_value = (idx >= 31); // 31~33 是白發中 (役牌)
        return is_value ? ScoreWeights::PROB_Z_VALUE[t_index] : ScoreWeights::PROB_Z_GUEST[t_index];
    }
    else
    { // 數牌
        int num = (idx % 9) + 1;
        if (num == 1 || num == 9)
            return ScoreWeights::PROB_T_19[t_index];
        if (num == 2 || num == 8)
            return ScoreWeights::PROB_T_28[t_index];
        return ScoreWeights::PROB_T_37[t_index];
    }
}

// ==========================================
// 3. 輔助函式：吃碰判斷 (C++ 位址直接存取)
// ==========================================
inline bool can_pon(const Hand &hand, int idx)
{
    return hand.tiles[idx] >= 2;
}

inline bool can_chi(const Hand &hand, int idx)
{
    if (idx >= 27)
        return false; // 字牌不能吃

    int rel = idx % 9;
    bool has_left = (rel >= 2) && (hand.tiles[idx - 2] > 0) && (hand.tiles[idx - 1] > 0);
    bool has_middle = (rel >= 1 && rel <= 7) && (hand.tiles[idx - 1] > 0) && (hand.tiles[idx + 1] > 0);
    bool has_right = (rel <= 6) && (hand.tiles[idx + 1] > 0) && (hand.tiles[idx + 2] > 0);

    return has_left || has_middle || has_right;
}

// ==========================================
// 4. 靜態估算器：取得牌的權重 (你的完美邏輯移植)
// ==========================================
// 在參數中多加一個 bool is_winning_tile
inline double get_tile_weight(const Hand &hand, int idx, int turn, bool is_winning_tile = false) {
    double base = ScoreWeights::WEIGHT_BASE_DRAW; 
    double prob = get_discard_prob(turn, idx);
    
    if (is_winning_tile) {
        return base + (prob * ScoreWeights::WEIGHT_WINNING); 
    }

    double extra = 0.0;
    if (can_pon(hand, idx)) {
        extra = prob * ScoreWeights::WEIGHT_PON; 
    } else if (can_chi(hand, idx)) {
        extra = prob * ScoreWeights::WEIGHT_CHI; 
    }
    return base + extra;
}

// ==========================================
// 5. 結構定義：取代 Python Dictionary 的 C++ Struct
// ==========================================

// 代表「單一張有效牌」的詳細資訊 (對應你原本 list 裡面的小 dict)
struct UkeireDetail
{
    int tile_id;         // 用整數存 ID (0~33)
    int count;           // 實體剩餘張數
    double weight;       // 該牌的機率權重 (吃碰加權)
    double weighted_val; // count * weight
};

// 代表「整個手牌狀態」的進張報告 (對應 ukeire1 回傳的大 dict)
struct UkeireResult
{
    int shanten;                       // 當前向聽數
    int count;                         // 總實體進張數
    double weighted_ukeire;            // 總加權進張數
    vector<UkeireDetail> details; // 有效進張清單 (取代原本的 "list")
};

// ==========================================
// 6. 第一層進張分析 (ukeire1) 3n + 1 要摸牌
// ==========================================
// 🎯 注意：這裡我們傳入 Hand& (加上 & 符號)，代表傳參考。
// 因為我們會直接在記憶體裡「塞牌、拔牌」來測試，而不是一直複製整個手牌陣列。
UkeireResult ukeire1(Hand &hand, int turn, int current_shanten = -1)
{
    UkeireResult res; // 建立一個空的報告書
    res.count = 0;
    res.weighted_ukeire = 0.0;

    // 🎯 依賴注入：如果外面有傳算好的向聽數進來，就直接用；沒傳 (-1) 才呼叫黑盒子自己算
    res.shanten = (current_shanten != -1) ? current_shanten : calculate_shanten(hand);

    for (int i = 0; i < 34; ++i)
    {
        int remaining = hand.getRemaining(i);
        if (remaining <= 0)
            continue;

        // 1. 塞入牌，測試向聽數是否前進
        hand.tiles[i]++;
        int new_shanten = calculate_shanten(hand); // 摸入後的向聽數
        bool is_effective = (new_shanten < res.shanten);

        bool is_winning_tile = (new_shanten == -1);
        // 2. 測試完【無條件立刻拿出】，保證手牌狀態完美復原！
        hand.tiles[i]--;

        // 3. 結算有效進張
        if (is_effective)
        {
            double weight = get_tile_weight(hand, i, turn,is_winning_tile);
            double weighted_val = remaining * weight;

            // 建立一筆明細並填寫資料
            UkeireDetail detail;
            detail.tile_id = i;
            detail.count = remaining;
            detail.weight = weight;
            detail.weighted_val = weighted_val;

            // 將明細塞入清單 (對應 Python 的 append)
            res.details.push_back(detail);

            // 累加總分
            res.count += remaining;
            res.weighted_ukeire += weighted_val;
        }
    }
    return res;
}

// ==========================================
// 7. 決策層光速靜態掃描 (ukeire2) 3n + 2 要打牌
// ==========================================
// 1. 新增一個結構，用來裝 ukeire2 的回傳結果
struct Ukeire2Result {
    double best_weighted; // 最佳加權進張分數
    int best_raw;         // 最佳物理進張張數
    int best_discard;     // 為了得到這個分數，必須打掉哪張牌 (這就是 k2_discard!)
};

// 2. 升級 ukeire2 函數
Ukeire2Result ukeire2(Hand &hand, int turn) {
    int original_shanten = calculate_shanten(hand);
    double best_weighted = 0.0;
    int best_raw = 0;
    int best_discard = -1; // 新增：用來記住最佳切牌

    for (int i = 0; i < 34; ++i) {
        if (hand.tiles[i] > 0) {
            hand.tiles[i]--; // 模擬打出這張牌
            
            if (calculate_shanten(hand) == original_shanten) {
                UkeireResult res1 = ukeire1(hand, turn, original_shanten);
                
                // 如果找到更高的分數，不只記住分數，還要記住是打哪張牌 (i) 換來的！
                if (res1.weighted_ukeire > best_weighted) {
                    best_weighted = res1.weighted_ukeire;
                    best_raw = res1.count;
                    best_discard = i; 
                }
            }
            hand.tiles[i]++; // 復原手牌
        }
    }
    
    // 回傳升級版的包裹
    return {best_weighted, best_raw, best_discard};
}

// ==========================================
// 8. 結構定義：深層模擬的回傳結果
// ==========================================
struct DeepScoreDetail
{
    int tile_id;
    int left;
    double val_draw;
    double val_pon;
    double val_chi;
    string chi_shape;
    double prob;
    double weight;
    double next_ukeire;
    double weighted_val;
    double contribution;
    int k2_discard;
    string k2_waits;
};

struct DeepScoreResult
{
    double sum_score;
    double sum_k1;
    vector<DeepScoreDetail> details;
};

// ==========================================
// 10. 結構定義：最終分析報告書 (提前定義以供 Expectimax 存取)
// ==========================================
struct DPWinResult {
    double final_win_prob;         // N 巡模擬結束後的最終(累積)勝率 (供機器比較用)
    vector<double> turn_by_turn;   // index 0~N-1, 各別代表該回合當下的累積勝率 (供人類檢視用)
};

inline DPWinResult calculate_win_prob(int N, double U, double W0, double W1 = 0.0) {
    DPWinResult result;
    
    // 初始化狀態，依照我們是否處於 1 向聽來判定
    double S1 = (W1 > 0) ? 1.0 : 0.0;
    double S0 = (W1 == 0 && W0 > 0) ? 1.0 : 0.0;
    double SW = 0.0;
    
    double current_U = U;
    for (int turn = 0; turn < N; ++turn) {
        if (current_U <= 0) break;
        
        double p1 = W1 / current_U;
        double p0 = W0 / current_U;
        
        // 確保機率不超過 1
        p1 = min(1.0, p1);
        p0 = min(1.0, p0);
        
        // Markov Chain 流量更新
        double new_win = S0 * p0;
        double new_tenpai = S1 * p1;
        
        SW += new_win;
        S0 = (S0 - new_win) + new_tenpai;
        S1 -= new_tenpai;
        
        // 將此巡勝率推入 vector (保持 0.0~1.0 原值，交給前端處理百分比)
        result.turn_by_turn.push_back(SW);
        
        current_U -= 1.0; 
    }
    
    result.final_win_prob = result.turn_by_turn.empty() ? 0.0 : result.turn_by_turn.back();
    return result;
}

struct AnalyzeResult {
    int discard_tile;             // 建議打哪一張牌
    int shanten;                  // 打出後的向聽數
    UkeireResult base_ukeire;     // 第一層物理進張
    DeepScoreResult deep_result;  // 這條路線的完整期望值與細節報告
    DPWinResult dp_result;        // DP 動態規劃勝率轉換結果
};

// ==========================================
// 🏆 前置宣告 (Forward Declaration)
// ==========================================
// 因為 calculate_deep_score_optimized 會在 depth > 0 時呼叫 analyze，
// 但 analyze 的實作還沒寫出來，所以我們先宣告它存在，讓編譯器安心。
vector<AnalyzeResult> analyze_internal(Hand &hand, int turn, bool allow_pruning, int depth);

// ==========================================
// 9. 核心大腦：深度期望值運算 (Expectimax)
// ==========================================
DeepScoreResult calculate_deep_score_optimized(
    Hand &hand,
    int turn,
    int original_shanten,
    const UkeireResult &base_res,
    int depth = 0,
    bool need_details = false)
{
    DeepScoreResult result;
    result.sum_score = 0.0;
    result.sum_k1 = 0.0;

    // 🎯 1. 提取有效進張 (放棄 Python 的 set，改用 C++ 最快的 bool 陣列查表)
    bool is_valid_draw[34] = {false};
    for (const auto &detail : base_res.details)
    {
        is_valid_draw[detail.tile_id] = true;
    }

    for (int i = 0; i < 34; ++i) // k1，這手牌目前的有效進張數
    {
        if (!is_valid_draw[i])
            continue; // 廢牌直接無視！

        int remaining = hand.getRemaining(i);
        if (remaining <= 0)
            continue;

        // 🎯 2. 紀錄吃碰合法性 (必須在手牌改變前)
        bool can_pon_flag = can_pon(hand, i);
        bool can_chi_flag = false;
        string chi_shape = "";

        if (i < 27)
        {
            int rel = i % 9;
            if (rel >= 1 && rel <= 7 && hand.tiles[i - 1] > 0 && hand.tiles[i + 1] > 0)
            {
                can_chi_flag = true;
                // 這裡暫時省略字串組合以節省效能，如果你未來 UI 需要再組裝
                chi_shape = "middle";
            }
            else if (rel >= 2 && hand.tiles[i - 2] > 0 && hand.tiles[i - 1] > 0)
            {
                can_chi_flag = true;
                chi_shape = "left";
            }
            else if (rel <= 6 && hand.tiles[i + 1] > 0 && hand.tiles[i + 2] > 0)
            {
                can_chi_flag = true;
                chi_shape = "right";
            }
        }

        // 🎯 3. 模擬摸牌 (進入 17 張狀態)
hand.tiles[i]++;
        int target_shanten = original_shanten - 1;
        bool is_next_tenpai = (target_shanten == 0);

        // 🚀 Lambda 魔法：C++ 版本的內部函式
        // [&] 代表：直接抓取外面所有的變數 (包含 hand, depth, turn 等)，而且是傳參考！
        int current_k2_discard = -1; // 準備一個變數來接

        auto get_val = [&](Hand &hand_after) -> double {
            if (calculate_shanten(hand_after) > target_shanten) return 0.0;
            if (depth > 0) {
                vector<AnalyzeResult> future = analyze_internal(hand_after, turn, false, depth - 1);
                // 如果有深層未來，深層未來的最佳切牌就是 future[0].discard_tile
                if (!future.empty()) current_k2_discard = future[0].discard_tile;
                return future.empty() ? 0.0 : future[0].deep_result.sum_score;
            } else {
                // 如果是淺層未來，就從我們剛升級的 ukeire2 裡面拿 best_discard
                Ukeire2Result ukeire_data = ukeire2(hand_after, turn);
                current_k2_discard = ukeire_data.best_discard;
                return is_next_tenpai ? (double)ukeire_data.best_raw : ukeire_data.best_weighted;
            }
        };

        double val_draw = get_val(hand);
        
        // 把抓到的資訊存起來，準備給 UI 顯示
        int k2_discard = current_k2_discard;
        // 🎯 4. 乾淨俐落地扣回 16 張，絕不重複！
        hand.tiles[i]--;

        // 🎯 5. 碰牌模擬 (14張)
        double val_pon = 0.0;
        if (can_pon_flag)
        {
            hand.tiles[i] -= 2;
            hand.visible[i] += 3; // 2張來自手牌，1張來自對手打出

            val_pon = get_val(hand);

            hand.visible[i] -= 3; // 完美復原
            hand.tiles[i] += 2;
        }

        // 🎯 6. 吃牌模擬 (14張) - 窮舉所有可能的吃牌形狀並取 Max
        double val_chi = 0.0;
        if (i < 27)
        {
            int rel = i % 9;

            // 情況 A：嵌張吃 (Middle)
            if (rel >= 1 && rel <= 7 && hand.tiles[i - 1] > 0 && hand.tiles[i + 1] > 0)
            {
                hand.tiles[i - 1]--;
                hand.tiles[i + 1]--;
                hand.visible[i - 1]++;
                hand.visible[i + 1]++;
                hand.visible[i]++; // 對手打出的那張

                double val = get_val(hand);
                if (val > val_chi)
                {
                    val_chi = val;
                    chi_shape = "middle";
                }

                hand.visible[i]--; // 完美復原
                hand.visible[i - 1]--;
                hand.visible[i + 1]--;
                hand.tiles[i - 1]++;
                hand.tiles[i + 1]++;
            }

            // 情況 B：邊張吃左側 (Left)
            if (rel >= 2 && hand.tiles[i - 2] > 0 && hand.tiles[i - 1] > 0)
            {
                hand.tiles[i - 2]--;
                hand.tiles[i - 1]--;
                hand.visible[i - 2]++;
                hand.visible[i - 1]++;
                hand.visible[i]++; // 對手打出的那張

                double val = get_val(hand);
                if (val > val_chi)
                {
                    val_chi = val;
                    chi_shape = "left";
                }

                hand.visible[i]--; // 完美復原
                hand.visible[i - 2]--;
                hand.visible[i - 1]--;
                hand.tiles[i - 2]++;
                hand.tiles[i - 1]++;
            }

            // 情況 C：邊張吃右側 (Right)
            if (rel <= 6 && hand.tiles[i + 1] > 0 && hand.tiles[i + 2] > 0)
            {
                hand.tiles[i + 1]--;
                hand.tiles[i + 2]--;
                hand.visible[i + 1]++;
                hand.visible[i + 2]++;
                hand.visible[i]++; // 對手打出的那張

                double val = get_val(hand);
                if (val > val_chi)
                {
                    val_chi = val;
                    chi_shape = "right";
                }

                hand.visible[i]--; // 完美復原
                hand.visible[i + 1]--;
                hand.visible[i + 2]--;
                hand.tiles[i + 1]++;
                hand.tiles[i + 2]++;
            }
        }
        // 🎯 7. 機率疊加與結算
        double prob = get_discard_prob(turn, i);
        double weight_kamicha = prob * ScoreWeights::ACTION_MULT_KAMICHA;      
        double weight_others = prob * ScoreWeights::ACTION_MULT_OTHERS; 

        double action_multiplier = ScoreWeights::ACTION_MULT_DRAW; 
        double weighted_val = val_draw * ScoreWeights::ACTION_MULT_DRAW;

        if (val_pon > 0)
        {
            // 對家、下家打出，只能碰，無法吃
            action_multiplier += weight_others;
            weighted_val += val_pon * weight_others;
        }

        if (val_chi > 0 || val_pon > 0)
        {
            // 上家打出，能吃也能碰，極大化期望值 (取 Max)
            action_multiplier += weight_kamicha;
            double max_call_score = max(val_pon, val_chi);
            weighted_val += max_call_score * weight_kamicha;
        }

        // 結算 K1 加權與總分
        double k1_weight = remaining * action_multiplier;
        result.sum_k1 += k1_weight;

        double contribution = remaining * weighted_val;
        result.sum_score += contribution;

        // 紀錄 X 光掃描細節 (若有需要)
        if (need_details)
        {
            DeepScoreDetail detail;
            detail.tile_id = i;
            detail.left = remaining;
            detail.val_draw = val_draw;
            detail.val_pon = val_pon;
            detail.val_chi = val_chi;
            detail.chi_shape = chi_shape;
            detail.prob = prob;
            detail.weight = k1_weight;

            // 防呆：避免 action_multiplier 為 0 的除以零錯誤
            detail.next_ukeire = (action_multiplier > 0) ? (weighted_val / action_multiplier) : 0;

            detail.weighted_val = weighted_val;
            detail.contribution = contribution;
            detail.k2_discard = k2_discard;
            // k2_waits 這裡在先前 C++ 草稿中已被宣告為字串，未來可依 UI 需求補上
            result.details.push_back(detail);
        }
    } // 👈 這是 for (int i = 0; i < 34; ++i) 迴圈的結束

    return result; // ✅ 迴圈跑完所有 34 張牌後，才回傳最終總結報告
}

// ==========================================
// 11. 系統總司令：打牌決策大腦 (3n+2 張的狀態)
// ==========================================
vector<AnalyzeResult> analyze_internal(Hand& hand, int turn, bool allow_pruning, int depth) {
    vector<AnalyzeResult> results;
    int original_shanten = calculate_shanten(hand); // 目前 17 張的向聽數

    // 計算已經公開的牌數量，供 U（未知牌總量）使用
    int visible_count = 0;
    for (int i = 0; i < 34; ++i) {
        visible_count += hand.visible[i];
    }
    // 總保留海底不給摸，此處 hand (17張) 減去一張變成 16 張長度
    double current_U = ScoreWeights::TOTAL_TILES - ScoreWeights::HAND_TILES - ScoreWeights::DEAD_WALL - visible_count;
    
    // N (剩餘巡數)
    int N = max(0, ScoreWeights::MAX_TURNS - turn);

    // 遍歷手牌，嘗試打出每一張牌
    for (int i = 0; i < 34; ++i) {
        if (hand.tiles[i] > 0) {
            
            hand.tiles[i]--; // 🎬 動作：模擬打出這張牌 (進入 16 張狀態)
            
            // 只有在「打出去沒有退向聽」的情況下，才值得浪費算力去評估未來
            if (calculate_shanten(hand) == original_shanten) {
                
                // 1. 呼叫近視眼 (ukeire1)，取得基礎的有效進張名單 (這就是 K1 過濾器)
                UkeireResult base_res = ukeire1(hand, turn, original_shanten);

                // 2. 呼叫遠視眼 (calculate_deep)，計算這條路線的終極期望值！
                DeepScoreResult deep_res = calculate_deep_score_optimized(
                    hand, turn, original_shanten, base_res, depth, true
                );

                // 🚀 套用沙盒戰術 (Sandbox Tactics)
                deep_res.sum_score = AgentTactics::apply_situational_tactics(
                    deep_res.sum_score, 
                    original_shanten, 
                    base_res.count, 
                    turn
                );

                // 3. ✨ 計算 DP 勝率
                DPWinResult dp_res;
                if (original_shanten == 0) {
                    double W0 = base_res.weighted_ukeire;
                    dp_res = calculate_win_prob(N, current_U, W0, 0.0);
                } else if (original_shanten == 1) {
                    double W1 = deep_res.sum_k1;
                    double W0 = (W1 > 0) ? (deep_res.sum_score / W1) : 0.0;
                    dp_res = calculate_win_prob(N, current_U, W0, W1);
                } else {
                    dp_res.final_win_prob = 0.0;
                }

                // 4. 把這條路線的評估報告打包裝箱
                AnalyzeResult res;
                res.discard_tile = i;
                res.shanten = original_shanten;
                res.base_ukeire = base_res;
                res.deep_result = deep_res;
                res.dp_result = dp_res;
                results.push_back(res);
            }
            
            hand.tiles[i]++; // 🎬 動作：復原手牌，準備嘗試打下一張
        }
    }

    // 🏆 最終排序：四重標準排序 Tie-breaker
    sort(results.begin(), results.end(), [](const AnalyzeResult& a, const AnalyzeResult& b) {
        // 1. DP 勝率 (Win Probability)
        if (abs(a.dp_result.final_win_prob - b.dp_result.final_win_prob) > 1e-6)
            return a.dp_result.final_win_prob > b.dp_result.final_win_prob;
        
        // 2. Expectimax sum_score
        if (abs(a.deep_result.sum_score - b.deep_result.sum_score) > 1e-6)
            return a.deep_result.sum_score > b.deep_result.sum_score;
            
        // 3. 原生物理進張數 (這裡的 base_ukeire.count)
        if (a.base_ukeire.count != b.base_ukeire.count)
            return a.base_ukeire.count > b.base_ukeire.count;
            
        // 4. 切牌優先序 (字牌優先切) 
        return a.discard_tile > b.discard_tile;
    });

    return results;
}

// ==========================================
// 8. 系統大門：提供給 Python 呼叫的 API
// ==========================================
vector<AnalyzeResult> analyze_for_python(const vector<int>& py_hand_tiles, const vector<int>& py_visible_tiles, int turn, int depth = 0) {
    Hand current_hand;
    current_hand.loadFromInts(py_hand_tiles, false);
    current_hand.loadFromInts(py_visible_tiles, true);
    return analyze_internal(current_hand, turn, false, depth);
}

// ==========================================
// 🚀 PyBind11 膠水程式 (提供 Python 介面對接)
// ==========================================
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(tw_ukeire_cpp, m) {
    m.doc() = "C++ Mahjong AI Core Engine";

    m.def("is_winning_hand", [](const std::vector<int>& py_hand_tiles) {
        Hand current_hand;
        current_hand.loadFromInts(py_hand_tiles, false);
        return calculate_shanten(current_hand) == -1;
    }, "Check if the current hand is winning", py::arg("py_hand_tiles"));

    py::class_<UkeireDetail>(m, "UkeireDetail")
        .def_readwrite("tile_id", &UkeireDetail::tile_id)
        .def_readwrite("count", &UkeireDetail::count)
        .def_readwrite("weight", &UkeireDetail::weight)
        .def_readwrite("weighted_val", &UkeireDetail::weighted_val);

    py::class_<UkeireResult>(m, "UkeireResult")
        .def_readwrite("shanten", &UkeireResult::shanten)
        .def_readwrite("count", &UkeireResult::count)
        .def_readwrite("weighted_ukeire", &UkeireResult::weighted_ukeire)
        .def_readwrite("details", &UkeireResult::details);

    py::class_<DPWinResult>(m, "DPWinResult")
        .def_readwrite("final_win_prob", &DPWinResult::final_win_prob)
        .def_readwrite("turn_by_turn", &DPWinResult::turn_by_turn);

    py::class_<DeepScoreDetail>(m, "DeepScoreDetail")
        .def_readwrite("val_draw", &DeepScoreDetail::val_draw)
        .def_readwrite("val_pon", &DeepScoreDetail::val_pon)
        .def_readwrite("val_chi", &DeepScoreDetail::val_chi)
        .def_readwrite("weight", &DeepScoreDetail::weight)
        .def_readwrite("next_ukeire", &DeepScoreDetail::next_ukeire)
        .def_readwrite("weighted_val", &DeepScoreDetail::weighted_val)
        .def_readwrite("contribution", &DeepScoreDetail::contribution)
        .def_readwrite("k2_discard", &DeepScoreDetail::k2_discard);

    py::class_<DeepScoreResult>(m, "DeepScoreResult")
        .def_readwrite("sum_score", &DeepScoreResult::sum_score)
        .def_readwrite("sum_k1", &DeepScoreResult::sum_k1)
        .def_readwrite("details", &DeepScoreResult::details);

    py::class_<AnalyzeResult>(m, "AnalyzeResult")
        .def_readwrite("discard_tile", &AnalyzeResult::discard_tile)
        .def_readwrite("shanten", &AnalyzeResult::shanten)
        .def_readwrite("base_ukeire", &AnalyzeResult::base_ukeire)
        .def_readwrite("deep_result", &AnalyzeResult::deep_result)
        .def_readwrite("dp_result", &AnalyzeResult::dp_result);

    m.def("analyze", &analyze_for_python, 
          "Analyze the best discards for current hand",
          py::arg("py_hand_tiles"), 
          py::arg("py_visible_tiles"), 
          py::arg("turn") = 8, 
          py::arg("depth") = 0);

    // ==========================================
    // 🚧 假函數：供 UI 暫時呼叫以免報錯
    // ==========================================
    m.def("check_call_decision", [](py::list hand_list, py::str discard_tile, int from_seat, int my_seat, py::object visible_list, int turn) {
        py::list recommendations;
        py::dict base_stats;
        base_stats["shanten"] = 99;
        base_stats["ukeire"] = 0;
        base_stats["weighted_ukeire"] = 0.0;
        base_stats["score"] = 0.0;
        return py::make_tuple(recommendations, base_stats);
    }, py::arg("hand_list"), py::arg("discard_tile"), py::arg("from_seat"), py::arg("my_seat"), py::arg("visible_list") = py::none(), py::arg("turn") = 8);

    m.def("evaluate_call_decision", [](py::dict base_best_rec, py::dict call_best_rec, int U) {
        py::dict res;
        res["t_no_call"] = 999.0;
        res["t_call"] = 999.0;
        res["n_req"] = 0.0;
        res["n_curr"] = 0.0;
        res["is_accelerated"] = false;
        return res;
    }, py::arg("base_best_rec"), py::arg("call_best_rec"), py::arg("U"));
}