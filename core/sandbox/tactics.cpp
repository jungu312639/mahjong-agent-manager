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

        // 策略：多條件觸發式防禦 (Multi-condition Defensive Trigger)
        // 根據知識庫，單純依賴巡目會過早放棄進攻。此策略旨在更精準地判斷防禦時機。
        // 防禦模式的啟動條件 (Trigger Conditions for Defense Mode):
        // 1. 時機 (Timing): 遊戲進入後期 (turn > 12)。
        // 2. 自身牌效 (Own Hand): 我方離聽牌還很遠 (shanten >= 2)。
        // 3. 他家威脅 (Opponent Threat): 場上至少有一家已經鳴牌 (k1_count >= 1)。
        //    (註：此為架構限制下的近似條件，理想上應判斷副露次數>=2)
        bool should_enter_defense_mode = (turn > 12) && (original_shanten >= 2) && (k1_count >= 1);

        if (should_enter_defense_mode) {
            // 進入防禦模式，對所有非安全牌的進攻性打法（例如拆搭、切中張）進行分數懲罰。
            // 在此處降低分數後，由其他模組算出的「安全牌」的原始高分將會凸顯出來，
            // 使得 AI 傾向於選擇更安全的捨牌。
            final_score *= 0.1; // Penalty factor for aggressive moves in defensive situations.
        }

        // TODO: 未來 Agent 可以根據 Testbench 實驗，修改此處邏輯

        return final_score;
    }

}
