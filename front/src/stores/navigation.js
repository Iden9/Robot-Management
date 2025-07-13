import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getNavigationSettings, 
    getNavigationSettingDetail, 
    createNavigationSetting, 
    updateNavigationSetting, 
    deleteNavigationSetting,
    copyNavigationSetting,
    getNavigationPoints,
    getNavigationPointDetail,
    createNavigationPoint,
    updateNavigationPoint,
    deleteNavigationPoint,
    moveNavigationPoint,
    getNavigationStatistics,
    exportNavigationConfig,
    importNavigationConfig
} from '@/api/navigation'

export const useNavigationStore = defineStore('navigation', () => {
    // 状态
    const navigationSettings = ref([])
    const navigationPoints = ref([])
    const currentSetting = ref(null)
    const currentPoint = ref(null)
    const statistics = ref(null)
    const isLoading = ref(false)
    const pagination = ref({
        current_page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    })

    // 获取导览设置列表
    const fetchNavigationSettings = async (params = {}) => {
        try {
            isLoading.value = true
            const response = await getNavigationSettings(params)
            
            if (response.data) {
                navigationSettings.value = response.data.settings || []
                pagination.value = {
                    current_page: response.data.current_page || 1,
                    per_page: response.data.per_page || 20,
                    total: response.data.total || 0,
                    pages: response.data.pages || 1,
                    has_next: response.data.has_next || false,
                    has_prev: response.data.has_prev || false
                }
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取导览设置列表失败' }
        } catch (error) {
            console.error('获取导览设置列表失败:', error.message)
            return { success: false, message: error.message || '获取导览设置列表失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取导览设置详情
    const fetchNavigationSettingDetail = async (settingId) => {
        try {
            const response = await getNavigationSettingDetail(settingId)
            
            if (response.data) {
                currentSetting.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取导览设置详情失败' }
        } catch (error) {
            console.error('获取导览设置详情失败:', error.message)
            return { success: false, message: error.message || '获取导览设置详情失败' }
        }
    }

    // 创建导览设置
    const createNavigationSettingAction = async (data) => {
        try {
            const response = await createNavigationSetting(data)
            
            if (response.data) {
                // 刷新设置列表
                await fetchNavigationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建导览设置失败' }
        } catch (error) {
            console.error('创建导览设置失败:', error.message)
            return { success: false, message: error.message || '创建导览设置失败' }
        }
    }

    // 更新导览设置
    const updateNavigationSettingAction = async (settingId, data) => {
        try {
            const response = await updateNavigationSetting(settingId, data)
            
            if (response.data) {
                // 更新本地设置列表中的数据
                const index = navigationSettings.value.findIndex(item => item.id === settingId)
                if (index !== -1) {
                    navigationSettings.value[index] = response.data
                }
                
                // 如果是当前查看的设置，也更新
                if (currentSetting.value && currentSetting.value.id === settingId) {
                    currentSetting.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新导览设置失败' }
        } catch (error) {
            console.error('更新导览设置失败:', error.message)
            return { success: false, message: error.message || '更新导览设置失败' }
        }
    }

    // 删除导览设置
    const deleteNavigationSettingAction = async (settingId) => {
        try {
            const response = await deleteNavigationSetting(settingId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                navigationSettings.value = navigationSettings.value.filter(item => item.id !== settingId)
                
                // 如果删除的是当前查看的设置，清空
                if (currentSetting.value && currentSetting.value.id === settingId) {
                    currentSetting.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除导览设置失败' }
        } catch (error) {
            console.error('删除导览设置失败:', error.message)
            return { success: false, message: error.message || '删除导览设置失败' }
        }
    }

    // 复制导览设置
    const copyNavigationSettingAction = async (settingId, data) => {
        try {
            const response = await copyNavigationSetting(settingId, data)
            
            if (response.data) {
                // 刷新设置列表
                await fetchNavigationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '复制导览设置失败' }
        } catch (error) {
            console.error('复制导览设置失败:', error.message)
            return { success: false, message: error.message || '复制导览设置失败' }
        }
    }

    // 获取导览点位列表
    const fetchNavigationPoints = async (params = {}) => {
        try {
            const response = await getNavigationPoints(params)
            
            if (response.data) {
                navigationPoints.value = response.data.points || []
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取导览点位列表失败' }
        } catch (error) {
            console.error('获取导览点位列表失败:', error.message)
            return { success: false, message: error.message || '获取导览点位列表失败' }
        }
    }

    // 获取导览点位详情
    const fetchNavigationPointDetail = async (pointId) => {
        try {
            const response = await getNavigationPointDetail(pointId)
            
            if (response.data) {
                currentPoint.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取导览点位详情失败' }
        } catch (error) {
            console.error('获取导览点位详情失败:', error.message)
            return { success: false, message: error.message || '获取导览点位详情失败' }
        }
    }

    // 创建导览点位
    const createNavigationPointAction = async (data) => {
        try {
            const response = await createNavigationPoint(data)
            
            if (response.data) {
                // 刷新点位列表
                await fetchNavigationPoints()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建导览点位失败' }
        } catch (error) {
            console.error('创建导览点位失败:', error.message)
            return { success: false, message: error.message || '创建导览点位失败' }
        }
    }

    // 更新导览点位
    const updateNavigationPointAction = async (pointId, data) => {
        try {
            const response = await updateNavigationPoint(pointId, data)
            
            if (response.data) {
                // 更新本地点位列表中的数据
                const index = navigationPoints.value.findIndex(item => item.id === pointId)
                if (index !== -1) {
                    navigationPoints.value[index] = response.data
                }
                
                // 如果是当前查看的点位，也更新
                if (currentPoint.value && currentPoint.value.id === pointId) {
                    currentPoint.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新导览点位失败' }
        } catch (error) {
            console.error('更新导览点位失败:', error.message)
            return { success: false, message: error.message || '更新导览点位失败' }
        }
    }

    // 删除导览点位
    const deleteNavigationPointAction = async (pointId) => {
        try {
            const response = await deleteNavigationPoint(pointId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                navigationPoints.value = navigationPoints.value.filter(item => item.id !== pointId)
                
                // 如果删除的是当前查看的点位，清空
                if (currentPoint.value && currentPoint.value.id === pointId) {
                    currentPoint.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除导览点位失败' }
        } catch (error) {
            console.error('删除导览点位失败:', error.message)
            return { success: false, message: error.message || '删除导览点位失败' }
        }
    }

    // 移动导览点位
    const moveNavigationPointAction = async (pointId, data) => {
        try {
            const response = await moveNavigationPoint(pointId, data)
            
            if (response.data) {
                // 刷新点位列表
                await fetchNavigationPoints()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '移动导览点位失败' }
        } catch (error) {
            console.error('移动导览点位失败:', error.message)
            return { success: false, message: error.message || '移动导览点位失败' }
        }
    }

    // 获取导览统计
    const fetchNavigationStatistics = async () => {
        try {
            const response = await getNavigationStatistics()
            
            if (response.data) {
                statistics.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取导览统计失败' }
        } catch (error) {
            console.error('获取导览统计失败:', error.message)
            return { success: false, message: error.message || '获取导览统计失败' }
        }
    }

    // 导出导览配置
    const exportNavigationConfigAction = async (params = {}) => {
        try {
            const response = await exportNavigationConfig(params)
            
            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'navigation_config.xlsx')
            document.body.appendChild(link)
            link.click()
            link.remove()
            
            return { success: true, message: '导出成功' }
        } catch (error) {
            console.error('导出导览配置失败:', error.message)
            return { success: false, message: error.message || '导出导览配置失败' }
        }
    }

    // 导入导览配置
    const importNavigationConfigAction = async (formData) => {
        try {
            const response = await importNavigationConfig(formData)
            
            if (response.data) {
                // 刷新设置列表
                await fetchNavigationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '导入导览配置失败' }
        } catch (error) {
            console.error('导入导览配置失败:', error.message)
            return { success: false, message: error.message || '导入导览配置失败' }
        }
    }

    // 清空数据
    const clearData = () => {
        navigationSettings.value = []
        navigationPoints.value = []
        currentSetting.value = null
        currentPoint.value = null
        statistics.value = null
        pagination.value = {
            current_page: 1,
            per_page: 20,
            total: 0,
            pages: 1
        }
    }

    return {
        // 状态
        navigationSettings,
        navigationPoints,
        currentSetting,
        currentPoint,
        statistics,
        isLoading,
        pagination,
        
        // 动作
        fetchNavigationSettings,
        fetchNavigationSettingDetail,
        createNavigationSettingAction,
        updateNavigationSettingAction,
        deleteNavigationSettingAction,
        copyNavigationSettingAction,
        fetchNavigationPoints,
        fetchNavigationPointDetail,
        createNavigationPointAction,
        updateNavigationPointAction,
        deleteNavigationPointAction,
        moveNavigationPointAction,
        fetchNavigationStatistics,
        exportNavigationConfigAction,
        importNavigationConfigAction,
        clearData
    }
})