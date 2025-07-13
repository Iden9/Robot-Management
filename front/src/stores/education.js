import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getEducationSettings, 
    getEducationSettingDetail, 
    createEducationSetting, 
    updateEducationSetting, 
    deleteEducationSetting,
    copyEducationSetting,
    getEducationStatistics,
    exportEducationConfig,
    importEducationConfig,
    previewEducationSetting,
    applyEducationSetting
} from '@/api/education'

export const useEducationStore = defineStore('education', () => {
    // 状态
    const educationSettings = ref([])
    const currentSetting = ref(null)
    const statistics = ref(null)
    const isLoading = ref(false)
    const pagination = ref({
        current_page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    })

    // 获取教育设置列表
    const fetchEducationSettings = async (params = {}) => {
        try {
            isLoading.value = true
            const response = await getEducationSettings(params)
            
            if (response.data) {
                educationSettings.value = response.data.settings || []
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
            
            return { success: false, message: response.message || '获取教育设置列表失败' }
        } catch (error) {
            console.error('获取教育设置列表失败:', error.message)
            return { success: false, message: error.message || '获取教育设置列表失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取教育设置详情
    const fetchEducationSettingDetail = async (settingId) => {
        try {
            const response = await getEducationSettingDetail(settingId)
            
            if (response.data) {
                currentSetting.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取教育设置详情失败' }
        } catch (error) {
            console.error('获取教育设置详情失败:', error.message)
            return { success: false, message: error.message || '获取教育设置详情失败' }
        }
    }

    // 创建教育设置
    const createEducationSettingAction = async (data) => {
        try {
            const response = await createEducationSetting(data)
            
            if (response.data) {
                // 刷新设置列表
                await fetchEducationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建教育设置失败' }
        } catch (error) {
            console.error('创建教育设置失败:', error.message)
            return { success: false, message: error.message || '创建教育设置失败' }
        }
    }

    // 更新教育设置
    const updateEducationSettingAction = async (settingId, data) => {
        try {
            const response = await updateEducationSetting(settingId, data)
            
            if (response.data) {
                // 更新本地设置列表中的数据
                const index = educationSettings.value.findIndex(item => item.id === settingId)
                if (index !== -1) {
                    educationSettings.value[index] = response.data
                }
                
                // 如果是当前查看的设置，也更新
                if (currentSetting.value && currentSetting.value.id === settingId) {
                    currentSetting.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新教育设置失败' }
        } catch (error) {
            console.error('更新教育设置失败:', error.message)
            return { success: false, message: error.message || '更新教育设置失败' }
        }
    }

    // 删除教育设置
    const deleteEducationSettingAction = async (settingId) => {
        try {
            const response = await deleteEducationSetting(settingId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                educationSettings.value = educationSettings.value.filter(item => item.id !== settingId)
                
                // 如果删除的是当前查看的设置，清空
                if (currentSetting.value && currentSetting.value.id === settingId) {
                    currentSetting.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除教育设置失败' }
        } catch (error) {
            console.error('删除教育设置失败:', error.message)
            return { success: false, message: error.message || '删除教育设置失败' }
        }
    }

    // 复制教育设置
    const copyEducationSettingAction = async (settingId, data) => {
        try {
            const response = await copyEducationSetting(settingId, data)
            
            if (response.data) {
                // 刷新设置列表
                await fetchEducationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '复制教育设置失败' }
        } catch (error) {
            console.error('复制教育设置失败:', error.message)
            return { success: false, message: error.message || '复制教育设置失败' }
        }
    }

    // 获取教育统计
    const fetchEducationStatistics = async () => {
        try {
            const response = await getEducationStatistics()
            
            if (response.data) {
                statistics.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取教育统计失败' }
        } catch (error) {
            console.error('获取教育统计失败:', error.message)
            return { success: false, message: error.message || '获取教育统计失败' }
        }
    }

    // 导出教育配置
    const exportEducationConfigAction = async (params = {}) => {
        try {
            const response = await exportEducationConfig(params)
            
            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'education_config.xlsx')
            document.body.appendChild(link)
            link.click()
            link.remove()
            
            return { success: true, message: '导出成功' }
        } catch (error) {
            console.error('导出教育配置失败:', error.message)
            return { success: false, message: error.message || '导出教育配置失败' }
        }
    }

    // 导入教育配置
    const importEducationConfigAction = async (formData) => {
        try {
            const response = await importEducationConfig(formData)
            
            if (response.data) {
                // 刷新设置列表
                await fetchEducationSettings()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '导入教育配置失败' }
        } catch (error) {
            console.error('导入教育配置失败:', error.message)
            return { success: false, message: error.message || '导入教育配置失败' }
        }
    }

    // 预览教育设置
    const previewEducationSettingAction = async (settingId) => {
        try {
            const response = await previewEducationSetting(settingId)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '预览教育设置失败' }
        } catch (error) {
            console.error('预览教育设置失败:', error.message)
            return { success: false, message: error.message || '预览教育设置失败' }
        }
    }

    // 应用教育设置到设备
    const applyEducationSettingAction = async (settingId, equipmentIds) => {
        try {
            const response = await applyEducationSetting(settingId, equipmentIds)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '应用教育设置失败' }
        } catch (error) {
            console.error('应用教育设置失败:', error.message)
            return { success: false, message: error.message || '应用教育设置失败' }
        }
    }

    // 清空数据
    const clearData = () => {
        educationSettings.value = []
        currentSetting.value = null
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
        educationSettings,
        currentSetting,
        statistics,
        isLoading,
        pagination,
        
        // 动作
        fetchEducationSettings,
        fetchEducationSettingDetail,
        createEducationSettingAction,
        updateEducationSettingAction,
        deleteEducationSettingAction,
        copyEducationSettingAction,
        fetchEducationStatistics,
        exportEducationConfigAction,
        importEducationConfigAction,
        previewEducationSettingAction,
        applyEducationSettingAction,
        clearData
    }
})