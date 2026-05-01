// FINAL_ARCHITECTURE_CLEANUP_SUCCESS
// ARCHITECTURE_TEST_SUCCESS
#include "tactics.h"

namespace AgentTactics {

    double apply_situational_tactics(double original_score, int original_shanten, int k1_count, int turn) {
        double final_score = original_score;

        // ==============================================================
        // 🚧 [SANDBOX AREA] 🚧
        // LLM Coding Agent 可以在這裡自由增加 if-else 邏輯
        // ==============================================================

        // 根據 RAG 分析，舊的防禦策略 (單純看巡目) 效果不彰。
        // 新策略：晚巡 (12巡後)，當自己手牌離聽牌還很遠 (2向聽以上)，
        // 且有任一對手已經明顯領先 (吃碰2次以上) 時，轉入高度防禦模式。
        // 在此，我們假設 k1_count 代表對手的總吃碰數。
        bool high_alert_defense = (turn > 12 && original_shanten >= 2 && k1_count >= 2);

        if (high_alert_defense) {
            // 進入高度防禦模式，大幅降低當前操作的評分，
            // 迫使 AI 選擇更安全的打法 (例如，打現物安全牌，其評分會更高)。
            // 這裡我們將原始分數乘以一個懲罰因子。
            final_score *= 0.1; // Penalty factor for high-risk situations
        }


        // TODO: 未來 Agent 可以根據 Testbench 實驗，修改此處邏輯

        return final_score;
    }

}
