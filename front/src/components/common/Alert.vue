<template>
  <div v-if="visible" class="alert-overlay" @click="handleOverlayClick">
    <div class="alert-container" @click.stop>
      <div class="alert-header" :data-type="type">
        <component :is="iconComponent" class="alert-icon" />
        <h3 class="alert-title">{{ title }}</h3>
        <button class="alert-close" @click="handleClose" v-if="showClose">
          <CloseIcon />
        </button>
      </div>
      
      <div class="alert-body">
        <p class="alert-message">{{ message }}</p>
      </div>
      
      <div class="alert-footer">
        <button 
          v-if="showCancel" 
          class="alert-btn alert-btn-cancel" 
          @click="handleCancel"
        >
          {{ cancelText }}
        </button>
        <button 
          class="alert-btn alert-btn-confirm" 
          @click="handleConfirm"
          :class="buttonClass"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import CheckCircleIcon from './icons/CheckCircleIcon.vue'
import AlertTriangleIcon from './icons/AlertTriangleIcon.vue'
import XCircleIcon from './icons/XCircleIcon.vue'
import InfoIcon from './icons/InfoIcon.vue'
import CloseIcon from './icons/CloseIcon.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info', // success, warning, error, info
    validator: (value) => ['success', 'warning', 'error', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  showCancel: {
    type: Boolean,
    default: false
  },
  showClose: {
    type: Boolean,
    default: true
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  closeOnClickOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

// 根据类型显示不同的图标
const iconComponent = computed(() => {
  const iconMap = {
    success: CheckCircleIcon,
    warning: AlertTriangleIcon,
    error: XCircleIcon,
    info: InfoIcon
  }
  return iconMap[props.type] || InfoIcon
})

// 根据类型设置不同的按钮样式
const buttonClass = computed(() => {
  const classMap = {
    success: 'alert-btn-success',
    warning: 'alert-btn-warning',
    error: 'alert-btn-error',
    info: 'alert-btn-info'
  }
  return classMap[props.type] || 'alert-btn-info'
})

// 根据类型设置默认标题
const title = computed(() => {
  if (props.title) return props.title
  
  const titleMap = {
    success: '成功',
    warning: '警告',
    error: '错误',
    info: '提示'
  }
  return titleMap[props.type] || '提示'
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}

const handleClose = () => {
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnClickOverlay) {
    handleClose()
  }
}

// 组件挂载时添加键盘事件监听
onMounted(() => {
  const handleKeydown = (event) => {
    if (event.key === 'Escape' && props.visible) {
      handleClose()
    }
    if (event.key === 'Enter' && props.visible) {
      handleConfirm()
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  // 组件卸载时移除监听
  return () => {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<style scoped>
.alert-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}

.alert-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  min-width: 400px;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

.alert-header {
  display: flex;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.alert-icon {
  width: 24px;
  height: 24px;
  margin-right: 12px;
  flex-shrink: 0;
}

.alert-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
}

.alert-close {
  position: absolute;
  right: 16px;
  top: 16px;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.alert-close:hover {
  background: #f5f5f5;
  color: #333;
}

.alert-close svg {
  width: 16px;
  height: 16px;
}

.alert-body {
  padding: 16px 24px 20px;
}

.alert-message {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.alert-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 20px;
  border-top: 1px solid #f0f0f0;
}

.alert-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
  height: 36px;
  font-weight: 500;
}

.alert-btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.alert-btn-cancel:hover {
  background: #e8e8e8;
  color: #333;
}

.alert-btn-confirm {
  color: white;
}

.alert-btn-success {
  background: #52c41a;
}

.alert-btn-success:hover {
  background: #389e0d;
}

.alert-btn-warning {
  background: #faad14;
}

.alert-btn-warning:hover {
  background: #d48806;
}

.alert-btn-error {
  background: #ff4d4f;
}

.alert-btn-error:hover {
  background: #cf1322;
}

.alert-btn-info {
  background: #1890ff;
}

.alert-btn-info:hover {
  background: #096dd9;
}

/* 图标颜色 */
.alert-header .alert-icon {
  color: #1890ff;
}

.alert-header[data-type="success"] .alert-icon {
  color: #52c41a;
}

.alert-header[data-type="warning"] .alert-icon {
  color: #faad14;
}

.alert-header[data-type="error"] .alert-icon {
  color: #ff4d4f;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .alert-container {
    min-width: 320px;
    max-width: 90vw;
    margin: 0 20px;
  }
  
  .alert-header {
    padding: 16px 20px 12px;
  }
  
  .alert-body {
    padding: 12px 20px 16px;
  }
  
  .alert-footer {
    padding: 12px 20px 16px;
    flex-direction: column;
  }
  
  .alert-btn {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .alert-btn:last-child {
    margin-bottom: 0;
  }
}
</style>