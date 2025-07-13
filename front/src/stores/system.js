import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getSystemInfo, 
    getSystemLogs, 
    getSystemPerformance, 
    createSystemBackup, 
    getBackupList,
    restoreSystemBackup,
    deleteBackup,
    getSystemConfig,
    updateSystemConfig,
    restartSystem,
    clearSystemCache,
    getSystemUpdateInfo,
    updateSystem
} from '@/api/system'

export const useSystemStore = defineStore('system', () => {
    // 状态
    const systemInfo = ref(null)
    const systemLogs = ref([])
    const systemPerformance = ref(null)
    const systemConfig = ref(null)
    const backupList = ref([])
    const updateInfo = ref(null)
    const isLoading = ref(false)
    const isBackuping = ref(false)
    const isUpdating = ref(false)

    // 获取系统信息
    const fetchSystemInfo = async () => {
        try {
            isLoading.value = true
            const response = await getSystemInfo()
            
            if (response.data) {
                systemInfo.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取系统信息失败' }
        } catch (error) {
            console.error('获取系统信息失败:', error.message)
            return { success: false, message: error.message || '获取系统信息失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取系统日志
    const fetchSystemLogs = async (params = {}) => {
        try {
            const response = await getSystemLogs(params)
            
            if (response.data) {
                systemLogs.value = response.data.logs || []
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取系统日志失败' }
        } catch (error) {
            console.error('获取系统日志失败:', error.message)
            return { success: false, message: error.message || '获取系统日志失败' }
        }
    }

    // 获取系统性能监控
    const fetchSystemPerformance = async () => {
        try {
            const response = await getSystemPerformance()
            
            if (response.data) {
                systemPerformance.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取系统性能监控失败' }
        } catch (error) {
            console.error('获取系统性能监控失败:', error.message)
            return { success: false, message: error.message || '获取系统性能监控失败' }
        }
    }

    // 创建系统备份
    const createSystemBackupAction = async (data) => {
        try {
            isBackuping.value = true
            const response = await createSystemBackup(data)
            
            if (response.data) {
                // 刷新备份列表
                await fetchBackupList()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建系统备份失败' }
        } catch (error) {
            console.error('创建系统备份失败:', error.message)
            return { success: false, message: error.message || '创建系统备份失败' }
        } finally {
            isBackuping.value = false
        }
    }

    // 获取备份列表
    const fetchBackupList = async () => {
        try {
            const response = await getBackupList()
            
            if (response.data) {
                backupList.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取备份列表失败' }
        } catch (error) {
            console.error('获取备份列表失败:', error.message)
            return { success: false, message: error.message || '获取备份列表失败' }
        }
    }

    // 恢复系统备份
    const restoreSystemBackupAction = async (backupId) => {
        try {
            isLoading.value = true
            const response = await restoreSystemBackup(backupId)
            
            if (response.code === 200) {
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '恢复系统备份失败' }
        } catch (error) {
            console.error('恢复系统备份失败:', error.message)
            return { success: false, message: error.message || '恢复系统备份失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 删除备份
    const deleteBackupAction = async (backupId) => {
        try {
            const response = await deleteBackup(backupId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                backupList.value = backupList.value.filter(item => item.id !== backupId)
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除备份失败' }
        } catch (error) {
            console.error('删除备份失败:', error.message)
            return { success: false, message: error.message || '删除备份失败' }
        }
    }

    // 获取系统配置
    const fetchSystemConfig = async () => {
        try {
            const response = await getSystemConfig()
            
            if (response.data) {
                systemConfig.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取系统配置失败' }
        } catch (error) {
            console.error('获取系统配置失败:', error.message)
            return { success: false, message: error.message || '获取系统配置失败' }
        }
    }

    // 更新系统配置
    const updateSystemConfigAction = async (data) => {
        try {
            isLoading.value = true
            const response = await updateSystemConfig(data)
            
            if (response.data) {
                systemConfig.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新系统配置失败' }
        } catch (error) {
            console.error('更新系统配置失败:', error.message)
            return { success: false, message: error.message || '更新系统配置失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 系统重启
    const restartSystemAction = async () => {
        try {
            const response = await restartSystem()
            
            if (response.code === 200) {
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '系统重启失败' }
        } catch (error) {
            console.error('系统重启失败:', error.message)
            return { success: false, message: error.message || '系统重启失败' }
        }
    }

    // 清理系统缓存
    const clearSystemCacheAction = async () => {
        try {
            const response = await clearSystemCache()
            
            if (response.code === 200) {
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '清理系统缓存失败' }
        } catch (error) {
            console.error('清理系统缓存失败:', error.message)
            return { success: false, message: error.message || '清理系统缓存失败' }
        }
    }

    // 获取系统更新信息
    const fetchSystemUpdateInfo = async () => {
        try {
            const response = await getSystemUpdateInfo()
            
            if (response.data) {
                updateInfo.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取系统更新信息失败' }
        } catch (error) {
            console.error('获取系统更新信息失败:', error.message)
            return { success: false, message: error.message || '获取系统更新信息失败' }
        }
    }

    // 系统更新
    const updateSystemAction = async () => {
        try {
            isUpdating.value = true
            const response = await updateSystem()
            
            if (response.code === 200) {
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '系统更新失败' }
        } catch (error) {
            console.error('系统更新失败:', error.message)
            return { success: false, message: error.message || '系统更新失败' }
        } finally {
            isUpdating.value = false
        }
    }

    // 清空数据
    const clearData = () => {
        systemInfo.value = null
        systemLogs.value = []
        systemPerformance.value = null
        systemConfig.value = null
        backupList.value = []
        updateInfo.value = null
    }

    return {
        // 状态
        systemInfo,
        systemLogs,
        systemPerformance,
        systemConfig,
        backupList,
        updateInfo,
        isLoading,
        isBackuping,
        isUpdating,
        
        // 动作
        fetchSystemInfo,
        fetchSystemLogs,
        fetchSystemPerformance,
        createSystemBackupAction,
        fetchBackupList,
        restoreSystemBackupAction,
        deleteBackupAction,
        fetchSystemConfig,
        updateSystemConfigAction,
        restartSystemAction,
        clearSystemCacheAction,
        fetchSystemUpdateInfo,
        updateSystemAction,
        clearData
    }
})