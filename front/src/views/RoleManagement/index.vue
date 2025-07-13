<template>
  <div class="role-management">
    <div class="top-section">
      <div class="action-bar">
        <ActionButton 
          text="新增角色" 
          :icon="PlusIcon" 
          primary 
          @click="handleAddRole"
        />
        <ActionButton 
          text="批量删除" 
          :icon="TrashIcon" 
          danger
          :disabled="selectedRoles.length === 0"
          @click="handleBatchDelete"
        />
      </div>
      
      <RoleSearchBar 
        @search="handleSearch" 
        @filter="handleFilter"
      />
    </div>

    <div class="roles-grid">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <div class="loading-text">加载中...</div>
        </div>
      </div>
      
      <RoleCard 
        v-for="role in filteredRoles" 
        :key="role.id" 
        :role="role"
        :selected="selectedRoles.includes(role.id)"
        @select="handleSelectRole"
        @edit="handleEdit"
        @permissions="handlePermissions"
        @delete="handleDelete"
      />
      
      <div v-if="filteredRoles.length === 0 && !loading" class="no-results">
        <p>没有找到匹配的角色</p>
      </div>
    </div>

    <!-- 角色编辑弹窗 -->
    <RoleEditModal 
      :show="showEditModal"
      :role="selectedRole"
      @close="closeEditModal"
      @save="handleSaveRole"
    />

    <!-- 权限分配弹窗 -->
    <PermissionModal
      :show="showPermissionModal"
      :role="selectedRole"
      @close="closePermissionModal"
      @save="handleSavePermissions"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ActionButton from '@/components/account/ActionButton.vue'
import RoleCard from './components/RoleCard.vue'
import RoleSearchBar from './components/RoleSearchBar.vue'
import RoleEditModal from './components/RoleEditModal.vue'
import PermissionModal from './components/PermissionModal.vue'
import PlusIcon from '@/components/account/icons/PlusIcon.vue'
import TrashIcon from '@/components/account/icons/TrashIcon.vue'

// Utils
import { success, error, confirm } from '@/utils/alert'

// API
import { 
  getRoleList,
  deleteRole,
  createRole,
  updateRole,
  assignRolePermissions,
  batchRoleOperation
} from '@/api/role'

// 响应式数据
const loading = ref(false)
const roles = ref([])
const selectedRoles = ref([])

// 搜索和过滤状态
const searchQuery = ref('')
const filterValue = ref('all')

// 编辑弹窗状态
const showEditModal = ref(false)
const showPermissionModal = ref(false)
const selectedRole = ref(null)

// 计算属性
const filteredRoles = computed(() => {
  return roles.value.filter(role => {
    // 先按状态过滤
    if (filterValue.value === 'active' && !role.status) return false
    if (filterValue.value === 'inactive' && role.status) return false
    if (filterValue.value === 'system' && !role.is_system) return false
    if (filterValue.value === 'custom' && role.is_system) return false
    
    // 再按搜索词过滤
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      return role.name.toLowerCase().includes(query) || 
             role.code.toLowerCase().includes(query) ||
             (role.description && role.description.toLowerCase().includes(query))
    }
    
    return true
  })
})

// 处理搜索
const handleSearch = (query) => {
  searchQuery.value = query
}

// 处理过滤
const handleFilter = (filter) => {
  filterValue.value = filter
}

// 处理角色选择
const handleSelectRole = (roleId, selected) => {
  if (selected) {
    selectedRoles.value.push(roleId)
  } else {
    const index = selectedRoles.value.indexOf(roleId)
    if (index > -1) {
      selectedRoles.value.splice(index, 1)
    }
  }
}

// 处理函数
const handleAddRole = () => {
  selectedRole.value = null
  showEditModal.value = true
}

const handleEdit = (role) => {
  selectedRole.value = { ...role }
  showEditModal.value = true
}

const handlePermissions = (role) => {
  selectedRole.value = role
  showPermissionModal.value = true
}

const handleDelete = async (role) => {
  try {
    const confirmed = await confirm(`确定要删除角色 "${role.name}" 吗？`)
    
    if (confirmed) {
      const response = await deleteRole(role.id)
      if (response.code === 200) {
        await success('角色删除成功')
        await loadRoles()
      } else {
        await error(`删除失败: ${response.message}`)
      }
    }
  } catch (err) {
    if (err !== 'cancel') {
      await error(`删除角色失败: ${err.message || '未知错误'}`)
    }
  }
}

const handleBatchDelete = async () => {
  try {
    const confirmed = await confirm(`确定要删除选中的 ${selectedRoles.value.length} 个角色吗？`)
    
    if (confirmed) {
      const response = await batchRoleOperation(selectedRoles.value, 'delete')
      
      if (response.code === 200) {
        await success('批量删除成功')
        selectedRoles.value = []
        await loadRoles()
      } else {
        await error(`批量删除失败: ${response.message}`)
      }
    }
  } catch (err) {
    if (err !== 'cancel') {
      await error(`批量删除失败: ${err.message || '未知错误'}`)
    }
  }
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false
  selectedRole.value = null
}

// 关闭权限弹窗
const closePermissionModal = () => {
  showPermissionModal.value = false
  selectedRole.value = null
}

// 保存角色
const handleSaveRole = async (roleData) => {
  try {
    let response
    if (selectedRole.value?.id) {
      // 更新角色
      response = await updateRole(selectedRole.value.id, roleData)
    } else {
      // 创建角色
      response = await createRole(roleData)
    }
    
    if (response.code === 200) {
      await success(selectedRole.value?.id ? '角色更新成功' : '角色创建成功')
      closeEditModal()
      await loadRoles()
    } else {
      await error(`操作失败: ${response.message}`)
    }
  } catch (err) {
    await error(`操作失败: ${err.message || '未知错误'}`)
  }
}

// 保存权限
const handleSavePermissions = async (permissionIds) => {
  try {
    const response = await assignRolePermissions(selectedRole.value.id, permissionIds)
    
    if (response.code === 200) {
      await success('权限分配成功')
      closePermissionModal()
      await loadRoles()
    } else {
      await error(`权限分配失败: ${response.message}`)
    }
  } catch (err) {
    await error(`权限分配失败: ${err.message || '未知错误'}`)
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    loading.value = true
    const response = await getRoleList()
    if (response.code === 200) {
      roles.value = response.data.roles
    }
  } catch (err) {
    console.error('加载角色列表失败:', err)
    await error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.top-section {
  margin-bottom: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.loading {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0071e4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .roles-grid {
    grid-template-columns: 1fr;
  }
}
</style>