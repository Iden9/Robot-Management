<template>
  <div v-if="visible" class="message-box-overlay" @click="handleClose">
    <div class="message-box" @click.stop>
      <div class="message-header">
        <div class="message-icon" :class="typeClass">
          <component :is="iconComponent" />
        </div>
        <h3 class="message-title">{{ title }}</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>
      
      <div class="message-content">
        <p>{{ message }}</p>
      </div>
      
      <div class="message-actions">
        <button v-if="type === 'confirm'" class="btn btn-cancel" @click="handleCancel">
          {{ cancelText }}
        </button>
        <button class="btn btn-confirm" :class="typeClass" @click="handleConfirm">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 图标组件
const SuccessIcon = () => '✓'
const ErrorIcon = () => '✗'  
const WarningIcon = () => '⚠'
const InfoIcon = () => 'ℹ'
const QuestionIcon = () => '?'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info', // 'success', 'error', 'warning', 'info', 'confirm'
  },
  title: {
    type: String,
    default: '提示'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

const typeClass = computed(() => {
  const classes = {
    success: 'success',
    error: 'error',
    warning: 'warning',
    info: 'info',
    confirm: 'confirm'
  }
  return classes[props.type] || 'info'
})

const iconComponent = computed(() => {
  const icons = {
    success: SuccessIcon,
    error: ErrorIcon,
    warning: WarningIcon,
    info: InfoIcon,
    confirm: QuestionIcon
  }
  return icons[props.type] || InfoIcon
})

const handleConfirm = () => {
  emit('confirm')
  emit('close')
}

const handleCancel = () => {
  emit('cancel')
  emit('close')
}

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.message-box-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.message-box {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
}

.message-header {
  display: flex;
  align-items: center;
  padding: 20px 20px 0 20px;
  position: relative;
}

.message-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-weight: bold;
  font-size: 16px;
  color: white;
}

.message-icon.success {
  background-color: #52c41a;
}

.message-icon.error {
  background-color: #ff4d4f;
}

.message-icon.warning {
  background-color: #faad14;
}

.message-icon.info {
  background-color: #1890ff;
}

.message-icon.confirm {
  background-color: #722ed1;
}

.message-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  position: absolute;
  right: 20px;
  top: 20px;
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #666;
}

.message-content {
  padding: 20px;
  color: #666;
  line-height: 1.5;
}

.message-actions {
  padding: 0 20px 20px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel {
  color: #666;
}

.btn-cancel:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.btn-confirm {
  color: white;
  border: none;
}

.btn-confirm.success {
  background-color: #52c41a;
}

.btn-confirm.error {
  background-color: #ff4d4f;
}

.btn-confirm.warning {
  background-color: #faad14;
}

.btn-confirm.info {
  background-color: #1890ff;
}

.btn-confirm.confirm {
  background-color: #722ed1;
}

.btn-confirm:hover {
  opacity: 0.8;
}
</style>