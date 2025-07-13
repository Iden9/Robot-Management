<template>
  <div class="sidebar">
    <div class="logo-container">
      <img src="@/assets/robot-logo.svg" alt="Robot Logo" class="logo-icon" />
      <span class="logo-text">宇树G1 EDU</span>
    </div>
    
    <nav class="nav-menu">
      <!-- 动态菜单项 -->
      <router-link 
        v-for="menuItem in availableMenus"
        :key="menuItem.name"
        :to="menuItem.path" 
        class="nav-item" 
        active-class="active"
      >
        <div class="nav-icon" v-html="getMenuIcon(menuItem.icon)"></div>
        <span>{{ menuItem.title }}</span>
      </router-link>
      
      <!-- 退出系统 -->
      <div class="nav-item logout" @click="handleLogout">
        <div class="nav-icon" v-html="getMenuIcon('logout')"></div>
        <span>退出系统</span>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getAvailableMenus } from '@/utils/menu'
import { MENU_ICONS } from '@/config/menu'

const router = useRouter()
const authStore = useAuthStore()

// 获取用户可访问的菜单列表
const availableMenus = computed(() => getAvailableMenus())

// 获取菜单图标
const getMenuIcon = (iconName) => {
  return MENU_ICONS[iconName] || ''
}

const handleLogout = async () => {
  try {
    // 调用登出 API
    await authStore.logoutAction()
    
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    // 即使登出失败，也要清理本地状态并跳转
    authStore.clearAuth()
    router.push('/login')
  }
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  height: 100vh;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
}

.logo-container {
  display: flex;
  align-items: center;
  padding: 0 24px;
  margin-bottom: 24px;
  height: 50px;
}

.logo-icon {
  width: 24px;
  height: 24px;
  margin-right: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #0071e4;
}

.nav-menu {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
  color: #666;
  text-decoration: none;
  transition: background-color 0.3s, color 0.3s;
}

.nav-item:hover {
  background-color: #f0f0f0;
  color: #0071e4;
}

.nav-item.active {
  color: #0071e4;
  background-color: #e6f7ff;
  border-right: 3px solid #0071e4;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-right: 10px;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.logout {
  margin-top: auto;
}
</style>