<template>
  <div class="header">
    <h1 class="title">{{ currentTitle }}</h1>
    <div class="user-dropdown-container">
      <div class="user-info" @click.stop="toggleDropdown">
        <div class="user-avatar">{{ userAvatar }}</div>
        <div class="user-details">
          <div class="user-name">{{ userName }}</div>
          <div class="user-role">{{ userRoleText }}</div>
        </div>
      </div>
      
      <!-- 用户下拉菜单 -->
      <div class="user-dropdown" v-if="showDropdown" @click.stop>
        <div class="dropdown-item" @click="handleViewProfile">
          <span class="dropdown-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </span>
          <span>个人信息</span>
        </div>
        <div class="dropdown-divider"></div>
        <div class="dropdown-item" @click="handleLogout">
          <span class="dropdown-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </span>
          <span>退出登录</span>
        </div>
      </div>
    </div>
    
    <!-- 个人信息弹窗 -->
    <div v-if="showProfileModal" class="modal-overlay" @click="showProfileModal = false">
      <div class="profile-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">个人信息</h3>
          <button class="close-btn" @click="showProfileModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="profile-avatar-section">
            <div class="profile-avatar-large">{{ userAvatar }}</div>
          </div>
          
          <div class="profile-info">
            <div class="info-item">
              <label class="info-label">用户名</label>
              <div class="info-value">{{ authStore.userInfo?.username || '未知' }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">真实姓名</label>
              <div class="info-value">{{ authStore.userInfo?.real_name || '未设置' }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">邮箱</label>
              <div class="info-value">{{ authStore.userInfo?.email || '未设置' }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">手机号</label>
              <div class="info-value">{{ authStore.userInfo?.phone || '未设置' }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">角色</label>
              <div class="info-value">
                <span class="role-badge" :class="authStore.userInfo?.role">
                  {{ userRoleText }}
                </span>
              </div>
            </div>
            
            <div class="info-item">
              <label class="info-label">注册时间</label>
              <div class="info-value">{{ formatDate(authStore.userInfo?.created_at) }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">最后登录</label>
              <div class="info-value">{{ formatDate(authStore.userInfo?.last_login) }}</div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-cancel" @click="showProfileModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 下拉菜单状态
const showDropdown = ref(false)
// 个人信息弹窗状态
const showProfileModal = ref(false)

// 根据路由路径映射页面标题
const titleMap = {
  '/dashboard': '系统看板',
  '/education': '教育培训',
  '/navigation': '自主导览',
  '/equipment': '设备管理',
  '/account': '账号管理',
  '/system': '系统设置',
  '/robot-control': '机器人控制'
}

// 根据当前路由路径获取对应的标题
const currentTitle = computed(() => {
  return titleMap[route.path] || 'G1 EDU机器人'
})

// 用户信息
const userName = computed(() => {
  return authStore.userName || '未知用户'
})

const userRoleText = computed(() => {
  const roleMap = {
    admin: '系统管理员',
    operator: '操作员',
    viewer: '查看者'
  }
  return roleMap[authStore.userRole] || '未知角色'
})

const userAvatar = computed(() => {
  const name = authStore.userName
  if (name && name.length > 0) {
    // 获取用户名的第一个字符作为头像
    return name.charAt(0).toUpperCase()
  }
  return '用'
})

// 切换下拉菜单显示状态
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// 查看个人信息
const handleViewProfile = () => {
  showDropdown.value = false
  showProfileModal.value = true
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '未知'
  }
}

// 处理退出登录
const handleLogout = async () => {
  showDropdown.value = false
  
  try {
    // 调用登出 API
    await authStore.logoutAction()
    
    // 退出登录，禁用页面过渡动画
    if (window.disableRouteTransition) {
      window.disableRouteTransition(true)
    }
    
    // 直接跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    // 即使登出失败，也要清理本地状态并跳转
    authStore.clearAuth()
    
    // 禁用过渡动画
    if (window.disableRouteTransition) {
      window.disableRouteTransition(true)
    }
    
    router.push('/login')
  }
}

// 点击外部关闭下拉菜单
const closeDropdownOnClickOutside = (event) => {
  if (showDropdown.value) {
    showDropdown.value = false
  }
}

// 添加全局点击事件监听器
onMounted(() => {
  document.addEventListener('click', closeDropdownOnClickOutside)
})

// 移除全局点击事件监听器
onUnmounted(() => {
  document.removeEventListener('click', closeDropdownOnClickOutside)
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 10px 24px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.user-dropdown-container {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #0071e4;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-right: 10px;
}

.user-details {
  text-align: left;
}

.user-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.user-role {
  font-size: 12px;
  color: #999;
}

/* 下拉菜单样式 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 160px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin-top: 5px;
  z-index: 1000;
  overflow: hidden;
  animation: dropdownFadeIn 0.2s ease-out;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #333;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-icon {
  display: flex;
  align-items: center;
  margin-right: 8px;
  color: #666;
}

.dropdown-divider {
  height: 1px;
  background-color: #e8e8e8;
  margin: 4px 0;
}

/* 个人信息弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.profile-modal {
  background-color: white;
  border-radius: 12px;
  width: 480px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e8e8;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  color: #666;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.profile-avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.profile-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #0071e4;
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.info-value {
  font-size: 14px;
  color: #333;
  text-align: right;
  flex: 1;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background-color: #e6f7ff;
  color: #1890ff;
}

.role-badge.operator {
  background-color: #f6ffed;
  color: #52c41a;
}

.role-badge.viewer {
  background-color: #fff7e6;
  color: #fa8c16;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e8e8e8;
  text-align: right;
}

.btn-cancel {
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: #e8e8e8;
  color: #333;
}
</style>