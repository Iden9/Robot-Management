<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">
        <img src="@/assets/robot-logo.svg" alt="Robot Logo" />
      </div>
      <h1 class="title">宇树G1 EDU机器人</h1>
      
      <!-- 错误信息显示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="form-item">
        <label>账号</label>
        <input 
          type="text" 
          placeholder="请输入账号" 
          v-model="formData.username"
          @keyup="handleKeyup"
          :disabled="isLoading"
        />
      </div>
      
      <div class="form-item">
        <label>密码</label>
        <input 
          type="password" 
          placeholder="请输入密码" 
          v-model="formData.password"
          @keyup="handleKeyup"
          :disabled="isLoading"
        />
      </div>
      
      
      <button 
        class="login-btn" 
        @click="handleLogin"
        :disabled="isLoading"
        :class="{ loading: isLoading }">
        {{ isLoading ? '登录中...' : '登录系统' }}
      </button>
      
      <div class="register-link">
        <p>还没有账号？ <router-link to="/register">立即注册</router-link></p>
      </div>
      
      <div class="copyright">
        © 2025 宇树科技 - 智能机器人管理系统
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const formData = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

// 处理登录
const handleLogin = async () => {
  // 验证表单
  if (!formData.username) {
    errorMessage.value = '请输入用户名'
    return
  }
  if (!formData.password) {
    errorMessage.value = '请输入密码'
    return
  }

  try {
    isLoading.value = true
    errorMessage.value = ''
    
    // 构建登录参数
    const loginData = {
      username: formData.username,
      password: formData.password
    }
    
    // 调用登录API
    const result = await authStore.loginAction(loginData)
    
    if (result.success) {
      // 登录成功，禁用页面过渡动画
      if (window.disableRouteTransition) {
        window.disableRouteTransition(true)
      }
      
      // 检查是否有重定向地址
      const redirect = router.currentRoute.value.query.redirect
      if (redirect) {
        // 有重定向地址，跳转到指定页面
        router.push(redirect)
      } else {
        // 没有重定向地址，根据角色跳转到默认页面
        if (result.data.user.role === 'viewer') {
          router.push('/education')
        } else {
          router.push('/dashboard')
        }
      }
    } else {
      // 登录失败，显示错误信息
      const message = result.message || '登录失败'
      errorMessage.value = message
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMessage.value = error.message || '登录失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}


// 回车登录
const handleKeyup = (event) => {
  if (event.key === 'Enter') {
    handleLogin()
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-box {
  width: 380px;
  padding: 40px;
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.logo img {
  width: 60px;
  height: 60px;
  color: #0071e4;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin: 20px 0 30px;
  color: #333;
}

.form-item {
  margin-bottom: 20px;
  text-align: left;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.form-item input {
  width: 100%;
  height: 40px;
  padding: 0 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-item input:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 2px rgba(0, 113, 228, 0.2);
}


.login-btn {
  width: 100%;
  height: 40px;
  background-color: #0071e4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 30px;
}

.copyright {
  font-size: 12px;
  color: #999;
}

.error-message {
  background-color: #fef0f0;
  color: #f56565;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #fed7d7;
  font-size: 14px;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-btn.loading {
  background-color: #409eff;
}


input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.register-link {
  margin-bottom: 20px;
  text-align: center;
}

.register-link p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #0071e4;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>