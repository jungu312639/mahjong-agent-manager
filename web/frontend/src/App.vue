<script setup>
import { ref, onMounted, nextTick, shallowRef } from 'vue'
import { Terminal, Code, Activity, Play, Square, Settings, Cpu, MessageSquare, AlertTriangle } from 'lucide-vue-next'
import { ApiService } from './services/ApiService'
import { IS_MOCK_MODE } from './config'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

echarts.use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

// UI State
const userInput = ref('')
const isRunning = ref(false)
const apiError = ref('')
const logs = ref([])
const consoleRef = ref(null)

// Data State
const agents = ref([
  { id: 'Supervisor', name: '主管 (Supervisor)', status: 'idle', color: 'text-purple-400' },
  { id: 'Strategic', name: '總工程師 (Strategic)', status: 'idle', color: 'text-blue-400' },
  { id: 'Coding', name: '軟體工程師 (Coding)', status: 'idle', color: 'text-green-400' },
  { id: 'QA', name: '測試工程師 (QA)', status: 'idle', color: 'text-orange-400' },
])

const diffCode = ref(`// 等待 Agent 修改...`)
const winRates = ref([50, 50, 50, 50, 50, 50])
let currentTurn = 5

// Chart options
const chartOptions = ref({
  grid: { left: 40, right: 20, top: 20, bottom: 20 },
  tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
  xAxis: { type: 'category', data: ['T1', 'T2', 'T3', 'T4', 'T5', 'Now'] },
  yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
  series: [{ data: winRates.value, type: 'line', smooth: true, itemStyle: { color: '#3b82f6' }, areaStyle: { color: 'rgba(59, 130, 246, 0.2)' } }]
})

let abortAgentSession = null;

const appendLog = (sender, content, type = 'thought') => {
  logs.value.push({
    id: Date.now() + Math.random(),
    sender,
    content,
    type,
    time: new Date().toLocaleTimeString()
  })
  nextTick(() => {
    if (consoleRef.value) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight
    }
  })
}

const toggleRun = () => {
  if (isRunning.value) {
    if (abortAgentSession) abortAgentSession()
    isRunning.value = false
    appendLog('System', '停止優化程序', 'error')
    agents.value.forEach(a => a.status = 'idle')
    return
  }

  isRunning.value = true
  apiError.value = ''
  appendLog('System', `發動 Multi-Agent 研發引擎...`, 'thought')
  
  abortAgentSession = ApiService.startAgentSession(
    userInput.value || '開始優化',
    (data) => {
      // 根據 type 分發
      if (data.type === 'thought' || data.type === 'tool_call') {
        appendLog(data.sender, data.content, data.type)
        
        // 更新 Agent 燈號
        if (data.sender) {
           agents.value.forEach(a => a.status = 'idle')
           const agent = agents.value.find(a => a.id === data.sender)
           if (agent) agent.status = 'active'
        }
      } else if (data.type === 'diff') {
        diffCode.value = data.content
      } else if (data.type === 'metric') {
        currentTurn++
        const newWinRate = Number((data.content * 100).toFixed(1))
        winRates.value.push(newWinRate)
        winRates.value.shift()
        
        chartOptions.value = {
           ...chartOptions.value,
           xAxis: { ...chartOptions.value.xAxis, data: [...chartOptions.value.xAxis.data.slice(1), `T${currentTurn}`] },
           series: [{ ...chartOptions.value.series[0], data: [...winRates.value] }]
        }
      }
    },
    () => {
      isRunning.value = false
      agents.value.forEach(a => a.status = 'idle')
    },
    (err) => {
      apiError.value = err
      isRunning.value = false
      agents.value.forEach(a => a.status = 'idle')
      appendLog('System', err, 'error')
    }
  )
}
</script>

