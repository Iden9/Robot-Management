<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h2>编辑用户信息</h2>
        <button class="close-btn" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- 基本信息 -->
          <div class="form-section">
            <h3>基本信息</h3>
            
            <div class="form-group">
              <label>用户名</label>
              <input 
                type="text" 
                v-model="formData.username" 
                readonly
                class="readonly-input"
              />
              <span class="form-help">用户名不可修改</span>
            </div>

            <div class="form-group">
              <label>真实姓名</label>
              <input 
                type="text" 
                v-model="formData.real_name" 
                placeholder="请输入真实姓名"
                required
              />
            </div>

            <div class="form-group">
              <label>邮箱地址</label>
              <input 
                type="email" 
                v-model="formData.email" 
                placeholder="请输入邮箱地址"
              />
            </div>

            <div class="form-group">
              <label>手机号码</label>
              <input 
                type="tel" 
                v-model="formData.phone" 
                placeholder="请输入手机号码"
              />
            </div>
          </div>

          <!-- 权限设置 -->
          <div class="form-section">
            <h3>权限设置</h3>
            
            <div class="form-group">
              <label>用户角色</label>
              <div v-if="loadingRoles" class="loading-roles">
                加载角色列表中...
              </div>
              <div v-else class="role-select">
                <label 
                  v-for="role in availableRoles" 
                  :key="role.id"
                  class="radio-option" 
                  :class="{ 
                    disabled: !canChangeRole || !canAssignRole(role)
                  }"
                >
                  <input 
                    type="radio" 
                    :value="role.id" 
                    v-model="formData.role_id"
                    :disabled="!canChangeRole || !canAssignRole(role)"
                  />
                  <span class="radio-label">
                    <span class="role-name">{{ role.name }}</span>
                    <span class="role-desc">{{ role.description || '暂无描述' }}</span>
                    <span v-if="role.is_system" class="role-badge">系统角色</span>
                  </span>
                </label>
              </div>
              <span v-if="isCurrentUser" class="form-help warning">
                不能修改自己的角色
              </span>
              <span v-else-if="!canChangeRole" class="form-help warning">
                您没有权限修改此用户的角色
              </span>
            </div>
          </div>

          <!-- 状态设置 -->
          <div class="form-section">
            <h3>状态设置</h3>
            
            <div class="form-group">
              <label>账户状态</label>
              <div class="status-toggle">
                <button 
                  type="button"
                  class="status-button"
                  :class="{ 
                    'status-enabled': formData.status, 
                    'status-disabled': !formData.status,
                    'disabled': isCurrentUser
                  }"
                  @click="toggleStatus"
                  :disabled="isCurrentUser"
                >
                  <span class="status-icon">
                    {{ formData.status ? '✓' : '✗' }}
                  </span>
                  <span class="status-text">
                    {{ formData.status ? '已启用' : '已禁用' }}
                  </span>
                </button>
              </div>
              <span v-if="isCurrentUser" class="form-help warning">
                不能禁用自己的账户
              </span>
              <span v-else class="form-help">
                禁用后用户将无法登录系统
              </span>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="form-section">
            <h3>统计信息</h3>
            
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">创建时间</span>
                <span class="stat-value">{{ formatDateTime(user?.created_at) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">最后登录</span>
                <span class="stat-value">{{ formatDateTime(user?.last_login) || '从未登录' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">登录次数</span>
                <span class="stat-value">{{ user?.login_count || 0 }}次</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">在线状态</span>
                <span class="stat-value" :class="user?.is_online ? 'online' : 'offline'">
                  {{ user?.is_online ? '在线' : '离线' }}
                </span>
              </div>
            </div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-secondary" @click="closeModal" :disabled="isLoading">
          取消
        </button>
        <button type="button" class="btn-primary" @click="handleSubmit" :disabled="isLoading">
          {{ isLoading ? '保存中...' : '保存更改' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getAllActiveRoles } from '@/api/role'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const authStore = useAuthStore()
const isLoading = ref(false)
const loadingRoles = ref(false)
const availableRoles = ref([])

// 表单数据
const formData = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role_id: null,
  status: true
})

// 计算属性
const isCurrentUser = computed(() => {
  return props.user?.id === authStore.userInfo?.id
})

const canChangeRole = computed(() => {
  const currentUserRole = authStore.userInfo?.role
  const targetUserRole = props.user?.role
  
  // 只有管理员可以修改角色
  if (currentUserRole !== 'admin') return false
  
  // 管理员不能修改其他管理员的角色（除了自己，但自己的角色也不能改）
  if (targetUserRole === 'admin' && !isCurrentUser.value) return false
  
  return true
})

// 监听user变化，初始化表单
watch(() => props.user, (newUser) => {
  if (newUser) {
    formData.username = newUser.username || ''
    formData.real_name = newUser.real_name || ''
    formData.email = newUser.email || ''
    formData.phone = newUser.phone || ''
    
    // 优先使用 role_id，如果没有则根据 role 查找对应的 role_id
    if (newUser.role_id) {
      formData.role_id = newUser.role_id
    } else if (newUser.role && availableRoles.value.length > 0) {
      const matchedRole = availableRoles.value.find(role => role.code === newUser.role)
      formData.role_id = matchedRole ? matchedRole.id : null
    } else {
      formData.role_id = null
    }
    
    formData.status = newUser.status !== false
  }
}, { immediate: true })

// 格式化时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

// 切换状态
const toggleStatus = () => {
  if (!isCurrentUser.value) {
    formData.status = !formData.status
  }
}

// 关闭弹窗
const closeModal = () => {
  if (!isLoading.value) {
    emit('close')
  }
}

// 加载可用角色
const loadAvailableRoles = async () => {
  try {
    loadingRoles.value = true
    const response = await getAllActiveRoles()
    if (response.code === 200) {
      // 过滤出启用的角色
      availableRoles.value = response.data.roles.filter(role => role.status === true)
    }
  } catch (err) {
    console.error('加载角色列表失败:', err)
  } finally {
    loadingRoles.value = false
  }
}

// 检查是否可以分配某个角色
const canAssignRole = (role) => {
  const currentUserRole = authStore.userInfo?.role
  
  // 只有管理员可以分配角色
  if (currentUserRole !== 'admin') return false
  
  // 管理员不能将其他用户设置为管理员（除了自己，但自己的角色也不能改）
  if (role.code === 'admin' && !isCurrentUser.value) return false
  
  return true
}

// 提交表单
const handleSubmit = async () => {
  if (isLoading.value) return

  try {
    isLoading.value = true

    // 构建更新数据
    const updateData = {
      real_name: formData.real_name,
      email: formData.email,
      phone: formData.phone,
      status: formData.status
    }

    // 只有在可以修改角色且不是当前用户时才包含角色
    if (canChangeRole.value && !isCurrentUser.value) {
      updateData.role_id = formData.role_id
    }

    // 发送更新请求
    emit('save', {
      userId: props.user.id,
      data: updateData
    })

  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 监听弹窗显示状态，加载角色数据
watch(() => props.show, (show) => {
  if (show) {
    loadAvailableRoles()
  }
})

// 监听角色列表变化，重新匹配用户角色
watch(() => availableRoles.value, (newRoles) => {
  if (newRoles.length > 0 && props.user && !formData.role_id && props.user.role) {
    const matchedRole = newRoles.find(role => role.code === props.user.role)
    if (matchedRole) {
      formData.role_id = matchedRole.id
    }
  }
})

// 组件挂载时如果弹窗已显示，则加载数据
onMounted(() => {
  if (props.show) {
    loadAvailableRoles()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #3b82f6;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="tel"] {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.readonly-input {
  background-color: #f9fafb !important;
  cursor: not-allowed;
}

.form-help {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-help.warning {
  color: #f59e0b;
}

/* 角色选择 */
.role-select {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-option:hover:not(.disabled) {
  border-color: #3b82f6;
  background: #f8faff;
}

.radio-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.radio-option input[type="radio"] {
  margin-right: 12px;
  margin-top: 2px;
}

.radio-label {
  flex: 1;
}

.role-name {
  display: block;
  font-weight: 500;
  color: #111827;
  margin-bottom: 4px;
}

.role-desc {
  display: block;
  font-size: 12px;
  color: #6b7280;
}

.role-badge {
  color: #0071e4;
  font-size: 11px;
  background: #e6f7ff;
  padding: 2px 6px;
  border-radius: 3px;
  margin-left: 8px;
}

.loading-roles {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #6b7280;
  font-size: 14px;
}

/* 状态切换 */
.status-toggle {
  display: flex;
  align-items: center;
}

.status-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 2px solid;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.status-button.status-enabled {
  border-color: #10b981;
  color: #10b981;
  background: #f0fdf4;
}

.status-button.status-enabled:hover:not(:disabled) {
  background: #dcfce7;
  border-color: #059669;
}

.status-button.status-disabled {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.status-button.status-disabled:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #dc2626;
}

.status-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-icon {
  font-size: 16px;
  font-weight: bold;
}

.status-text {
  font-size: 14px;
}

/* 统计信息 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.stat-value.online {
  color: #10b981;
}

.stat-value.offline {
  color: #6b7280;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn-secondary,
.btn-primary {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .modal-container {
    width: 95%;
    margin: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-body {
    max-height: 50vh;
  }
}
</style>