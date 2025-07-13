import request from '@/utils/request'

/**
 * 仪表板相关API
 */

// 获取仪表板概览数据
export const getDashboardOverview = () => {
    return request({
        url: '/dashboard/overview',
        method: 'GET'
    })
}

// 获取图表数据
export const getDashboardCharts = () => {
    return request({
        url: '/dashboard/charts',
        method: 'GET'
    })
}

// 获取实时监控数据
export const getRealtimeMonitoring = () => {
    return request({
        url: '/dashboard/realtime',
        method: 'GET'
    })
}

// 导出仪表板数据
export const exportDashboardData = (params = {}) => {
    return request({
        url: '/dashboard/export',
        method: 'GET',
        params,
        responseType: 'blob'
    })
}