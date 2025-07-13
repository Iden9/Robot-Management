<template>
  <div class="stat-card">
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <div class="icon-container" :class="iconBgColor">
        <component :is="icon" class="icon" />
      </div>
    </div>
    
    <div class="card-value">{{ value }}</div>
    
    <div class="card-footer" :class="statusColor">
      <component :is="statusIcon" class="status-icon" v-if="statusIcon" />
      <span>{{ status }}</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  status: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    required: true
  },
  iconBgColor: {
    type: String,
    default: 'blue-bg'
  },
  statusType: {
    type: String,
    default: 'default' // 可以是 'success', 'warning', 'danger', 'info' 或 'default'
  },
  statusIcon: {
    type: Object,
    default: null
  }
})

// 计算状态的颜色类
const statusColor = computed(() => {
  switch (props.statusType) {
    case 'success':
      return 'text-success'
    case 'warning':
      return 'text-warning'
    case 'danger':
      return 'text-danger'
    case 'info':
      return 'text-info'
    default:
      return ''
  }
})
</script>

<style scoped>
.stat-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.icon-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue-bg {
  background-color: rgba(0, 113, 228, 0.1);
}

.green-bg {
  background-color: rgba(82, 196, 26, 0.1);
}

.orange-bg {
  background-color: rgba(250, 173, 20, 0.1);
}

.purple-bg {
  background-color: rgba(114, 46, 209, 0.1);
}

.icon {
  width: 24px;
  height: 24px;
  color: #0071e4;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.card-footer {
  font-size: 14px;
  display: flex;
  align-items: center;
}

.status-icon {
  margin-right: 5px;
  width: 16px;
  height: 16px;
}

.text-success {
  color: #52c41a;
}

.text-warning {
  color: #faad14;
}

.text-danger {
  color: #f5222d;
}

.text-info {
  color: #1890ff;
}
</style> 