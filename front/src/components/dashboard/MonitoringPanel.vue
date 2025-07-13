<template>
  <div class="monitoring-panel">
    <div class="panel-header">
      <MonitorIcon class="panel-icon" />
      <span class="panel-title">工控机状态监控</span>
    </div>
    
    <div class="monitoring-cards">
      <!-- CPU状态 -->
      <div class="monitor-card">
        <div class="card-header">
          <CpuIcon class="card-icon" />
          <span class="card-title">CPU状态</span>
        </div>
        <div class="card-content">
          <div class="metric-value">{{ cpuUsage }}%</div>
          <div class="metric-bar">
            <div class="progress-bar">
              <div 
                class="progress-fill cpu-fill"
                :style="{ width: cpuUsage + '%' }"
              ></div>
            </div>
          </div>
          <div class="metric-detail">
            <ThermometerIcon class="detail-icon" />
            <span class="detail-text">温度: {{ cpuTemp }}°C</span>
          </div>
        </div>
      </div>
      
      <!-- 内存使用 -->
      <div class="monitor-card">
        <div class="card-header">
          <MemoryIcon class="card-icon" />
          <span class="card-title">内存使用</span>
        </div>
        <div class="card-content">
          <div class="metric-value">{{ memoryUsage }}%</div>
          <div class="metric-bar">
            <div class="progress-bar">
              <div 
                class="progress-fill memory-fill"
                :style="{ width: memoryUsage + '%' }"
              ></div>
            </div>
          </div>
          <div class="metric-detail">
            <DatabaseIcon class="detail-icon" />
            <span class="detail-text">已用: {{ memoryUsed }} / {{ memoryTotal }}</span>
          </div>
        </div>
      </div>
      
      <!-- 电池状态 -->
      <div class="monitor-card">
        <div class="card-header">
          <BatteryIcon class="card-icon" />
          <span class="card-title">电池状态</span>
        </div>
        <div class="card-content">
          <div class="metric-value">{{ batteryLevel }}%</div>
          <div class="metric-bar">
            <div class="progress-bar">
              <div 
                class="progress-fill battery-fill"
                :style="{ width: batteryLevel + '%' }"
              ></div>
            </div>
          </div>
          <div class="metric-detail">
            <ClockIcon class="detail-icon" />
            <span class="detail-text">预计剩余: {{ batteryRemaining }}</span>
          </div>
        </div>
      </div>
      
      <!-- 网络状态 -->
      <div class="monitor-card">
        <div class="card-header">
          <NetworkIcon class="card-icon" />
          <span class="card-title">网络状态</span>
        </div>
        <div class="card-content">
          <div class="metric-value">{{ networkType }}</div>
          <div class="network-details">
            <div class="network-item">
              <SignalIcon class="detail-icon" />
              <span class="detail-text">信号强度: {{ signalStrength }}</span>
            </div>
            <div class="network-item">
              <GlobeIcon class="detail-icon" />
              <span class="detail-text">网速: {{ networkSpeed }}</span>
            </div>
            <div class="network-item">
              <MapPinIcon class="detail-icon" />
              <span class="detail-text">位置: {{ location }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 导入图标组件
import MonitorIcon from './icons/MonitorIcon.vue'
import CpuIcon from './icons/CpuIcon.vue'
import MemoryIcon from './icons/MemoryIcon.vue'
import BatteryIcon from './icons/BatteryIcon.vue'
import NetworkIcon from './icons/NetworkIcon.vue'
import ThermometerIcon from './icons/ThermometerIcon.vue'
import DatabaseIcon from './icons/DatabaseIcon.vue'
import ClockIcon from './icons/ClockIcon.vue'
import SignalIcon from './icons/SignalIcon.vue'
import GlobeIcon from './icons/GlobeIcon.vue'
import MapPinIcon from './icons/MapPinIcon.vue'

// 响应式数据
const cpuUsage = ref(45)
const cpuTemp = ref(56)
const memoryUsage = ref(38)
const memoryUsed = ref('3.2GB')
const memoryTotal = ref('8GB')
const batteryLevel = ref(78)
const batteryRemaining = ref('4小时22分')
const networkType = ref('5G')
const signalStrength = ref('优秀')
const networkSpeed = ref('86 Mbps')
const location = ref('北京海淀实验小学')

// 定时器
let monitoringInterval = null

// 模拟数据更新
const updateMonitoringData = () => {
  // 模拟CPU使用率波动
  cpuUsage.value = Math.floor(Math.random() * 30) + 35 // 35-65%
  cpuTemp.value = Math.floor(Math.random() * 10) + 50 // 50-60°C
  
  // 模拟内存使用率波动
  memoryUsage.value = Math.floor(Math.random() * 20) + 30 // 30-50%
  
  // 模拟电池电量缓慢下降
  if (Math.random() > 0.8) {
    batteryLevel.value = Math.max(0, batteryLevel.value - 1)
    const hours = Math.floor(batteryLevel.value / 20)
    const minutes = Math.floor((batteryLevel.value % 20) * 3)
    batteryRemaining.value = `${hours}小时${minutes}分`
  }
  
  // 模拟网络速度波动
  const speeds = ['86 Mbps', '92 Mbps', '78 Mbps', '88 Mbps', '94 Mbps']
  networkSpeed.value = speeds[Math.floor(Math.random() * speeds.length)]
}

// 组件挂载时启动监控
onMounted(() => {
  monitoringInterval = setInterval(updateMonitoringData, 3000) // 每3秒更新一次
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (monitoringInterval) {
    clearInterval(monitoringInterval)
  }
})
</script>

<style scoped>
.monitoring-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.panel-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  color: #495057;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.monitoring-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.monitor-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.card-icon {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  color: #495057;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.metric-bar {
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.cpu-fill {
  background: linear-gradient(90deg, #28a745, #ffc107);
}

.memory-fill {
  background: linear-gradient(90deg, #28a745, #ffc107);
}

.battery-fill {
  background: linear-gradient(90deg, #dc3545, #28a745);
}

.metric-detail {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #6c757d;
}

.detail-icon {
  width: 12px;
  height: 12px;
  margin-right: 4px;
  color: #6c757d;
}

.detail-text {
  white-space: nowrap;
}

.network-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.network-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #6c757d;
}

.network-item .detail-icon {
  width: 12px;
  height: 12px;
  margin-right: 4px;
  color: #6c757d;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .monitoring-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .monitoring-cards {
    grid-template-columns: 1fr;
  }
  
  .monitoring-panel {
    padding: 16px;
  }
}
</style>