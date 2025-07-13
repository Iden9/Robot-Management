<template>
  <div class="account-management">
    <div class="top-section">
      <div class="action-bar">
        <ActionButton 
          text="添加账号" 
          :icon="PlusIcon" 
          primary 
          @click="handleAddAccount"
        />
      </div>
      
      <SearchBar 
        @search="handleSearch" 
        @filter="handleFilter"
      />
    </div>

    <div class="account-grid">
      <AccountCard 
        v-for="account in filteredAccounts" 
        :key="account.id" 
        :account="account"
        @edit="handleEdit"
        @reset-password="handleResetPassword"
        @delete="handleDelete"
      />
      
      <div v-if="filteredAccounts.length === 0" class="no-results">
        <p>没有找到匹配的账号</p>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <UserEditModal 
      :show="showEditModal"
      :user="selectedUser"
      @close="closeEditModal"
      @save="handleSaveUser"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AccountCard from '@/components/account/AccountCard.vue'
import ActionButton from '@/components/account/ActionButton.vue'
import SearchBar from '@/components/account/SearchBar.vue'
import UserEditModal from '@/components/account/UserEditModal.vue'
import PlusIcon from '@/components/account/icons/PlusIcon.vue'

// Stores
import { useUsersStore } from '@/stores/users'
import { success, error, confirm } from '@/utils/alert'

// 初始化stores
const usersStore = useUsersStore()

// 搜索和过滤状态
const searchQuery = ref('')
const filterValue = ref('all')
const isLoading = ref(false)

// 编辑弹窗状态
const showEditModal = ref(false)
const selectedUser = ref(null)

// 计算属性
const accountList = computed(() => usersStore.userList)
const currentUser = computed(() => usersStore.currentUser)
const pagination = computed(() => usersStore.pagination)

// 过滤后的账号列表
const filteredAccounts = computed(() => {
  return accountList.value.filter(account => {
    // 先按角色过滤
    if (filterValue.value !== 'all' && account.role !== filterValue.value) {
      return false
    }
    
    // 再按搜索词过滤
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      return account.username.toLowerCase().includes(query) || 
             (account.real_name && account.real_name.toLowerCase().includes(query)) ||
             (account.phone && account.phone.toLowerCase().includes(query))
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

// 处理函数
const handleAddAccount = () => {
  // TODO: 打开添加账号对话框
  console.log('添加账号')
}

const handleEdit = async (account) => {
  try {
    // 获取账号详情
    const result = await usersStore.fetchUserDetail(account.id)
    
    if (result.success) {
      selectedUser.value = result.data
      showEditModal.value = true
    } else {
      console.error('获取账号详情失败:', result.message)
    }
  } catch (error) {
    console.error('编辑账号失败:', error)
  }
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false
  selectedUser.value = null
}

// 保存用户编辑
const handleSaveUser = async ({ userId, data }) => {
  try {
    const result = await usersStore.updateUserAction(userId, data)
    
    if (result.success) {
      console.log('用户更新成功')
      closeEditModal()
      // 刷新用户列表
      await loadAccountList()
    } else {
      console.error('用户更新失败:', result.message)
    }
  } catch (error) {
    console.error('保存用户失败:', error)
  }
}

const handleResetPassword = async (account) => {
  try {
    // 先确认是否要重置密码
    const confirmed = await confirm(`确定要重置用户 "${account.username}" 的密码吗？\n\n重置后将生成新的临时密码。`)
    if (!confirmed) return
    
    // 生成新密码
    const newPassword = Math.random().toString(36).slice(-8) + Math.random().toString(36).slice(-3).toUpperCase()
    
    const result = await usersStore.resetUserPasswordAction(account.id, {
      new_password: newPassword
    })
    
    if (result.success) {
      // 显示新密码给用户
      await success(`密码重置成功！\n\n用户：${account.username}\n新密码：${newPassword}\n\n请将新密码告知用户，并提醒用户及时修改密码。`, {
        title: '密码重置成功',
        confirmText: '已复制密码'
      })
      
      // 复制新密码到剪贴板（如果浏览器支持）
      if (navigator.clipboard) {
        try {
          await navigator.clipboard.writeText(newPassword)
        } catch (clipboardError) {
          console.log('无法自动复制到剪贴板:', clipboardError)
        }
      }
      
      console.log('密码重置成功，新密码:', newPassword)
    } else {
      await error(`密码重置失败: ${result.message || '未知错误'}`)
      console.error('密码重置失败:', result.message)
    }
  } catch (error) {
    await error(`重置密码失败: ${error.message || '未知错误'}`)
    console.error('重置密码失败:', error)
  }
}

const handleDelete = async (account) => {
  try {
    const confirmed = await confirm(`确定要删除用户 "${account.username}" 吗？`)
    
    if (confirmed) {
      const result = await usersStore.deleteUserAction(account.id)
      
      if (result.success) {
        await success('账号删除成功')
        console.log('账号删除成功')
      } else {
        await error(`账号删除失败: ${result.message}`)
        console.error('账号删除失败:', result.message)
      }
    }
  } catch (error) {
    await error(`删除账号失败: ${error.message || '未知错误'}`)
    console.error('删除账号失败:', error)
  }
}

// 创建新账号
const createAccount = async (accountData) => {
  try {
    const result = await usersStore.createUserAction(accountData)
    
    if (result.success) {
      console.log('账号创建成功:', result.data)
      return { success: true, data: result.data }
    } else {
      console.error('账号创建失败:', result.message)
      return { success: false, message: result.message }
    }
  } catch (error) {
    console.error('创建账号失败:', error)
    return { success: false, message: error.message }
  }
}

// 更新账号信息
const updateAccount = async (accountId, accountData) => {
  try {
    const result = await usersStore.updateUserAction(accountId, accountData)
    
    if (result.success) {
      console.log('账号更新成功:', result.data)
      return { success: true, data: result.data }
    } else {
      console.error('账号更新失败:', result.message)
      return { success: false, message: result.message }
    }
  } catch (error) {
    console.error('更新账号失败:', error)
    return { success: false, message: error.message }
  }
}

// 切换账号状态
const toggleAccountStatus = async (account) => {
  try {
    const newStatus = account.status === 'active' ? 'inactive' : 'active'
    const result = await usersStore.toggleUserStatusAction(account.id, newStatus)
    
    if (result.success) {
      console.log('账号状态更新成功')
    } else {
      console.error('账号状态更新失败:', result.message)
    }
  } catch (error) {
    console.error('切换账号状态失败:', error)
  }
}

// 导出账号列表
const exportAccounts = async () => {
  try {
    const result = await usersStore.exportUserListAction()
    
    if (result.success) {
      console.log('账号列表导出成功')
    } else {
      console.error('账号列表导出失败:', result.message)
    }
  } catch (error) {
    console.error('导出账号列表失败:', error)
  }
}

// 加载账号列表
const loadAccountList = async () => {
  try {
    isLoading.value = true
    await usersStore.fetchUserList()
  } catch (error) {
    console.error('加载账号列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadAccountList()
})
</script>

<style scoped>
/* .account-management {
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

.account-grid {
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

@media (max-width: 768px) {
  .account-grid {
    grid-template-columns: 1fr;
  }
}
</style> 