import { useAuthStore } from '@/stores/auth'

/**
 * 权限指令
 * 用法：v-permission="'admin'" 或 v-permission="['admin', 'operator']"
 */
export const permission = {
  mounted(el, binding) {
    const { value } = binding
    const authStore = useAuthStore()
    
    if (!authStore.isAuthenticated) {
      el.style.display = 'none'
      return
    }
    
    const userRole = authStore.userInfo?.role
    
    if (value) {
      let hasPermission = false
      
      if (Array.isArray(value)) {
        hasPermission = value.includes(userRole)
      } else {
        hasPermission = userRole === value
      }
      
      if (!hasPermission) {
        el.style.display = 'none'
      }
    }
  },
  
  updated(el, binding) {
    // 在更新时重新检查权限
    permission.mounted(el, binding)
  }
}

/**
 * 角色指令
 * 用法：v-role="'admin'" 或 v-role="['admin', 'operator']"
 */
export const role = {
  mounted(el, binding) {
    permission.mounted(el, binding)
  },
  
  updated(el, binding) {
    permission.updated(el, binding)
  }
}