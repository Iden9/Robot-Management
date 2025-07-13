import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDashboardOverview, getDashboardCharts, getRealtimeMonitoring } from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
    // 状态
    const overview = ref(null)
    const charts = ref(null)
    const realtimeData = ref(null)
    const isLoading = ref(false)
    const lastUpdated = ref(null)

    // 获取概览数据
    const fetchOverview = async () => {
        try {
            isLoading.value = true
            const response = await getDashboardOverview()
            
            if (response.data) {
                overview.value = response.data
                lastUpdated.value = new Date()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取概览数据失败' }
        } catch (error) {
            console.error('获取概览数据失败:', error.message)
            return { success: false, message: error.message || '获取概览数据失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取图表数据
    const fetchCharts = async () => {
        try {
            const response = await getDashboardCharts()
            
            if (response.data) {
                charts.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取图表数据失败' }
        } catch (error) {
            console.error('获取图表数据失败:', error.message)
            return { success: false, message: error.message || '获取图表数据失败' }
        }
    }

    // 获取实时监控数据
    const fetchRealtimeData = async () => {
        try {
            const response = await getRealtimeMonitoring()
            
            if (response.data) {
                realtimeData.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取实时数据失败' }
        } catch (error) {
            console.error('获取实时数据失败:', error.message)
            return { success: false, message: error.message || '获取实时数据失败' }
        }
    }

    // 刷新所有数据
    const refreshAll = async () => {
        const results = await Promise.allSettled([
            fetchOverview(),
            fetchCharts(),
            fetchRealtimeData()
        ])
        
        return results.map(result => 
            result.status === 'fulfilled' ? result.value : { success: false, error: result.reason }
        )
    }

    // 清空数据
    const clearData = () => {
        overview.value = null
        charts.value = null
        realtimeData.value = null
        lastUpdated.value = null
    }

    return {
        // 状态
        overview,
        charts,
        realtimeData,
        isLoading,
        lastUpdated,
        
        // 动作
        fetchOverview,
        fetchCharts,
        fetchRealtimeData,
        refreshAll,
        clearData
    }
})