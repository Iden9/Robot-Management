import request from '@/utils/request'

/**
 * 设备管理相关API
 */

// 获取设备列表
export const getEquipmentList = (params = {}) => {
    return request({
        url: '/equipment',
        method: 'GET',
        params
    })
}

// 获取设备详情
export const getEquipmentDetail = (equipmentId) => {
    return request({
        url: `/equipment/${equipmentId}`,
        method: 'GET'
    })
}

// 创建设备
export const createEquipment = (data) => {
    return request({
        url: '/equipment',
        method: 'POST',
        data
    })
}

// 更新设备信息
export const updateEquipment = (equipmentId, data) => {
    return request({
        url: `/equipment/${equipmentId}`,
        method: 'PUT',
        data
    })
}

// 删除设备
export const deleteEquipment = (equipmentId) => {
    return request({
        url: `/equipment/${equipmentId}`,
        method: 'DELETE'
    })
}

// 批量删除设备
export const batchDeleteEquipment = (equipmentIds) => {
    return request({
        url: '/equipment/batch-delete',
        method: 'POST',
        data: { equipment_ids: equipmentIds }
    })
}

// 获取设备统计信息
export const getEquipmentStatistics = () => {
    return request({
        url: '/equipment/statistics',
        method: 'GET'
    })
}

// 设备状态控制
export const controlEquipmentStatus = (equipmentId, action) => {
    return request({
        url: `/equipment/${equipmentId}/control`,
        method: 'POST',
        data: { action }
    })
}

// 获取设备日志
export const getEquipmentLogs = (equipmentId, params = {}) => {
    return request({
        url: `/equipment/${equipmentId}/logs`,
        method: 'GET',
        params
    })
}

// 设备健康检查
export const equipmentHealthCheck = (equipmentId) => {
    return request({
        url: `/equipment/${equipmentId}/health-check`,
        method: 'POST'
    })
}

// 批量导入设备
export const batchImportEquipment = (formData) => {
    return request({
        url: '/equipment/batch-import',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 导出设备列表
export const exportEquipmentList = (params = {}) => {
    return request({
        url: '/equipment/export',
        method: 'GET',
        params,
        responseType: 'blob'
    })
}

// 下载设备导入模板
export const downloadImportTemplate = () => {
    return request({
        url: '/equipment/import-template',
        method: 'GET',
        responseType: 'blob'
    })
}