import { useAuthStore } from '@/stores/auth'

/**
 * 检查用户是否有访问指定路由的权限
 * @param {Object} route - 路由对象
 * @returns {Boolean} - 是否有权限
 */
export const hasRoutePermission = (route) => {
  const authStore = useAuthStore()
  
  // 如果路由不需要认证，直接允许访问
  if (!route.meta?.requiresAuth) {
    return true
  }
  
  // 检查是否已登录
  if (!authStore.isAuthenticated) {
    return false
  }
  
  // 检查角色权限
  if (route.meta.roles && Array.isArray(route.meta.roles)) {
    const userRole = authStore.userInfo?.role
    return route.meta.roles.includes(userRole)
  }
  
  // 默认允许访问
  return true
}

/**
 * 检查用户是否有指定角色
 * @param {String|Array} roles - 角色或角色数组
 * @returns {Boolean} - 是否有权限
 */
export const hasRole = (roles) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return false
  }
  
  const userRole = authStore.userInfo?.role
  
  if (Array.isArray(roles)) {
    return roles.includes(userRole)
  }
  
  return userRole === roles
}

/**
 * 检查用户是否是管理员
 * @returns {Boolean} - 是否是管理员
 */
export const isAdmin = () => {
  const authStore = useAuthStore()
  return authStore.isAdmin
}

/**
 * 检查用户是否是操作员
 * @returns {Boolean} - 是否是操作员
 */
export const isOperator = () => {
  const authStore = useAuthStore()
  return authStore.isOperator
}

/**
 * 检查用户是否是查看者
 * @returns {Boolean} - 是否是查看者
 */
export const isViewer = () => {
  const authStore = useAuthStore()
  return authStore.isViewer
}

/**
 * 根据角色过滤菜单项
 * @param {Array} menuItems - 菜单项数组
 * @returns {Array} - 过滤后的菜单项
 */
export const filterMenuByRole = (menuItems) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return []
  }
  
  return menuItems.filter(item => {
    if (!item.meta?.roles) {
      return true
    }
    
    const userRole = authStore.userInfo?.role
    return item.meta.roles.includes(userRole)
  })
}

/**
 * 角色权限映射
 */
export const ROLE_PERMISSIONS = {
  admin: ['all'], // 管理员拥有所有权限
  operator: ['read', 'write', 'execute'], // 操作员可读可写可执行
  viewer: ['read'] // 查看者只能读
}

/**
 * 检查用户是否有指定权限
 * @param {String} permission - 权限名称
 * @returns {Boolean} - 是否有权限
 */
export const hasPermission = (permission) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return false
  }
  
  const userRole = authStore.userInfo?.role
  const rolePermissions = ROLE_PERMISSIONS[userRole] || []
  
  return rolePermissions.includes('all') || rolePermissions.includes(permission)
}