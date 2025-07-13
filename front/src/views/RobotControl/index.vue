<template>
  <div class="robot-control">
    <div class="page-header">
      <h1>机器人控制面板</h1>
      <p>实时控制G1 EDU机器人的运动和动作</p>
    </div>

    <!-- 机器人运动控制 -->
    <div class="control-section">
      <h2>机器人运动控制</h2>
      <div class="movement-control">
        <!-- 方向控制 -->
        <div class="direction-pad">
          <button 
            class="direction-btn up" 
            @mousedown="startMovement('forward')"
            @mouseup="stopMovement"
            @touchstart="startMovement('forward')"
            @touchend="stopMovement">
            ↑
          </button>
          
          <div class="middle-row">
            <button 
              class="direction-btn left" 
              @mousedown="startMovement('left')"
              @mouseup="stopMovement"
              @touchstart="startMovement('left')"
              @touchend="stopMovement">
              ←
            </button>
            
            <button 
              class="direction-btn stop" 
              @click="emergencyStop"
              :class="{ active: isEmergencyStop }">
              ■
            </button>
            
            <button 
              class="direction-btn right" 
              @mousedown="startMovement('right')"
              @mouseup="stopMovement"
              @touchstart="startMovement('right')"
              @touchend="stopMovement">
              →
            </button>
          </div>
          
          <button 
            class="direction-btn down" 
            @mousedown="startMovement('backward')"
            @mouseup="stopMovement"
            @touchstart="startMovement('backward')"
            @touchend="stopMovement">
            ↓
          </button>
        </div>

        <!-- 动作控制 -->
        <div class="action-controls">
          <button class="action-btn" @click="performAction('stand')">
            <StandIcon class="action-icon" />
            站立
          </button>
          <button class="action-btn" @click="performAction('sit')">
            <ChairIcon class="action-icon" />
            下蹲
          </button>
          <button class="action-btn" @click="performAction('dance')">
            <MusicIcon class="action-icon" />
            跳舞
          </button>
          <button class="action-btn" @click="performAction('home')">
            <HomeIcon class="action-icon" />
            回家
          </button>
        </div>
      </div>
    </div>

    <!-- 功能设置 -->
    <div class="settings-section">
      <h2>
        <SettingsIcon class="section-icon" />
        功能设置
      </h2>
      <div class="settings-card">
        <div class="setting-group">
          <h3>
            <ControlIcon class="subsection-icon" />
            控制参数设置
          </h3>
          
          <div class="setting-item">
            <label>移动速度</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="settings.speed"
                class="slider speed-slider"
                @input="updateSettings"
              />
              <span class="slider-value">{{ settings.speed }}%</span>
            </div>
          </div>

          <div class="setting-item">
            <label>转向灵敏度</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="settings.sensitivity"
                class="slider sensitivity-slider"
                @input="updateSettings"
              />
              <span class="slider-value">{{ settings.sensitivity }}%</span>
            </div>
          </div>

          <div class="setting-item">
            <label>动作幅度</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="settings.amplitude"
                class="slider amplitude-slider"
                @input="updateSettings"
              />
              <span class="slider-value">{{ settings.amplitude }}%</span>
            </div>
          </div>

          <button class="save-btn" @click="saveSettings" :disabled="isSaving">
            <LockIcon class="save-icon" />
            {{ isSaving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 状态信息 -->
    <div class="status-section">
      <h2>机器人状态</h2>
      <div class="status-grid">
        <div class="status-card">
          <div class="status-label">连接状态</div>
          <div class="status-value" :class="connectionStatus.class">
            {{ connectionStatus.text }}
          </div>
        </div>
        <div class="status-card">
          <div class="status-label">当前动作</div>
          <div class="status-value">{{ currentAction }}</div>
        </div>
        <div class="status-card">
          <div class="status-label">电池电量</div>
          <div class="status-value">{{ batteryLevel }}%</div>
        </div>
        <div class="status-card">
          <div class="status-label">运行时间</div>
          <div class="status-value">{{ runningTime }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

// 导入图标组件
import StandIcon from '@/components/robot/icons/StandIcon.vue'
import ChairIcon from '@/components/robot/icons/ChairIcon.vue'
import MusicIcon from '@/components/robot/icons/MusicIcon.vue'
import HomeIcon from '@/components/robot/icons/HomeIcon.vue'
import SettingsIcon from '@/components/robot/icons/SettingsIcon.vue'
import ControlIcon from '@/components/robot/icons/ControlIcon.vue'
import LockIcon from '@/components/robot/icons/LockIcon.vue'

// 响应式数据
const isEmergencyStop = ref(false)
const currentAction = ref('待机')
const batteryLevel = ref(85)
const runningTime = ref('02:45:30')
const isSaving = ref(false)

// 设置参数
const settings = reactive({
  speed: 50,
  sensitivity: 70,
  amplitude: 60
})

// 连接状态
const connectionStatus = computed(() => {
  return {
    text: '已连接',
    class: 'connected'
  }
})

// 移动控制相关
let movementInterval = null

const startMovement = (direction) => {
  console.log(`开始移动: ${direction}`)
  currentAction.value = getActionName(direction)
  
  // 这里可以发送实际的控制命令到机器人
  // sendRobotCommand({ action: 'move', direction, speed: settings.speed })
}

const stopMovement = () => {
  console.log('停止移动')
  currentAction.value = '待机'
  
  if (movementInterval) {
    clearInterval(movementInterval)
    movementInterval = null
  }
  
  // 发送停止命令
  // sendRobotCommand({ action: 'stop' })
}

const emergencyStop = () => {
  isEmergencyStop.value = true
  stopMovement()
  currentAction.value = '紧急停止'
  
  // 发送紧急停止命令
  // sendRobotCommand({ action: 'emergency_stop' })
  
  setTimeout(() => {
    isEmergencyStop.value = false
    currentAction.value = '待机'
  }, 2000)
}

const performAction = (action) => {
  console.log(`执行动作: ${action}`)
  currentAction.value = getActionName(action)
  
  // 发送动作命令
  // sendRobotCommand({ action: 'perform', type: action })
  
  // 模拟动作执行时间
  setTimeout(() => {
    currentAction.value = '待机'
  }, 3000)
}

const getActionName = (action) => {
  const actionMap = {
    forward: '前进',
    backward: '后退', 
    left: '左转',
    right: '右转',
    stand: '站立',
    sit: '下蹲',
    dance: '跳舞',
    home: '回到充电桩'
  }
  return actionMap[action] || action
}

const updateSettings = () => {
  console.log('更新设置:', settings)
  // 实时更新机器人参数
  // sendRobotCommand({ action: 'update_settings', settings })
}

const saveSettings = async () => {
  isSaving.value = true
  try {
    // 保存设置到后端
    console.log('保存设置:', settings)
    // await saveRobotSettings(settings)
    
    // 模拟保存延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    console.log('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
  } finally {
    isSaving.value = false
  }
}

// 模拟实时数据更新
let statusInterval = null

onMounted(() => {
  // 定期更新状态信息
  statusInterval = setInterval(() => {
    // 模拟电池电量变化
    if (Math.random() > 0.8) {
      batteryLevel.value = Math.max(0, batteryLevel.value - 1)
    }
    
    // 更新运行时间
    const [hours, minutes, seconds] = runningTime.value.split(':').map(Number)
    const totalSeconds = hours * 3600 + minutes * 60 + seconds + 1
    const newHours = Math.floor(totalSeconds / 3600)
    const newMinutes = Math.floor((totalSeconds % 3600) / 60)
    const newSeconds = totalSeconds % 60
    runningTime.value = `${String(newHours).padStart(2, '0')}:${String(newMinutes).padStart(2, '0')}:${String(newSeconds).padStart(2, '0')}`
  }, 1000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
  if (movementInterval) {
    clearInterval(movementInterval)
  }
})
</script>

<style scoped>
.robot-control {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 16px;
  color: #666;
}

.control-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.control-section h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.movement-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

/* 方向控制垫 */
.direction-pad {
  display: grid;
  grid-template-rows: auto auto auto;
  grid-template-columns: auto auto auto;
  gap: 10px;
  justify-items: center;
  align-items: center;
}

.direction-btn {
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 12px;
  background: #f5f5f5;
  color: #333;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.direction-btn:hover {
  background: #e8e8e8;
  transform: translateY(-2px);
}

.direction-btn:active {
  transform: translateY(0);
  background: #ddd;
}

.direction-btn.up {
  grid-column: 2;
  grid-row: 1;
}

.middle-row {
  grid-column: 1 / 4;
  grid-row: 2;
  display: flex;
  gap: 10px;
  align-items: center;
}

.direction-btn.down {
  grid-column: 2;
  grid-row: 3;
}

.direction-btn.stop {
  background: #ff4757;
  color: white;
  font-size: 20px;
}

.direction-btn.stop:hover {
  background: #ff3838;
}

.direction-btn.stop.active {
  background: #c23616;
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* 动作控制按钮 */
.action-controls {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: #0071e4;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-icon {
  width: 16px;
  height: 16px;
}

.action-btn:hover {
  background: #005bb5;
  transform: translateY(-2px);
}

.action-btn:active {
  transform: translateY(0);
}

/* 设置区域 */
/* .settings-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
} */

.settings-section h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #333;
}

.settings-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.setting-group h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #0071e4;
  padding-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subsection-icon {
  width: 18px;
  height: 18px;
  color: #333;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 8px;
  font-weight: 500;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #ddd;
  outline: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0071e4;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0071e4;
  cursor: pointer;
  border: none;
}

.slider-value {
  font-size: 14px;
  font-weight: 600;
  color: #0071e4;
  min-width: 40px;
  text-align: right;
}

.save-btn {
  background: #7c4dff;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.save-icon {
  width: 14px;
  height: 14px;
}

.save-btn:hover:not(:disabled) {
  background: #6a39d9;
  transform: translateY(-2px);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 状态区域 */
.status-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.status-section h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.status-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.status-value.connected {
  color: #28a745;
}

.status-value.disconnected {
  color: #dc3545;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .robot-control {
    width: 100%;
  }
  
  .control-section,
  .settings-section,
  .status-section {
    padding: 20px;
  }
  
  .direction-btn {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .action-controls {
    gap: 10px;
  }
  
  .action-btn {
    padding: 10px 15px;
    font-size: 12px;
    min-width: 70px;
    gap: 4px;
  }
  
  .action-icon {
    width: 14px;
    height: 14px;
  }
  
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}
</style>