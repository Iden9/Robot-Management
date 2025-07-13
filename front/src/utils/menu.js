import { useAuthStore } from '@/stores/auth'
import { MENU_CONFIG } from '@/config/menu'
import { hasRole } from '@/utils/permission'

/**
 * 检查用户是否有访问菜单项的权限
 * @param {Object} menuItem - 菜单项配置
 * @returns {Boolean} - 是否有权限
 */
export const hasMenuPermission = (menuItem) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return false
  }
  
  // 优先使用权限代码检查
  if (menuItem.requiredPermissions && menuItem.requiredPermissions.length > 0) {
    // 检查用户是否拥有任一所需权限
    return menuItem.requiredPermissions.some(permission => 
      authStore.hasPermission(permission)
    )
  }
  
  // 兼容旧的角色系统
  if (menuItem.roles && menuItem.roles.length > 0) {
    return hasRole(menuItem.roles)
  }
  
  // 默认允许访问
  return true
}

/**
 * 获取用户可访问的菜单列表
 * @returns {Array} - 过滤后的菜单列表
 */
export const getAvailableMenus = () => {
  return MENU_CONFIG.filter(menuItem => hasMenuPermission(menuItem))
}

/**
 * 检查用户是否有访问指定路径的权限
 * @param {String} path - 路由路径
 * @returns {Boolean} - 是否有权限
 */
export const hasPathPermission = (path) => {
  const menuItem = MENU_CONFIG.find(item => item.path === path)
  if (!menuItem) {
    // 如果菜单配置中没有该路径，默认允许访问
    return true
  }
  
  return hasMenuPermission(menuItem)
}

/**
 * 根据用户权限过滤路由
 * @param {Array} routes - 路由配置数组
 * @returns {Array} - 过滤后的路由数组
 */
export const filterRoutesByPermission = (routes) => {
  return routes.filter(route => {
    // 检查路由是否在菜单配置中
    const menuItem = MENU_CONFIG.find(item => item.path === route.path)
    
    if (menuItem) {
      return hasMenuPermission(menuItem)
    }
    
    // 对于不在菜单配置中的路由，使用现有的角色检查逻辑
    if (route.meta?.roles) {
      return hasRole(route.meta.roles)
    }
    
    // 默认允许访问
    return true
  })
}

/**
 * 获取默认首页路径
 * 根据用户权限返回合适的首页
 * @returns {String} - 首页路径
 */
export const getDefaultHomePath = () => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    return '/login'
  }
  
  const availableMenus = getAvailableMenus()
  
  // 优先返回系统看板
  if (availableMenus.some(menu => menu.path === '/dashboard')) {
    return '/dashboard'
  }
  
  // 如果没有看板权限，返回第一个可访问的菜单
  if (availableMenus.length > 0) {
    return availableMenus[0].path
  }
  
  // 兜底返回教育培训页面
  return '/education'
}