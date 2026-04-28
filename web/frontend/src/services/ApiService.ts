import { IS_MOCK_MODE, API_BASE_URL } from '../config';

export class ApiService {
  /**
   * 啟動 Agent Session
   * @param {string} userMessage - 使用者輸入的指令
   * @param {function} onMessage - 接收到新事件的回呼函數 (event: any) => void
   * @param {function} onFinish - 任務完成的回呼函數 () => void
   * @param {function} onError - 發生錯誤的回呼函數 (error: string) => void
   * @returns {function} abortFunction - 呼叫此函數可中斷連線
   */
  static startAgentSession(
    userMessage: string,
    onMessage: (data: any) => void,
    onFinish: () => void,
    onError: (error: string) => void
  ) {
    if (IS_MOCK_MODE) {
      // 3. 明日 Demo 專用：Mock 演示模式
      let isAborted = false;
      
      const runMockSequence = async () => {
        try {
          if (isAborted) return;
          
          const delay = (ms: number) => new Promise(r => setTimeout(r, ms));

          // [1s] 主管接收指令
          await delay(1000);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Supervisor',
            content: `接收到使用者指令：「${userMessage}」。開始分析局勢與調度任務。`
          });

          // [3.5s] 主管分派任務給總工程師
          await delay(2500);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Supervisor',
            content: '呼叫 Strategic 總工程師，請針對防禦理論進行知識庫(RAG)檢索與策略擬定。'
          });

          // [6.5s] 總工程師使用工具檢索
          await delay(3000);
          if (isAborted) return;
          onMessage({
            type: 'tool_call',
            sender: 'Strategic',
            content: '調用 tool_retrieve_context 檢索知識庫 (關鍵字: 壁理論, 防禦時機)'
          });

          // [10s] 總工程師回報策略
          await delay(3500);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Strategic',
            content: '根據 RAG 歷史演化數據：若超過 12 巡且向聽數 >= 2，勝率期望值將劇降，應強制轉為防守模式。建議修改 apply_situational_tactics 的防禦權重。交由 Coding Agent 實作。'
          });

          // [13.5s] 軟體工程師接手
          await delay(3500);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Coding',
            content: '收到 Strategic 的策略藍圖。準備修改核心演算法 core/sandbox/tactics.cpp。'
          });

          // [17s] 軟體工程師執行工具修改檔案
          await delay(3500);
          if (isAborted) return;
          onMessage({
            type: 'tool_call',
            sender: 'Coding',
            content: '調用 edit_code_segment 修改 tactics.cpp 中的 apply_situational_tactics 函式'
          });

          // [20s] 前端展示代碼 Diff
          await delay(3000);
          if (isAborted) return;
          onMessage({
            type: 'diff',
            sender: 'Coding',
            content: `// [修改前]\n// if (turn > 12 && shanten >= 2) {\n//    defense_weight += 10;\n// }\n\n// [修改後]\nif (turn > 12 && shanten >= 2) {\n    defense_weight += 50; // 大幅降低分數以強制防守\n}`
          });
          
          // [22s] 軟體工程師完成工作
          await delay(2000);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Coding',
            content: '代碼注入成功，編譯檢查通過。交接給 QA 測試工程師進行勝率模擬測試。'
          });

          // [25s] QA 開始測試
          await delay(3000);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'QA',
            content: '開始執行十萬局蒙地卡羅麻將模擬測試...請稍候。'
          });

          // [29s] QA 回報勝率與完成
          await delay(4000);
          if (isAborted) return;
          onMessage({
            type: 'metric',
            sender: 'QA',
            content: 0.65 // 勝率跳到 65%
          });
          onMessage({
            type: 'thought',
            sender: 'QA',
            content: '測試完成！新版防禦權重使得放銃率下降 12%，整體勝率顯著提升至 65.0%。結果令人滿意。'
          });

          // [31.5s] 主管結案
          await delay(2500);
          if (isAborted) return;
          onMessage({
            type: 'thought',
            sender: 'Supervisor',
            content: '優化任務圓滿達成，策略與程式碼均已就緒，系統返回待命狀態。'
          });

          await delay(1500);
          if (isAborted) return;
          onFinish();

        } catch (e) {
          onError('Mock sequence error');
        }
      };

      runMockSequence();

      return () => {
        isAborted = true;
      };
    } else {
      // 2. 後端與 Agent 接入點 (真實 SSE 連線)
      // TODO: Connect to Real API
      const url = `${API_BASE_URL}?message=${encodeURIComponent(userMessage)}`;
      const eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'finish') {
            onFinish();
            eventSource.close();
          } else if (data.type === 'error') {
             // 異常處理：需捕捉 429 Resource Exhausted 等 Rate Limit 錯誤並在 UI 顯示警告
            onError(data.content || '未知的後端錯誤');
            eventSource.close();
          } else {
            // data.type 可能是 'message', 'thought', 'tool_call', 'diff', 'metric' 等
            // 如果後端目前只吐 'message'，前端這裡可以適當轉換或直接透傳
            
            // 嘗試從字串解析是否包含特殊的格式，如果沒有則當成 thought
            // 在此先將所有 'message' 轉為 'thought' 供日誌顯示
            let type = data.type;
            if (type === 'message') {
                type = 'thought';
            }
            onMessage({
                ...data,
                type
            });
          }
        } catch (err) {
          console.error("SSE parse error", err);
        }
      };

      eventSource.onerror = (err) => {
        console.error("SSE connection error", err);
        onError('連線異常，或遇到 429 Resource Exhausted 等 Rate Limit 錯誤。請確認後端是否啟動並檢查日誌。');
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    }
  }
}
