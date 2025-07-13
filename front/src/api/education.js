import request from '@/utils/request'

/**
 * 教育培训相关API
 */

// 获取教育设置列表
export const getEducationSettings = (params = {}) => {
    return request({
        url: '/education/settings',
        method: 'GET',
        params
    })
}

// 获取教育设置详情
export const getEducationSettingDetail = (settingId) => {
    return request({
        url: `/education/settings/${settingId}`,
        method: 'GET'
    })
}

// 创建教育设置
export const createEducationSetting = (data) => {
    return request({
        url: '/education/settings',
        method: 'POST',
        data
    })
}

// 更新教育设置
export const updateEducationSetting = (settingId, data) => {
    return request({
        url: `/education/settings/${settingId}`,
        method: 'PUT',
        data
    })
}

// 删除教育设置
export const deleteEducationSetting = (settingId) => {
    return request({
        url: `/education/settings/${settingId}`,
        method: 'DELETE'
    })
}

// 复制教育设置
export const copyEducationSetting = (settingId, data) => {
    return request({
        url: `/education/settings/${settingId}/copy`,
        method: 'POST',
        data
    })
}

// 获取教育统计
export const getEducationStatistics = () => {
    return request({
        url: '/education/statistics',
        method: 'GET'
    })
}

// 导出教育配置
export const exportEducationConfig = (params = {}) => {
    return request({
        url: '/education/export',
        method: 'GET',
        params,
        responseType: 'blob'
    })
}

// 导入教育配置
export const importEducationConfig = (formData) => {
    return request({
        url: '/education/import',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 预览教育设置
export const previewEducationSetting = (settingId) => {
    return request({
        url: `/education/settings/${settingId}/preview`,
        method: 'GET'
    })
}

// 应用教育设置到设备
export const applyEducationSetting = (settingId, equipmentIds) => {
    return request({
        url: `/education/settings/${settingId}/apply`,
        method: 'POST',
        data: { equipment_ids: equipmentIds }
    })
}