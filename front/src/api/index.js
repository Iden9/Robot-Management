/**
 * API接口统一导出
 */

// 认证相关
export * from './auth'

// 仪表板相关
export * from './dashboard'

// 设备管理相关
export * from './equipment'

// 课件管理相关
export * from './courseware'

// 导览管理相关
export * from './navigation'

// 教育培训相关
export * from './education'

// 系统管理相关
export * from './system'

// 用户管理相关
export * from './users'

// 默认导出所有API
export default {
    auth: () => import('./auth'),
    dashboard: () => import('./dashboard'),
    equipment: () => import('./equipment'),
    courseware: () => import('./courseware'),
    navigation: () => import('./navigation'),
    education: () => import('./education'),
    system: () => import('./system'),
    users: () => import('./users')
}