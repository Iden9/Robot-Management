import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getEquipmentList, 
    getEquipmentDetail, 
    createEquipment, 
    updateEquipment, 
    deleteEquipment,
    getEquipmentStatistics,
    controlEquipmentStatus 
} from '@/api/equipment'

export const useEquipmentStore = defineStore('equipment', () => {
    // 状态
    const equipmentList = ref([])
    const currentEquipment = ref(null)
    const statistics = ref(null)
    const isLoading = ref(false)
    const pagination = ref({
        current_page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    })

    // 获取设备列表
    const fetchEquipmentList = async (params = {}) => {
        try {
            isLoading.value = true
            const response = await getEquipmentList(params)
            
            if (response.data) {
                equipmentList.value = response.data.equipment || []
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
            
            return { success: false, message: response.message || '获取设备列表失败' }
        } catch (error) {
            console.error('获取设备列表失败:', error.message)
            return { success: false, message: error.message || '获取设备列表失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取设备详情
    const fetchEquipmentDetail = async (equipmentId) => {
        try {
            const response = await getEquipmentDetail(equipmentId)
            
            if (response.data) {
                currentEquipment.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取设备详情失败' }
        } catch (error) {
            console.error('获取设备详情失败:', error.message)
            return { success: false, message: error.message || '获取设备详情失败' }
        }
    }

    // 创建设备
    const createEquipmentAction = async (data) => {
        try {
            const response = await createEquipment(data)
            
            if (response.data) {
                // 刷新设备列表
                await fetchEquipmentList()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建设备失败' }
        } catch (error) {
            console.error('创建设备失败:', error.message)
            return { success: false, message: error.message || '创建设备失败' }
        }
    }

    // 更新设备
    const updateEquipmentAction = async (equipmentId, data) => {
        try {
            const response = await updateEquipment(equipmentId, data)
            
            if (response.data) {
                // 更新本地设备列表中的数据
                const index = equipmentList.value.findIndex(item => item.id === equipmentId)
                if (index !== -1) {
                    equipmentList.value[index] = response.data
                }
                
                // 如果是当前查看的设备，也更新
                if (currentEquipment.value && currentEquipment.value.id === equipmentId) {
                    currentEquipment.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新设备失败' }
        } catch (error) {
            console.error('更新设备失败:', error.message)
            return { success: false, message: error.message || '更新设备失败' }
        }
    }

    // 删除设备
    const deleteEquipmentAction = async (equipmentId) => {
        try {
            const response = await deleteEquipment(equipmentId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                equipmentList.value = equipmentList.value.filter(item => item.id !== equipmentId)
                
                // 如果删除的是当前查看的设备，清空
                if (currentEquipment.value && currentEquipment.value.id === equipmentId) {
                    currentEquipment.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除设备失败' }
        } catch (error) {
            console.error('删除设备失败:', error.message)
            return { success: false, message: error.message || '删除设备失败' }
        }
    }

    // 获取设备统计
    const fetchStatistics = async () => {
        try {
            const response = await getEquipmentStatistics()
            
            if (response.data) {
                statistics.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取统计数据失败' }
        } catch (error) {
            console.error('获取统计数据失败:', error.message)
            return { success: false, message: error.message || '获取统计数据失败' }
        }
    }

    // 控制设备状态
    const controlStatus = async (equipmentId, action) => {
        try {
            const response = await controlEquipmentStatus(equipmentId, action)
            
            if (response.code === 200) {
                // 刷新设备信息
                await fetchEquipmentDetail(equipmentId)
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '设备控制失败' }
        } catch (error) {
            console.error('设备控制失败:', error.message)
            return { success: false, message: error.message || '设备控制失败' }
        }
    }

    // 清空数据
    const clearData = () => {
        equipmentList.value = []
        currentEquipment.value = null
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
        equipmentList,
        currentEquipment,
        statistics,
        isLoading,
        pagination,
        
        // 动作
        fetchEquipmentList,
        fetchEquipmentDetail,
        createEquipmentAction,
        updateEquipmentAction,
        deleteEquipmentAction,
        fetchStatistics,
        controlStatus,
        clearData
    }
})