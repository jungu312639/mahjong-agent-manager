<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Terminal, Code, Cpu, MessageSquare, Play, Square, Activity } from 'lucide-vue-next'

const logs = ref([])
const consoleRef = ref(null)
const isRunning = ref(false)
const agents = ref([
  { id: 'Supervisor', name: '主管 (Supervisor)', status: 'idle', color: 'text-purple-400' },
  { id: 'Strategic', name: '總工程師 (Strategic)', status: 'idle', color: 'text-blue-400' },
  { id: 'Coding', name: '軟體工程師 (Coding)', status: 'idle', color: 'text-green-400' },
  { id: 'QA', name: '測試工程師 (QA)', status: 'idle', color: 'text-orange-400' },
])

const currentCode = ref(`// 正在分析 score_weights.h ...
#ifndef SCORE_WEIGHTS_H
#define SCORE_WEIGHTS_H

const double UKEIRE_WEIGHT = 1.0;
const double SHANTEN_PENALTY = 50.0;

#endif`)

const winRate = ref(0.21)
const iterations = ref(0)
const userInput = ref('')

const appendLog = (sender, content, type = 'message') => {
  logs.value.push({
    id: Date.now(),
    sender,
    content,
    type,
    time: new Date().toLocaleTimeString()
  })
  
  // 自動捲動到底部
  nextTick(() => {
    if (consoleRef.value) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight
    }
  })
}

const toggleRun = async () => {
  if (isRunning.value) {
    isRunning.value = false
    appendLog('System', '停止優化程序', 'error')
    return
  }

  isRunning.value = true
  appendLog('System', '發動 Multi-Agent 研發引擎...', 'info')
  
  // 建立 SSE 連結 (由 FastAPI 提供)
  const url = `http://localhost:8000/api/run?message=${encodeURIComponent(userInput.value || '開始優化')}`
  const eventSource = new EventSource(url)
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'message') {
      appendLog(data.sender, data.content)
      // 動態更新 Agent 狀態
      const agent = agents.value.find(a => a.id === data.sender)
      if (agent) {
        agents.value.forEach(a => a.status = 'idle')
        agent.status = 'active'
      }
    } else if (data.type === 'finish') {
      isRunning.value = false
      eventSource.close()
    }
  }

  eventSource.onerror = (err) => {
    appendLog('System', '連線異常，請確認後端是否啟動', 'error')
    isRunning.value = false
    eventSource.close()
  }
}

const sendMessage = () => {
  if (!userInput.value.trim()) return
  appendLog('You', userInput.value, 'user')
  userInput.value = ''
}
</script>

<template>
  <div class="flex h-screen bg-ide-bg text-ide-text font-mono">
    <!-- 左側邊欄：代理人狀態 -->
    <div class="w-64 bg-ide-sidebar border-r border-gray-700 flex flex-col">
      <div class="p-4 border-b border-gray-700 font-bold flex items-center gap-2">
        <Cpu class="w-5 h-5 text-ide-accent" />
        AI 部門看板
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-for="agent in agents" :key="agent.id" 
             :class="['p-4 border-b border-gray-700 transition-colors', agent.status === 'active' ? 'bg-gray-800' : '']">
          <div class="flex items-center justify-between">
            <span :class="['font-semibold', agent.color]">{{ agent.name }}</span>
            <div :class="['w-2 h-2 rounded-full', agent.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-gray-500']"></div>
          </div>
          <p class="text-xs text-gray-500 mt-1 capitalize">{{ agent.status }}</p>
        </div>
      </div>
      <div class="p-4 bg-ide-panel text-xs">
        <div class="flex justify-between mb-2">
          <span>勝率:</span>
          <span class="text-green-400 font-bold">{{ (winRate * 100).toFixed(1) }}%</span>
        </div>
        <div class="flex justify-between">
          <span>迭代輪次:</span>
          <span class="text-blue-400">{{ iterations }}</span>
        </div>
      </div>
    </div>

    <!-- 中間主要區域 -->
    <div class="flex-1 flex flex-col">
      <!-- 頂部工具列 -->
      <div class="h-12 bg-ide-sidebar border-b border-gray-700 flex items-center justify-between px-4">
        <div class="flex items-center gap-2 text-sm">
          <Activity class="w-4 h-4 text-ide-accent" />
          <span>mahjong-agent/core/include/<span class="text-white">score_weights.h</span></span>
        </div>
        <div class="flex gap-2">
          <button @click="toggleRun" 
                  :class="['px-4 py-1 rounded flex items-center gap-2 text-sm font-bold', 
                           isRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-ide-accent hover:bg-blue-600']">
            <Play v-if="!isRunning" class="w-4 h-4" />
            <Square v-else class="w-4 h-4" />
            {{ isRunning ? '停止' : '啟動優化' }}
          </button>
        </div>
      </div>

      <!-- 代碼區 -->
      <div class="flex-1 bg-ide-bg overflow-auto p-4 relative">
        <div class="absolute top-2 right-4 text-[10px] text-gray-600 uppercase tracking-widest">Read Only</div>
        <pre class="text-sm font-mono leading-relaxed"><code class="text-blue-300">{{ currentCode }}</code></pre>
      </div>

      <!-- 底部 Console -->
      <div class="h-64 bg-black/50 border-t border-gray-700 flex flex-col">
        <div class="h-8 bg-ide-panel flex items-center px-4 gap-2 text-xs border-b border-gray-700">
          <Terminal class="w-4 h-4" />
          代理人日誌輸出 (LangGraph Node Stream)
        </div>
        <div ref="consoleRef" class="flex-1 overflow-y-auto p-2 scroll-smooth">
          <div v-for="log in logs" :key="log.id" class="text-sm mb-1">
            <span class="text-gray-500 text-[10px] mr-2">[{{ log.time }}]</span>
            <span :class="['font-bold mr-2', 
              log.sender === 'System' ? 'text-yellow-400' : 
              log.sender === 'You' ? 'text-white' : 
              agents.find(a => a.id === log.sender)?.color]">
              {{ log.sender }}:
            </span>
            <span class="text-ide-text">{{ log.content }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右側對話討論區 -->
    <div class="w-80 bg-ide-sidebar border-l border-gray-700 flex flex-col">
      <div class="p-4 border-b border-gray-700 font-bold flex items-center gap-2">
        <MessageSquare class="w-5 h-5 text-ide-accent" />
        戰略討論區 (RAG Support)
      </div>
      <div class="flex-1 p-4 text-xs text-gray-400 leading-relaxed italic">
        在此輸入你對演算法的想法，總工程師將會在下一輪決策時加入考量。
      </div>
      <div class="p-4 border-t border-gray-700">
        <div class="relative">
          <textarea v-model="userInput" 
                    @keyup.enter.prevent="sendMessage"
                    class="w-full bg-ide-panel border border-gray-600 rounded p-2 text-sm focus:outline-none focus:border-ide-accent resize-none h-24"
                    placeholder="告訴 AI 你對防禦戰術的建議..."></textarea>
          <div class="absolute bottom-2 right-2 flex items-center gap-1 text-[10px] text-gray-500">
            按 ENTER 送出
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 隱藏捲軸但保留功能 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
</style>
