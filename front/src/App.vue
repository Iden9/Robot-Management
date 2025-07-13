<script setup>
import SiderBar from './components/SiderBar.vue'
import Header from './components/Header.vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 禁用过渡动画的状态
const disableTransition = ref(false)

// 将禁用状态暴露给全局，让其他组件可以控制
window.disableRouteTransition = (disable = true) => {
  disableTransition.value = disable
  if (disable) {
    // 500ms后自动恢复过渡效果
    setTimeout(() => {
      disableTransition.value = false
    }, 500)
  }
}

// 在登录页面和注册页面不显示侧边栏和顶部栏
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

// 应用启动时检查认证状态
onMounted(async () => {
  // 如果有token，验证其有效性
  if (authStore.token) {
    try {
      const isValid = await authStore.checkTokenValidity()
      if (!isValid) {
        // token无效，清理认证状态
        authStore.clearAuth()
        if (route.meta?.requiresAuth) {
          router.push('/login')
        }
      }
    } catch (error) {
      console.error('检查token有效性失败:', error)
      authStore.clearAuth()
      if (route.meta?.requiresAuth) {
        router.push('/login')
      }
    }
  }
  
})
</script>

<template>
  <div class="app-container">
    <SiderBar v-if="!isAuthPage" />
    <div class="main-content" :class="{ 'full-width': isAuthPage }">
      <Header v-if="!isAuthPage" />
      <div class="content-area">
        <RouterView v-slot="{ Component, route }">
          <Transition 
            :name="disableTransition ? 'none' : 'page-fade'" 
            mode="out-in"
          >
            <component :is="Component" :key="route.path" />
          </Transition>
        </RouterView>
      </div>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: Arial, sans-serif;
}

.app-container {
  display: flex;
  height: 100vh;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f7f9;
  display: flex;
  flex-direction: column;
}

.content-area {
  padding: 20px;
  flex: 1;
}

.full-width .content-area {
  padding: 0;
}

.full-width {
  width: 100%;
}

/* 页面切换过渡动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease-in-out;
}

.page-fade-enter-from {
  opacity: 0;
}

.page-fade-leave-to {
  opacity: 0;
}

.page-fade-enter-to,
.page-fade-leave-from {
  opacity: 1;
}

/* 禁用过渡动画 */
.none-enter-active,
.none-leave-active {
  transition: none !important;
  animation: none !important;
}
</style>
