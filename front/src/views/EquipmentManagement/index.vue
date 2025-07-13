<template>
  <div class="equipment-management">
    <div class="top-section">
      <div class="action-bar">
        <ActionButton 
          text="添加设备" 
          :icon="PlusIcon" 
          primary 
          @click="handleAddEquipment"
        />
        <ActionButton 
          text="批量导入" 
          :icon="UploadIcon" 
          @click="handleBatchImport"
        />
        <ActionButton 
          text="批量部署" 
          :icon="RefreshIcon" 
          @click="handleBatchDeploy"
        />
        <ActionButton 
          text="导出数据" 
          :icon="ExportIcon" 
          @click="handleExportData"
        />
      </div>
      
      <SearchBar 
        @search="handleSearch" 
        @filter="handleFilter"
      />
    </div>

    <div class="equipment-grid">
      <EquipmentCard 
        v-for="equipment in filteredEquipment" 
        :key="equipment.id" 
        :equipment="equipment"
        @detail="handleDetail"
        @setting="handleSetting"
        @control="handleControl"
        @restart="handleRestart"
        @diagnose="handleDiagnose"
        @delete="handleDelete"
      />
      
      <div v-if="filteredEquipment.length === 0" class="no-results">
        <p>没有找到匹配的设备</p>
      </div>
    </div>

    <!-- 设备表单弹窗 -->
    <div class="modal" v-if="showForm">
      <div class="modal-overlay" @click="handleCancelForm"></div>
      <div class="modal-content">
        <EquipmentForm
          :title="formTitle"
          :equipment="currentEquipment"
          @submit="handleSubmitEquipment"
          @cancel="handleCancelForm"
        />
      </div>
    </div>

    <!-- 设备详情模态框 -->
    <EquipmentDetailModal
      :show="showDetailModal"
      :equipment="detailEquipment"
      :loading="detailLoading"
      @close="handleCloseDetail"
      @edit="handleEditFromDetail"
    />

    <!-- 批量导入模态框 -->
    <BatchImportModal
      :show="showBatchImportModal"
      @close="handleBatchImportClose"
      @success="handleBatchImportSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EquipmentCard from '@/components/equipment/EquipmentCard.vue'
import ActionButton from '@/components/equipment/ActionButton.vue'
import SearchBar from '@/components/equipment/SearchBar.vue'
import EquipmentForm from '@/components/equipment/EquipmentForm.vue'
import EquipmentDetailModal from '@/components/equipment/EquipmentDetailModal.vue'
import BatchImportModal from '@/components/equipment/BatchImportModal.vue'
import PlusIcon from '@/components/equipment/icons/PlusIcon.vue'
import UploadIcon from '@/components/equipment/icons/UploadIcon.vue'
import RefreshIcon from '@/components/equipment/icons/RefreshIcon.vue'
import ExportIcon from '@/components/equipment/icons/ExportIcon.vue'
import { useEquipmentStore } from '@/stores/equipment'
import { success, error, confirm } from '@/utils/alert'
import { exportEquipmentList } from '@/api/equipment'

// Store
const equipmentStore = useEquipmentStore()

// 搜索和过滤状态
const searchQuery = ref('')
const filterValue = ref('all')
const isLoading = ref(false)

// 计算属性
const equipmentList = computed(() => equipmentStore.equipmentList)

// 过滤后的设备列表
const filteredEquipment = computed(() => {
  return equipmentList.value.filter(equipment => {
    // 先按状态过滤
    if (filterValue.value !== 'all') {
      if (filterValue.value === 'online' && (equipment.is_offline || equipment.has_error)) return false
      if (filterValue.value === 'offline' && !equipment.is_offline) return false
      if (filterValue.value === 'error' && !equipment.has_error) return false
    }
    
    // 再按搜索词过滤
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      return equipment.id.toLowerCase().includes(query) || 
             equipment.location.toLowerCase().includes(query) || 
             (equipment.ip_address && equipment.ip_address.toLowerCase().includes(query))
    }
    
    return true
  })
})

// 表单相关状态
const showForm = ref(false)
const formTitle = ref('添加设备')
const currentEquipment = ref(null)

// 详情模态框相关状态
const showDetailModal = ref(false)
const detailEquipment = ref(null)
const detailLoading = ref(false)

// 批量导入模态框状态
const showBatchImportModal = ref(false)

// 处理搜索
const handleSearch = (query) => {
  searchQuery.value = query
}

// 处理过滤
const handleFilter = (filter) => {
  filterValue.value = filter
}

// 处理函数
const handleAddEquipment = () => {
  formTitle.value = '添加设备'
  currentEquipment.value = null
  showForm.value = true
}

const handleSubmitEquipment = async (equipment) => {
  try {
    if (currentEquipment.value) {
      // 更新设备
      await equipmentStore.updateEquipmentAction(currentEquipment.value.id, equipment)
    } else {
      // 创建新设备
      await equipmentStore.createEquipmentAction(equipment)
    }
    showForm.value = false
  } catch (error) {
    console.error('设备操作失败:', error)
  }
}

const handleCancelForm = () => {
  showForm.value = false
}

const handleBatchImport = () => {
  showBatchImportModal.value = true
}

