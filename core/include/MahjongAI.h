#ifndef MAHJONG_AI_H
#define MAHJONG_AI_H

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>

using namespace std;

namespace Mahjong
{

    // 34 種牌的字串對應表 (方便 Debug 與輸出)
    const vector<string> TILES_34 = {
        "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m",
        "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p",
        "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s",
        "1z", "2z", "3z", "4z", "5z", "6z", "7z"};

    inline bool isHonor(int tile_id) { return tile_id >= 27; }
}

class Hand
{
public:
    int tiles[34];   // 記錄自己手上的牌 (0~4張)
    int visible[34]; // 記錄場上可見的牌 (包含自己手牌、河底、副露)
    // 建構子：初始化陣列為 0
    Hand()
    {
        for (int i = 0; i < 34; ++i)
        {
            tiles[i] = 0;
            visible[i] = 0;
        }
    }

    // ==========================================
    // 🚀 終極優化：直接吃整數陣列 (0~33)
    // ==========================================
    void loadFromInts(const vector<int>& hand_list, bool is_visible = false) {
        for (int tile_id : hand_list) {
            // 防呆保護：確保 Python 傳來的 ID 不會越界導致 C++ 記憶體崩潰
            if (tile_id >= 0 && tile_id < 34) {
                if (is_visible) {
                    visible[tile_id]++;
                } else {
                    tiles[tile_id]++;
                }
            }
        }
    }
    // 取得某張牌在外面還剩幾張未知 (U)
    // 加上 inline 關鍵字，讓 C++ 編譯器展開它，達到極速存取
    inline int getRemaining(int tile_id) const
    {
        int rem = 4 - tiles[tile_id] - visible[tile_id];
        return (rem > 0) ? rem : 0;
    }

    // 方便 Debug：印出目前手牌
    void printHand() const
    {
        cout << "Hand: ";
        for (int i = 0; i < 34; ++i)
        {
            if (tiles[i] > 0)
            {
                cout << Mahjong::TILES_34[i] << "x" << tiles[i] << " ";
            }
        }
        cout << "\n";
    }
};

#endif // MAHJONG_AI_H