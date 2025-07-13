import request from '@/utils/request'

/**
 * 导览管理相关API
 */

// 获取导览设置列表
export const getNavigationSettings = (params = {}) => {
    return request({
        url: '/navigation/settings',
        method: 'GET',
        params
    })
}

// 获取导览设置详情
export const getNavigationSettingDetail = (settingId) => {
    return request({
        url: `/navigation/settings/${settingId}`,
        method: 'GET'
    })
}

// 创建导览设置
export const createNavigationSetting = (data) => {
    return request({
        url: '/navigation/settings',
        method: 'POST',
        data
    })
}

// 更新导览设置
export const updateNavigationSetting = (settingId, data) => {
    return request({
        url: `/navigation/settings/${settingId}`,
        method: 'PUT',
        data
    })
}

// 删除导览设置
export const deleteNavigationSetting = (settingId) => {
    return request({
        url: `/navigation/settings/${settingId}`,
        method: 'DELETE'
    })
}

// 复制导览设置
export const copyNavigationSetting = (settingId, data) => {
    return request({
        url: `/navigation/settings/${settingId}/copy`,
        method: 'POST',
        data
    })
}

// 获取导览点位列表
export const getNavigationPoints = (params = {}) => {
    return request({
        url: '/navigation/points',
        method: 'GET',
        params
    })
}

// 获取导览点位详情
export const getNavigationPointDetail = (pointId) => {
    return request({
        url: `/navigation/points/${pointId}`,
        method: 'GET'
    })
}

// 创建导览点位
export const createNavigationPoint = (data) => {
    return request({
        url: '/navigation/points',
        method: 'POST',
        data
    })
}

// 更新导览点位
export const updateNavigationPoint = (pointId, data) => {
    return request({
        url: `/navigation/points/${pointId}`,
        method: 'PUT',
        data
    })
}

// 删除导览点位
export const deleteNavigationPoint = (pointId) => {
    return request({
        url: `/navigation/points/${pointId}`,
        method: 'DELETE'
    })
}

// 移动导览点位
export const moveNavigationPoint = (pointId, data) => {
    return request({
        url: `/navigation/points/${pointId}/move`,
        method: 'POST',
        data
    })
}

// 获取导览统计
export const getNavigationStatistics = () => {
    return request({
        url: '/navigation/statistics',
        method: 'GET'
    })
}

// 导出导览配置
export const exportNavigationConfig = (params = {}) => {
    return request({
        url: '/navigation/export',
        method: 'GET',
        params,
        responseType: 'blob'
    })
}

// 导入导览配置
export const importNavigationConfig = (formData) => {
    return request({
        url: '/navigation/import',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}