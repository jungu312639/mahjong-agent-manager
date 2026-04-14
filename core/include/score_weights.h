#pragma once

// ==========================================
// 韌體/算法 評估參數 Config
// LLM Agent 將透過修改這些數字來進化演算法
// ==========================================
namespace ScoreWeights {
    // -------------------------
    // 1. 麻將基礎參數設定
    // -------------------------
    constexpr double TOTAL_TILES = 144.0;
    constexpr double HAND_TILES = 16.0;
    constexpr double DEAD_WALL = 16.0;
    constexpr int MAX_TURNS = 18;

    // -------------------------
    // 2. 基礎進張加值權重 (Ukeire1)
    // -------------------------
    constexpr double WEIGHT_BASE_DRAW = 1.0; 
    constexpr double WEIGHT_WINNING  = 3.0;
    constexpr double WEIGHT_PON      = 3.0;
    constexpr double WEIGHT_CHI      = 1.0;

    // -------------------------
    // 3. 遠視眼 Expectimax 乘數
    // -------------------------
    constexpr double ACTION_MULT_DRAW    = 1.0; // 基礎自摸權重
    constexpr double ACTION_MULT_KAMICHA = 1.0; // 只有上家能打出的權重
    constexpr double ACTION_MULT_OTHERS  = 2.0; // 其他家能打出的權重

    // -------------------------
    // 4. 各類牌型的安全程度先驗機率分布 (第 1 ~ 18 巡)
    // -------------------------
    const double PROB_Z_GUEST[18] = {0.85, 0.88, 0.90, 0.92, 0.92, 0.85, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.15, 0.10, 0.05, 0.05, 0.05, 0.05};
    const double PROB_Z_VALUE[18] = {0.60, 0.65, 0.70, 0.75, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.15, 0.10, 0.08, 0.05, 0.05, 0.05, 0.05, 0.05};
    const double PROB_T_19[18]    = {0.20, 0.25, 0.35, 0.45, 0.55, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.05};
    const double PROB_T_28[18]    = {0.15, 0.20, 0.25, 0.35, 0.45, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.08, 0.05, 0.05, 0.05};
    const double PROB_T_37[18]    = {0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.35, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.08, 0.05, 0.05, 0.05, 0.05};
}
