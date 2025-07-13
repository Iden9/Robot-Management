import { createApp } from 'vue'
import Alert from '@/components/common/Alert.vue'

// 创建单例实例
let alertInstance = null

// 显示Alert的通用方法
const showAlert = (options) => {
  return new Promise((resolve) => {
    // 如果已经有实例，先销毁
    if (alertInstance) {
      alertInstance.unmount()
      alertInstance = null
    }

    // 创建容器
    const container = document.createElement('div')
    document.body.appendChild(container)

    // 创建Alert实例
    alertInstance = createApp(Alert, {
      ...options,
      visible: true,
      onConfirm: () => {
        resolve(true)
        closeAlert()
      },
      onCancel: () => {
        resolve(false)
        closeAlert()
      },
      onClose: () => {
        resolve(false)
        closeAlert()
      }
    })

    alertInstance.mount(container)
  })
}

// 关闭Alert
const closeAlert = () => {
  if (alertInstance) {
    const container = alertInstance._container
    alertInstance.unmount()
    if (container && container.parentNode) {
      container.parentNode.removeChild(container)
    }
    alertInstance = null
  }
}

// 成功提示
export const success = (message, options = {}) => {
  return showAlert({
    type: 'success',
    message,
    title: options.title || '成功',
    showCancel: false,
    confirmText: options.confirmText || '确定',
    ...options
  })
}

// 警告提示
export const warning = (message, options = {}) => {
  return showAlert({
    type: 'warning',
    message,
    title: options.title || '警告',
    showCancel: false,
    confirmText: options.confirmText || '确定',
    ...options
  })
}

// 错误提示
export const error = (message, options = {}) => {
  return showAlert({
    type: 'error',
    message,
    title: options.title || '错误',
    showCancel: false,
    confirmText: options.confirmText || '确定',
    ...options
  })
}

// 信息提示
export const info = (message, options = {}) => {
  return showAlert({
    type: 'info',
    message,
    title: options.title || '提示',
    showCancel: false,
    confirmText: options.confirmText || '确定',
    ...options
  })
}

// 确认对话框
export const confirm = (message, options = {}) => {
  return showAlert({
    type: 'warning',
    message,
    title: options.title || '确认',
    showCancel: true,
    confirmText: options.confirmText || '确定',
    cancelText: options.cancelText || '取消',
    ...options
  })
}

// 通用Alert方法（兼容原生alert）
export const alert = (message, options = {}) => {
  return showAlert({
    type: 'info',
    message,
    title: options.title || '提示',
    showCancel: false,
    confirmText: options.confirmText || '确定',
    ...options
  })
}

// 默认导出
export default {
  success,
  warning,
  error,
  info,
  confirm,
  alert
}