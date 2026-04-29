// FINAL_ARCHITECTURE_CLEANUP_SUCCESS
// ARCHITECTURE_TEST_SUCCESS
#include "tactics.h"

namespace AgentTactics {

    double apply_situational_tactics(double original_score, int original_shanten, int k1_count, int turn) {
        double final_score = original_score;

        // ==============================================================
        // 🚧 [SANDBOX AREA] 🚧
        // LLM Coding Agent 可以在這裡自由增加 if-else 邏輯
        // 例如：根據 RAG 理論，如果 turn > 12 且 shanten >= 2，大幅降低分數以強制防守
        // ==============================================================

        // TODO: 未來 Agent 可以根據 Testbench 實驗，修改此處邏輯

        // Defensive tactic: If turn is greater than 12 and shanten is 2 or more,
        // significantly reduce the score to encourage defensive play.


        if (turn > 12 && original_shanten >= 2) {
            final_score -= 10000.0; // Significantly reduce score for defensive play
        }

        return final_score;
    }

}