<template>
  <div class="flex h-screen bg-gray-900 text-gray-100 font-mono overflow-hidden">
    <!-- 左側 (20%)：側邊控制欄 -->
    <div class="w-1/5 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div class="p-4 border-b border-gray-700 font-bold flex items-center gap-2">
        <Settings class="w-5 h-5 text-blue-400" />
        控制面板
      </div>
      
      <div class="p-4">
        <div class="mb-4">
          <label class="block text-xs text-gray-400 mb-1">API 狀態</label>
          <div class="flex items-center gap-2">
            <div :class="['w-3 h-3 rounded-full', isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-500']"></div>
            <span class="text-sm">{{ isRunning ? '連線中' : '未連線' }}</span>
            <span :class="[
              'text-xs ml-auto px-2 py-0.5 rounded border',
              IS_MOCK_MODE ? 'bg-yellow-900 text-yellow-200 border-yellow-700' : 'bg-blue-900 text-blue-200 border-blue-700'
            ]">
              {{ IS_MOCK_MODE ? 'Mock Demo' : 'Production' }}
            </span>
          </div>
        </div>
        
        <div v-if="apiError" class="mb-4 p-2 bg-red-900/50 border border-red-700 rounded flex items-start gap-2 text-xs text-red-200 break-words">
           <AlertTriangle class="w-4 h-4 shrink-0 mt-0.5" />
           <span>{{ apiError }}</span>
        </div>

        <div class="mb-4">
           <label class="block text-xs text-gray-400 mb-1">戰略指示</label>
           <textarea v-model="userInput" 
                     class="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm focus:outline-none focus:border-blue-500 resize-none h-32"
                     placeholder="例如：優化防守權重..."></textarea>
        </div>

        <button @click="toggleRun" 
                :class="['w-full py-2 rounded flex items-center justify-center gap-2 font-bold transition-colors', 
                         isRunning ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-blue-600 hover:bg-blue-500 text-white']">
          <Play v-if="!isRunning" class="w-4 h-4" />
          <Square v-else class="w-4 h-4" />
          {{ isRunning ? '停止優化' : '啟動優化' }}
        </button>
      </div>
      
      <div class="mt-auto p-4 border-t border-gray-700">
         <div class="text-xs text-gray-400 mb-2">Agent 狀態燈號</div>
         <div class="space-y-2">
            <div v-for="agent in agents" :key="agent.id" class="flex items-center justify-between text-sm">
              <span :class="agent.status === 'active' ? agent.color : 'text-gray-500'">{{ agent.name }}</span>
              <div :class="['w-2 h-2 rounded-full', agent.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-gray-600']"></div>
            </div>
         </div>
      </div>
    </div>

    <!-- 中央 (45%)：任務日誌 -->
    <div class="w-[45%] flex flex-col border-r border-gray-700">
      <div class="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 font-bold gap-2">
         <Terminal class="w-5 h-5 text-gray-400" />
         中央任務日誌 (Action Log)
      </div>
      <div ref="consoleRef" class="flex-1 bg-black p-4 overflow-y-auto scroll-smooth">
         <div v-if="logs.length === 0" class="text-gray-600 text-sm italic">等待啟動...</div>
         <div v-for="log in logs" :key="log.id" class="mb-3 text-sm font-mono leading-relaxed break-words">
            <div class="flex items-center gap-2 mb-1">
               <span class="text-gray-600 text-xs">[{{ log.time }}]</span>
               <span :class="['font-bold', 
                  log.sender === 'System' ? 'text-yellow-500' : 
                  agents.find(a => a.id === log.sender)?.color || 'text-white']">
                  {{ log.sender }}
               </span>
               <span v-if="log.type === 'tool_call'" class="text-[10px] bg-indigo-900 text-indigo-200 px-1.5 py-0.5 rounded border border-indigo-700">Tool Call</span>
            </div>
            <div :class="['pl-4 border-l-2', log.type === 'tool_call' ? 'border-indigo-600 text-indigo-300' : log.type === 'error' ? 'border-red-600 text-red-400' : 'border-gray-700 text-gray-300']">
               {{ log.content }}
            </div>
         </div>
      </div>
    </div>

    <!-- 右側 (35%)：效能看板 -->
    <div class="w-[35%] flex flex-col bg-gray-900">
      <!-- 上方 Code Diff 視窗 -->
      <div class="h-1/2 flex flex-col border-b border-gray-700">
         <div class="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 font-bold gap-2">
            <Code class="w-5 h-5 text-gray-400" />
            代碼變更 (Code Diff)
         </div>
         <div class="flex-1 bg-gray-950 p-4 overflow-auto text-sm">
            <pre class="font-mono text-gray-300 whitespace-pre-wrap"><code>{{ diffCode }}</code></pre>
         </div>
      </div>
      
      <!-- 下方 ECharts 折線圖區 -->
      <div class="h-1/2 flex flex-col">
         <div class="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 font-bold gap-2">
            <Activity class="w-5 h-5 text-gray-400" />
            勝率進化軌跡
         </div>
         <div class="flex-1 p-4 bg-gray-900 flex items-center justify-center min-h-0">
             <v-chart class="w-full h-full" :option="chartOptions" autoresize />
         </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 隱藏捲軸但保留功能 */
.overflow-y-auto::-webkit-scrollbar,
.overflow-auto::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.overflow-y-auto::-webkit-scrollbar-thumb,
.overflow-auto::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}
.overflow-y-auto::-webkit-scrollbar-track,
.overflow-auto::-webkit-scrollbar-track {
  background: #111827;
}
</style>
