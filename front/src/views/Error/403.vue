<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      </div>
      
      <h1 class="error-title">403</h1>
      <h2 class="error-subtitle">权限不足</h2>
      <p class="error-description">
        抱歉，您没有权限访问此页面。<br>
        请联系系统管理员获取相应权限。
      </p>
      
      <div class="error-actions">
        <button class="btn btn-primary" @click="goBack">
          返回上一页
        </button>
        <button class="btn btn-secondary" @click="goHome">
          回到首页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.go(-1)
}

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 40px 20px;
}

.error-content {
  text-align: center;
  max-width: 500px;
}

.error-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 30px;
  color: #ff6b6b;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-title {
  font-size: 72px;
  font-weight: bold;
  color: #ff6b6b;
  margin: 0 0 10px 0;
  line-height: 1;
}

.error-subtitle {
  font-size: 24px;
  color: #333;
  margin: 0 0 20px 0;
}

.error-description {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 40px 0;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  min-width: 120px;
}

.btn-primary {
  background-color: #0071e4;
  color: white;
}

.btn-primary:hover {
  background-color: #0062c4;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e6e6e6;
}

@media (max-width: 768px) {
  .error-title {
    font-size: 48px;
  }
  
  .error-subtitle {
    font-size: 20px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}
</style>