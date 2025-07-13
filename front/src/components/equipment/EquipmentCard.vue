<template>
  <div class="equipment-card">
    <div class="card-header">
      <div class="equipment-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#0071e4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="5" y="6" width="14" height="12" rx="2" />
          <rect x="8" y="2" width="8" height="4" rx="1" />
          <path d="M12 6v4" />
          <circle cx="9" cy="12" r="1" />
          <circle cx="15" cy="12" r="1" />
          <path d="M8 16h8" />
        </svg>
      </div>
      <div class="equipment-info">
        <div class="equipment-id">{{ equipment.id }}</div>
        <div class="equipment-location">{{ equipment.location }}</div>
      </div>
    </div>
    
    <div class="card-body">
      <div class="status-line">
        <span class="status-dot" :class="statusClass"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
      
      <div class="details-line">IP: {{ equipment.ip_address || 'N/A' }}</div>
      <div class="details-line">最后活动: {{ formatLastActive(equipment.last_active) }}</div>
      <div class="details-line">使用率: {{ equipment.usage_rate || '0%' }}</div>
      <div class="details-line">健康评分: {{ equipment.health_score || 0 }}/100</div>
    </div>
    
    <div class="card-actions">
      <button class="action-btn detail-btn" @click="$emit('detail', equipment)">详情</button>
      <button 
        class="action-btn setting-btn" 
        v-if="!equipment.is_offline && !equipment.has_error" 
        @click="$emit('setting', equipment)"
      >设置</button>
      <button 
        class="action-btn control-btn" 
        v-if="!equipment.is_offline && equipment.status === 'online'"
        @click="$emit('control', equipment)"
      >停止</button>
      <button 
        class="action-btn start-btn" 
        v-if="equipment.is_offline && !equipment.has_error"
        @click="$emit('control', equipment)"
      >启动</button>
      <button 
        class="action-btn restart-btn" 
        v-if="!equipment.has_error" 
        @click="$emit('restart', equipment)"
      >重启</button>
      <button 
        class="action-btn diagnose-btn" 
        v-if="equipment.has_error" 
        @click="$emit('diagnose', equipment)"
      >诊断</button>
      <button 
        class="action-btn delete-btn" 
        @click="$emit('delete', equipment)"
        title="删除设备"
      >
        <TrashIcon class="delete-icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TrashIcon from './icons/TrashIcon.vue'

const props = defineProps({
  equipment: {
    type: Object,
    required: true
  }
})

// 计算状态类
const statusClass = computed(() => {
  if (props.equipment.has_error) return 'status-error'
  if (props.equipment.is_offline || props.equipment.status === 'offline') return 'status-offline'
  return 'status-online'
})

// 计算状态文本
const statusText = computed(() => {
  if (props.equipment.has_error) return '离线 - 超过24小时'
  if (props.equipment.is_offline || props.equipment.status === 'offline') return '离线'
  return `在线 - ${props.equipment.status || '正常'}`
})

// 格式化最后活动时间
const formatLastActive = (lastActive) => {
  if (!lastActive) return '从未活动'
  
  try {
    const date = new Date(lastActive)
    if (isNaN(date.getTime())) return '从未活动'
    
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMins < 1) return '刚刚'
    if (diffMins < 60) return `${diffMins}分钟前`
    if (diffHours < 24) return `${diffHours}小时前`
    return `${diffDays}天前`
  } catch (error) {
    return '从未活动'
  }
}
</script>

<style scoped>
.equipment-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.equipment-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.equipment-icon svg {
  width: 24px;
  height: 24px;
}

.equipment-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.equipment-id {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.equipment-location {
  font-size: 14px;
  color: #666;
}

.card-body {
  padding: 16px;
  flex: 1;
}

.status-line {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-online {
  background-color: #52c41a;
}

.status-offline {
  background-color: #d9d9d9;
}

.status-error {
  background-color: #ff4d4f;
}

.status-text {
  font-size: 14px;
}

.details-line {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-actions {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  height: 32px;
  padding: 0 12px;
  margin-right: 8px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.detail-btn {
  background-color: #f0f0f0;
  color: #333;
}

.detail-btn:hover {
  background-color: #e6e6e6;
}

.setting-btn {
  background-color: #f0f0f0;
  color: #333;
}

.setting-btn:hover {
  background-color: #e6e6e6;
}

.control-btn {
  background-color: #ff4d4f;
  color: white;
}

.control-btn:hover {
  background-color: #cf1322;
}

.start-btn {
  background-color: #52c41a;
  color: white;
}

.start-btn:hover {
  background-color: #389e0d;
}

.restart-btn {
  background-color: #faad14;
  color: white;
}

.restart-btn:hover {
  background-color: #d48806;
}

.diagnose-btn {
  background-color: #ff4d4f;
  color: white;
}

.diagnose-btn:hover {
  background-color: #cf1322;
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  width: 32px;
  margin-right: 0;
}

.delete-btn:hover {
  background-color: #cf1322;
}

.delete-icon {
  width: 16px;
  height: 16px;
}
</style> 