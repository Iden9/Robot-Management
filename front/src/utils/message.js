import { createApp } from 'vue'
import MessageBox from '@/components/common/MessageBox.vue'

// 简单的消息提示函数
export const showMessage = (options) => {
  const {
    type = 'info',
    title = '提示',
    message = '',
    confirmText = '确定',
    cancelText = '取消',
    onConfirm = () => {},
    onCancel = () => {}
  } = options

  return new Promise((resolve) => {
    // 创建一个容器
    const container = document.createElement('div')
    document.body.appendChild(container)

    // 创建Vue应用实例
    const app = createApp(MessageBox, {
      visible: true,
      type,
      title,
      message,
      confirmText,
      cancelText,
      onConfirm: () => {
        onConfirm()
        resolve(true)
        cleanup()
      },
      onCancel: () => {
        onCancel()
        resolve(false)
        cleanup()
      },
      onClose: () => {
        resolve(false)
        cleanup()
      }
    })

    // 清理函数
    const cleanup = () => {
      setTimeout(() => {
        app.unmount()
        if (container.parentNode) {
          container.parentNode.removeChild(container)
        }
      }, 100)
    }

    // 挂载应用
    app.mount(container)
  })
}

// 便捷方法
export const message = {
  success: (msg, title = '成功') => showMessage({ type: 'success', title, message: msg }),
  error: (msg, title = '错误') => showMessage({ type: 'error', title, message: msg }),
  warning: (msg, title = '警告') => showMessage({ type: 'warning', title, message: msg }),
  info: (msg, title = '提示') => showMessage({ type: 'info', title, message: msg }),
  confirm: (msg, title = '确认', options = {}) => showMessage({ 
    type: 'confirm', 
    title, 
    message: msg,
    ...options 
  })
}