import request from '@/utils/request'

/**
 * 系统管理相关API
 */

// 获取系统信息
export const getSystemInfo = () => {
    return request({
        url: '/system/info',
        method: 'GET'
    })
}

// 获取系统日志
export const getSystemLogs = (params = {}) => {
    return request({
        url: '/system/logs',
        method: 'GET',
        params
    })
}

// 获取系统性能监控
export const getSystemPerformance = () => {
    return request({
        url: '/system/performance',
        method: 'GET'
    })
}

// 系统备份
export const createSystemBackup = (data) => {
    return request({
        url: '/system/backup',
        method: 'POST',
        data
    })
}

// 获取备份列表
export const getBackupList = () => {
    return request({
        url: '/system/backups',
        method: 'GET'
    })
}

// 恢复系统备份
export const restoreSystemBackup = (backupId) => {
    return request({
        url: `/system/backups/${backupId}/restore`,
        method: 'POST'
    })
}

// 删除备份
export const deleteBackup = (backupId) => {
    return request({
        url: `/system/backups/${backupId}`,
        method: 'DELETE'
    })
}

// 获取系统配置
export const getSystemConfig = () => {
    return request({
        url: '/system/config',
        method: 'GET'
    })
}

// 更新系统配置
export const updateSystemConfig = (data) => {
    return request({
        url: '/system/config',
        method: 'PUT',
        data
    })
}

// 系统重启
export const restartSystem = () => {
    return request({
        url: '/system/restart',
        method: 'POST'
    })
}

// 清理系统缓存
export const clearSystemCache = () => {
    return request({
        url: '/system/clear-cache',
        method: 'POST'
    })
}

// 获取系统更新信息
export const getSystemUpdateInfo = () => {
    return request({
        url: '/system/update-info',
        method: 'GET'
    })
}

// 系统更新
export const updateSystem = () => {
    return request({
        url: '/system/update',
        method: 'POST'
    })
}