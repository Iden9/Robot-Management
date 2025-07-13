<template>
  <div class="account-card">
    <div class="card-header">
      <div class="user-avatar" :class="{ 'admin': account.role === 'admin' }">
        <UserIcon />
      </div>
      <div class="user-info">
        <div class="username">{{ account.username }}</div>
        <div class="role-tag" :class="roleClass">{{ roleText }}</div>
      </div>
    </div>
    
    <div class="card-body">
      <div class="info-row">
        <span class="label">真实姓名:</span>
        <span class="value">{{ account.real_name || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">手机号码:</span>
        <span class="value">{{ account.phone || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">创建时间:</span>
        <span class="value">{{ formatDateTime(account.created_at) }}</span>
      </div>
      <div class="info-row">
        <span class="label">最后登录:</span>
        <span class="value">{{ formatDateTime(account.last_login) }}</span>
      </div>
    </div>
    
    <div class="card-actions">
      <button class="action-btn edit-btn" @click="$emit('edit', account)">
        <EditIcon class="btn-icon" />
        <span>编辑</span>
      </button>
      <button class="action-btn reset-btn" @click="$emit('reset-password', account)">
        <KeyIcon class="btn-icon" />
        <span>重置密码</span>
      </button>
      <button class="action-btn delete-btn" @click="$emit('delete', account)">
        <TrashIcon class="btn-icon" />
        <span>删除</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import UserIcon from './icons/UserIcon.vue'
import KeyIcon from './icons/KeyIcon.vue'
import EditIcon from './icons/EditIcon.vue'
import TrashIcon from './icons/TrashIcon.vue'

const props = defineProps({
  account: {
    type: Object,
    required: true
  }
})

// 计算角色样式类
const roleClass = computed(() => {
  switch (props.account.role) {
    case 'admin':
      return 'role-admin'
    case 'operator':
      return 'role-operator'
    case 'viewer':
      return 'role-viewer'
    default:
      return ''
  }
})

// 计算角色显示文本
const roleText = computed(() => {
  switch (props.account.role) {
    case 'admin':
      return '管理员'
    case 'operator':
      return '操作员'
    case 'viewer':
      return '访客'
    default:
      return props.account.role
  }
})

// 格式化日期时间
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-'
  
  try {
    const date = new Date(dateTimeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateTimeString
  }
}
</script>

<style scoped>
.account-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.user-avatar.admin {
  background-color: #fff2e8;
}

.user-avatar svg {
  width: 24px;
  height: 24px;
  color: #0071e4;
}

.user-avatar.admin svg {
  color: #fa8c16;
}

.user-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.role-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.role-admin {
  background-color: #fff2e8;
  color: #fa8c16;
}

.role-operator {
  background-color: #e6f7ff;
  color: #0071e4;
}

.role-viewer {
  background-color: #f6ffed;
  color: #52c41a;
}

.card-body {
  padding: 16px;
  flex: 1;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.label {
  width: 80px;
  color: #666;
  font-size: 14px;
}

.value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.card-actions {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  height: 32px;
  padding: 0 12px;
  margin-right: 8px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.btn-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}

.edit-btn {
  background-color: #f0f0f0;
  color: #333;
}

.edit-btn:hover {
  background-color: #e6e6e6;
}

.reset-btn {
  background-color: #e6f7ff;
  color: #0071e4;
}

.reset-btn:hover {
  background-color: #bae7ff;
}

.delete-btn {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.delete-btn:hover {
  background-color: #ffccc7;
}
</style> 