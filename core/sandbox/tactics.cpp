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

        return final_score;
    }

}
