#pragma once

namespace AgentTactics {
    /**
     * @brief 沙盒戰術評估器 (Sandbox Tactics Evaluator)
     * LLM Agent (Coding Agent) 被允許修改這個檔案中的邏輯。
     * 它會在 tw_ukeire.cpp 中每一張侯選切牌的最終評估階段被呼叫。
     * 
     * @param original_score Expectimax 原始算出的進張期望分數
     * @param original_shanten 切牌後的原始向聽數
     * @param k1_count 原始物理進張數
     * @param turn 當前巡數
     * @return 調整後的最終期望分數 (影響 AI 最終棄牌選擇)
     */
    double apply_situational_tactics(double original_score, int original_shanten, int k1_count, int turn);
}
