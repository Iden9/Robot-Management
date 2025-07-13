<template>
  <div class="register-container">
    <div class="register-box">
      <div class="logo">
        <img src="@/assets/robot-logo.svg" alt="Robot Logo" />
      </div>
      <h1 class="title">宇树G1 EDU机器人</h1>
      <p class="subtitle">用户注册</p>
      
      <!-- 进度指示器 -->
      <div class="progress-indicator">
        <div class="progress-step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
          <div class="step-number">1</div>
          <div class="step-label">基本信息</div>
        </div>
        <div class="progress-line" :class="{ active: currentStep > 1 }"></div>
        <div class="progress-step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
          <div class="step-number">2</div>
          <div class="step-label">联系方式</div>
        </div>
        <div class="progress-line" :class="{ active: currentStep > 2 }"></div>
        <div class="progress-step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
          <div class="step-number">3</div>
          <div class="step-label">密码设置</div>
        </div>
      </div>
      
      <!-- 错误信息显示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <!-- 步骤1: 基本信息 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3 class="step-title">基本信息</h3>
        <div class="form-item">
          <label>用户名</label>
          <input 
            type="text" 
            placeholder="请输入用户名" 
            v-model="formData.username"
            @keyup="handleKeyup"
            :disabled="isLoading"
          />
        </div>

        <div class="form-item">
          <label>真实姓名</label>
          <input 
            type="text" 
            placeholder="请输入真实姓名" 
            v-model="formData.real_name"
            @keyup="handleKeyup"
            :disabled="isLoading"
          />
        </div>

        <div class="step-actions">
          <button class="next-btn" @click="nextStep" :disabled="!canProceedStep1">
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤2: 联系方式 -->
      <div v-if="currentStep === 2" class="step-content">
        <h3 class="step-title">联系方式</h3>
        <div class="form-item">
          <label>邮箱地址</label>
          <input 
            type="email" 
            placeholder="请输入邮箱地址" 
            v-model="formData.email"
            @keyup="handleKeyup"
            :disabled="isLoading"
          />
        </div>

        <div class="form-item">
          <label>手机号码</label>
          <input 
            type="tel" 
            placeholder="请输入手机号码（可选）" 
            v-model="formData.phone"
            @keyup="handleKeyup"
            :disabled="isLoading"
          />
        </div>

        <div class="step-actions">
          <button class="prev-btn" @click="prevStep">
            上一步
          </button>
          <button class="next-btn" @click="nextStep" :disabled="!canProceedStep2">
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤3: 密码设置 -->
      <div v-if="currentStep === 3" class="step-content">
        <h3 class="step-title">密码设置</h3>
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

        <div class="form-item">
          <label>确认密码</label>
          <input 
            type="password" 
            placeholder="请再次输入密码" 
            v-model="formData.confirmPassword"
            @keyup="handleKeyup"
            :disabled="isLoading"
          />
        </div>

        <div class="step-actions">
          <button class="prev-btn" @click="prevStep">
            上一步
          </button>
          <button 
            class="register-btn" 
            @click="handleRegister"
            :disabled="isLoading || !canProceedStep3"
            :class="{ loading: isLoading }">
            {{ isLoading ? '注册中...' : '注册账号' }}
          </button>
        </div>
      </div>
      
      <div class="login-link">
        <p>已有账号？ <router-link to="/login">立即登录</router-link></p>
      </div>
      
      <div class="copyright">
        © 2025 宇树科技 - 智能机器人管理系统
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const currentStep = ref(1)
const isLoading = ref(false)
const errorMessage = ref('')

const formData = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

// 步骤验证
const canProceedStep1 = computed(() => {
  return formData.username.trim() && formData.real_name.trim()
})

const canProceedStep2 = computed(() => {
  return formData.email.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
})

const canProceedStep3 = computed(() => {
  return formData.password.length >= 6 && formData.password === formData.confirmPassword
})

// 步骤导航
const nextStep = () => {
  errorMessage.value = ''
  
  if (currentStep.value === 1 && canProceedStep1.value) {
    currentStep.value = 2
  } else if (currentStep.value === 2 && canProceedStep2.value) {
    currentStep.value = 3
  }
}

const prevStep = () => {
  errorMessage.value = ''
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const handleRegister = async () => {
  if (isLoading.value) return

  // 最终验证
  if (!canProceedStep1.value) {
    errorMessage.value = '请完善基本信息'
    currentStep.value = 1
    return
  }
  if (!canProceedStep2.value) {
    errorMessage.value = '请输入正确的邮箱地址'
    currentStep.value = 2
    return
  }
  if (!canProceedStep3.value) {
    errorMessage.value = '密码长度至少6位且两次输入必须一致'
    return
  }

  try {
    isLoading.value = true
    errorMessage.value = ''

    const result = await authStore.registerAction({
      username: formData.username,
      real_name: formData.real_name,
      email: formData.email,
      phone: formData.phone,
      password: formData.password
    })

    if (result.success) {
      // 注册成功，跳转到登录页面
      router.push({
        name: 'Login',
        query: { message: '注册成功，请登录' }
      })
    } else {
      // 注册失败，显示错误信息
      errorMessage.value = result.message || '注册失败'
    }
    
  } catch (error) {
    console.error('注册失败:', error)
    errorMessage.value = error.message || '注册失败，请重试'
  } finally {
    isLoading.value = false
  }
}

// 回车处理
const handleKeyup = (event) => {
  if (event.key === 'Enter') {
    if (currentStep.value === 1 && canProceedStep1.value) {
      nextStep()
    } else if (currentStep.value === 2 && canProceedStep2.value) {
      nextStep()
    } else if (currentStep.value === 3 && canProceedStep3.value) {
      handleRegister()
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.register-box {
  width: 420px;
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
  margin: 20px 0 10px;
  color: #333;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

/* 进度指示器 */
.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.progress-step.active {
  opacity: 1;
}

.progress-step.completed {
  opacity: 1;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #ddd;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 5px;
  transition: all 0.3s;
}

.progress-step.active .step-number {
  background-color: #0071e4;
  color: white;
}

.progress-step.completed .step-number {
  background-color: #28a745;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.progress-step.active .step-label {
  color: #0071e4;
  font-weight: 500;
}

.progress-line {
  width: 50px;
  height: 2px;
  background-color: #ddd;
  margin: 0 10px;
  transition: background-color 0.3s;
}

.progress-line.active {
  background-color: #0071e4;
}

/* 步骤内容 */
.step-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
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
  transition: border-color 0.3s;
}

.form-item input:focus {
  outline: none;
  border-color: #0071e4;
}

.form-item input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 30px;
}

.prev-btn, .next-btn, .register-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.prev-btn {
  background-color: #f5f5f5;
  color: #666;
}

.prev-btn:hover {
  background-color: #e8e8e8;
}

.next-btn, .register-btn {
  background-color: #0071e4;
  color: white;
  min-width: 80px;
}

.next-btn:hover:not(:disabled), .register-btn:hover:not(:disabled) {
  background-color: #005bb5;
}

.next-btn:disabled, .register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.register-btn.loading {
  background-color: #409eff;
}

.login-link {
  margin: 30px 0 20px;
  text-align: center;
}

.login-link p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #0071e4;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
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
</style>