const handleBatchDeploy = () => {
  // TODO: 实现批量部署功能
  console.log('批量部署')
}

const handleExportData = async () => {
  try {
    isLoading.value = true
    
    // 获取当前过滤条件
    const params = {
      search: searchQuery.value || undefined,
      status: filterValue.value !== 'all' ? filterValue.value : undefined
    }
    
    const response = await exportEquipmentList(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    link.setAttribute('download', `设备列表_${timestamp}.xlsx`)
    
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    await success('设备数据导出成功')
  } catch (err) {
    console.error('导出失败:', err)
    await error(`数据导出失败: ${err.response?.data?.message || err.message || '未知错误'}`)
  } finally {
    isLoading.value = false
  }
}

const handleDetail = async (equipment) => {
  try {
    detailLoading.value = true
    showDetailModal.value = true
    
    const result = await equipmentStore.fetchEquipmentDetail(equipment.id)
    if (result.success) {
      detailEquipment.value = equipmentStore.currentEquipment
    } else {
      await error(`获取设备详情失败: ${result.message}`)
    }
  } catch (err) {
    console.error('获取设备详情失败:', err)
    await error(`获取设备详情失败: ${err.message || '未知错误'}`)
  } finally {
    detailLoading.value = false
  }
}

const handleSetting = (equipment) => {
  // 设置设备配置
  formTitle.value = '设备设置'
  currentEquipment.value = equipment
  showForm.value = true
}

const handleControl = async (equipment) => {
  try {
    const isOnline = !equipment.is_offline && equipment.status === 'online'
    const action = isOnline ? 'stop' : 'start'
    const actionText = isOnline ? '停止' : '启动'
    
    const confirmed = await confirm(`确定要${actionText}设备 ${equipment.id} 吗？`)
    if (!confirmed) return
    
    await equipmentStore.controlStatus(equipment.id, action)
    
    // 显示成功消息
    await success(`设备${actionText}成功`)
    
    // 重新加载设备列表
    await loadEquipmentList()
  } catch (error) {
    console.error('设备控制失败:', error)
    await error(`设备控制失败: ${error.message || '未知错误'}`)
  }
}

const handleRestart = async (equipment) => {
  try {
    const confirmed = await confirm(`确定要重启设备 ${equipment.id} 吗？重启过程可能需要几分钟时间。`)
    if (!confirmed) return
    
    await equipmentStore.controlStatus(equipment.id, 'restart')
    
    await success('设备重启成功，请稍等片刻')
    
    // 重新加载设备列表
    await loadEquipmentList()
  } catch (error) {
    console.error('设备重启失败:', error)
    await error(`设备重启失败: ${error.message || '未知错误'}`)
  }
}

const handleDiagnose = async (equipment) => {
  try {
    const confirmed = await confirm(`确定要诊断设备 ${equipment.id} 吗？诊断过程可能需要一些时间。`)
    if (!confirmed) return
    
    // TODO: 实现设备诊断功能
    await success('设备诊断功能正在开发中')
    
    console.log('诊断设备', equipment)
  } catch (error) {
    console.error('设备诊断失败:', error)
    await error(`设备诊断失败: ${error.message || '未知错误'}`)
  }
}

const handleDelete = async (equipment) => {
  try {
    const confirmed = await confirm(`确定要删除设备 "${equipment.id}" 吗？\n\n设备: ${equipment.id}\n位置: ${equipment.location}\nIP地址: ${equipment.ip_address || 'N/A'}\n\n删除后无法恢复，请谨慎操作！`)
    if (!confirmed) return
    
    isLoading.value = true
    
    const result = await equipmentStore.deleteEquipmentAction(equipment.id)
    
    if (result.success) {
      await success('设备删除成功')
      // 重新加载设备列表
      await loadEquipmentList()
    } else {
      await error(`设备删除失败: ${result.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('设备删除失败:', error)
    await error(`设备删除失败: ${error.message || '未知错误'}`)
  } finally {
    isLoading.value = false
  }
}

// 处理详情模态框关闭
const handleCloseDetail = () => {
  showDetailModal.value = false
  detailEquipment.value = null
}

// 从详情模态框进入编辑
const handleEditFromDetail = (equipment) => {
  // 关闭详情模态框
  handleCloseDetail()
  // 打开编辑表单
  formTitle.value = '编辑设备'
  currentEquipment.value = equipment
  showForm.value = true
}

// 处理批量导入成功
const handleBatchImportSuccess = async () => {
  showBatchImportModal.value = false
  // 重新加载设备列表
  await loadEquipmentList()
  await success('设备批量导入完成')
}

// 处理批量导入关闭
const handleBatchImportClose = () => {
  showBatchImportModal.value = false
}

// 加载设备列表
const loadEquipmentList = async () => {
  try {
    isLoading.value = true
    await equipmentStore.fetchEquipmentList()
  } catch (error) {
    console.error('加载设备列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadEquipmentList()
})
</script>

<style scoped>
/* .equipment-management {
  padding: 20px;
} */

.top-section {
  margin-bottom: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  z-index: 101;
}

@media (max-width: 768px) {
  .equipment-grid {
    grid-template-columns: 1fr;
  }
}
</style> 