<template>
  <div class="dashboard">
    <div class="stat-cards">
      <!-- 设备总数卡片 -->
      <StatCard 
        title="设备总数"
        :value="overview?.summary?.total_equipment || 0"
        :status="getEquipmentStatus()"
        statusType="success"
        :statusIcon="ArrowUpIcon"
        :icon="RobotIcon"
        iconBgColor="blue-bg"
      />
      
      <!-- 在线设备卡片 -->
      <StatCard 
        title="在线设备"
        :value="overview?.equipment_status?.online || 0"
        :status="getOnlineStatus()"
        statusType="success"
        :statusIcon="CheckIcon"
        :icon="WifiIcon"
        iconBgColor="blue-bg"
      />
      
      <!-- 今日操作卡片 -->
      <StatCard 
        title="今日操作"
        :value="overview?.today_activity?.total_operations || 0"
        :status="getActivityStatus()"
        statusType="success"
        :statusIcon="ArrowDownIcon"
        :icon="AlertIcon"
        iconBgColor="blue-bg"
      />
      
      <!-- 用户总数卡片 -->
      <StatCard 
        title="用户总数"
        :value="overview?.summary?.total_users || 0"
        :status="getUserStatus()"
        statusType="info"
        :statusIcon="InfoIcon"
        :icon="UserIcon"
        iconBgColor="blue-bg"
      />
    </div>
    
    <!-- 工控机状态监控 -->
    <MonitoringPanel />
    
    <!-- 快捷操作栏 -->
    <ActionTab title="快捷操作">
      <ActionButton 
        text="添加新设备"
        :icon="PlusIcon"
        type="primary"
        @click="handleAddDevice"
      />
      <ActionButton 
        text="批量部署"
        :icon="RefreshIcon"
        :loading="isLoading"
        @click="handleBatchDeploy"
      />
      <ActionButton 
        text="导出数据"
        :icon="ExportIcon" 
        :loading="isLoading"
        @click="handleExportData"
      />
    </ActionTab>
    
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
  </div>
</template>

<script setup>
import StatCard from '@/components/dashboard/StatCard.vue'
import ActionTab from '@/components/dashboard/ActionTab.vue'
import ActionButton from '@/components/dashboard/ActionButton.vue'
import EquipmentForm from '@/components/equipment/EquipmentForm.vue'
import MonitoringPanel from '@/components/dashboard/MonitoringPanel.vue'

// 引入图标组件
import RobotIcon from '@/components/dashboard/icons/RobotIcon.vue'
import WifiIcon from '@/components/dashboard/icons/WifiIcon.vue'
import AlertIcon from '@/components/dashboard/icons/AlertIcon.vue'
import UserIcon from '@/components/dashboard/icons/UserIcon.vue'
import ArrowUpIcon from '@/components/dashboard/icons/ArrowUpIcon.vue'
import ArrowDownIcon from '@/components/dashboard/icons/ArrowDownIcon.vue'
import CheckIcon from '@/components/dashboard/icons/CheckIcon.vue'
import InfoIcon from '@/components/dashboard/icons/InfoIcon.vue'
import PlusIcon from '@/components/dashboard/icons/PlusIcon.vue'
import RefreshIcon from '@/components/dashboard/icons/RefreshIcon.vue'
import ExportIcon from '@/components/dashboard/icons/ExportIcon.vue'

import { ref, onMounted, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { message } from '@/utils/message'

// Stores
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()

// 表单相关状态
const showForm = ref(false)
const formTitle = ref('添加设备')
const currentEquipment = ref(null)
const isLoading = ref(false)

// 计算属性
const overview = computed(() => dashboardStore.overview)

// 状态描述函数
const getEquipmentStatus = () => {
  const total = overview.value?.summary?.total_equipment || 0
  return total > 0 ? `${total} 台设备在线` : '暂无设备'
}

const getOnlineStatus = () => {
  const online = overview.value?.equipment_status?.online || 0
  const total = overview.value?.summary?.total_equipment || 0
  if (total === 0) return '暂无设备'
  const percentage = ((online / total) * 100).toFixed(1)
  return `${percentage}% 正常运行`
}

const getActivityStatus = () => {
  const operations = overview.value?.today_activity?.total_operations || 0
  return operations > 0 ? '系统运行正常' : '今日暂无操作'
}

const getUserStatus = () => {
  const online = overview.value?.summary?.online_users || 0
  return online > 0 ? `${online} 人在线` : '暂无在线用户'
}

// 按钮的点击处理函数
const handleAddDevice = () => {
  formTitle.value = '添加设备'
  currentEquipment.value = null
  showForm.value = true
}

const handleSubmitEquipment = async (equipment) => {
  try {
    isLoading.value = true
    
    let result
    if (currentEquipment.value) {
      // 更新设备
      result = await equipmentStore.updateEquipmentAction(currentEquipment.value.id, equipment)
    } else {
      // 添加新设备
      result = await equipmentStore.createEquipmentAction(equipment)
    }
    
    if (result.success) {
      const action = currentEquipment.value ? '更新' : '添加'
      message.success(`设备${action}成功！`)
      showForm.value = false
      // 刷新仪表板数据
      await refreshData()
    } else {
      message.error(result.message || '设备操作失败')
    }
  } catch (error) {
    console.error('设备操作错误:', error)
    message.error('设备操作失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const handleCancelForm = () => {
  showForm.value = false
}

const handleBatchDeploy = async () => {
  try {
    isLoading.value = true
    console.log('批量部署')
    
    // 获取所有设备列表
    const equipmentResult = await equipmentStore.fetchEquipmentList()
    
    if (equipmentResult.success && equipmentStore.equipmentList.length > 0) {
      // 模拟批量部署操作
      const deployPromises = equipmentStore.equipmentList.map(equipment => 
        equipmentStore.controlStatus(equipment.id, 'start')
      )
      
      const results = await Promise.allSettled(deployPromises)
      const successCount = results.filter(r => r.status === 'fulfilled').length
      
      if (successCount > 0) {
        message.success(`批量部署完成，成功部署 ${successCount} 台设备`)
      } else {
        message.warning('批量部署失败，请检查设备状态')
      }
      
      // 刷新仪表板数据
      await refreshData()
    } else {
      message.info('暂无设备可部署')
    }
  } catch (error) {
    console.error('批量部署失败:', error)
    message.error('批量部署失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const handleExportData = async () => {
  try {
    isLoading.value = true
    console.log('导出数据')
    
    // 导出设备统计数据
    const result = await equipmentStore.fetchStatistics()
    
    if (result.success) {
      // 模拟导出操作（实际中可以调用导出API）
      const exportData = {
        overview: overview.value,
        statistics: result.data,
        exportTime: new Date().toISOString()
      }
      
      // 创建下载链接
      const dataStr = JSON.stringify(exportData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `dashboard_data_${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      message.success('数据导出成功！')
    } else {
      message.error(result.message || '获取导出数据失败')
    }
  } catch (error) {
    console.error('导出数据失败:', error)
    message.error('导出数据失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  try {
    isLoading.value = true
    await dashboardStore.fetchOverview()
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 初始化数据加载
const initData = async () => {
  await refreshData()
}

// 组件挂载时加载数据
onMounted(() => {
  initData()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }
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
</style> 