<template>
  <div class="role-card" :class="{ 'selected': selected }">
    <div class="card-header">
      <div class="selection-area">
        <input 
          type="checkbox" 
          :checked="selected" 
          @change="$emit('select', role.id, $event.target.checked)"
          class="role-checkbox"
        />
      </div>
      <div class="role-icon" :class="{ 'system': role.is_system }">
        <RoleIcon />
      </div>
      <div class="role-info">
        <div class="role-name">{{ role.name }}</div>
        <div class="role-code">{{ role.code }}</div>
      </div>
      <div class="status-tags">
        <div class="status-tag" :class="role.status ? 'active' : 'inactive'">
          {{ role.status ? '启用' : '禁用' }}
        </div>
        <div v-if="role.is_system" class="type-tag system">
          系统
        </div>
        <div v-else class="type-tag custom">
          自定义
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <div class="description" v-if="role.description">
        {{ role.description }}
      </div>
      <div class="description empty" v-else>
        暂无描述
      </div>
      
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-label">权限数量:</span>
          <span class="stat-value">{{ role.permission_count || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">用户数量:</span>
          <span class="stat-value">{{ role.user_count || 0 }}</span>
        </div>
      </div>
      
      <div class="meta-info">
        <div class="meta-item">
          <span class="meta-label">创建人:</span>
          <span class="meta-value">{{ role.creator_name || '-' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">创建时间:</span>
          <span class="meta-value">{{ formatDateTime(role.created_at) }}</span>
        </div>
      </div>
    </div>
    
    <div class="card-actions">
      <button class="action-btn edit-btn" @click="$emit('edit', role)">
        <EditIcon class="btn-icon" />
        <span>编辑</span>
      </button>
      <button class="action-btn permission-btn" @click="$emit('permissions', role)">
        <KeyIcon class="btn-icon" />
        <span>权限</span>
      </button>
      <button 
        class="action-btn delete-btn" 
        @click="$emit('delete', role)"
        :disabled="role.is_system"
      >
        <TrashIcon class="btn-icon" />
        <span>删除</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import RoleIcon from './icons/RoleIcon.vue'
import EditIcon from '@/components/account/icons/EditIcon.vue'
import KeyIcon from '@/components/account/icons/KeyIcon.vue'
import TrashIcon from '@/components/account/icons/TrashIcon.vue'

const props = defineProps({
  role: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select', 'edit', 'permissions', 'delete'])

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
.role-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.role-card.selected {
  border-color: #0071e4;
  box-shadow: 0 4px 20px rgba(0, 113, 228, 0.15);
}

.card-header {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.selection-area {
  position: absolute;
  top: 12px;
  left: 12px;
}

.role-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.role-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 24px;
  margin-right: 12px;
}

.role-icon.system {
  background-color: #fff2e8;
}

.role-icon svg {
  width: 24px;
  height: 24px;
  color: #0071e4;
}

.role-icon.system svg {
  color: #fa8c16;
}

.role-info {
  flex: 1;
}

.role-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.role-code {
  font-size: 12px;
  color: #666;
  font-family: 'Courier New', monospace;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

.status-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-tag, .type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
  min-width: 40px;
}

.status-tag.active {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-tag.inactive {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.type-tag.system {
  background-color: #fff2e8;
  color: #fa8c16;
}

.type-tag.custom {
  background-color: #f0f5ff;
  color: #1890ff;
}

.card-body {
  padding: 16px;
  flex: 1;
}

.description {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 16px;
}

.description.empty {
  color: #999;
  font-style: italic;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #0071e4;
}

.meta-info {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.meta-item {
  display: flex;
  margin-bottom: 4px;
}

.meta-label {
  width: 70px;
  font-size: 12px;
  color: #666;
}

.meta-value {
  flex: 1;
  font-size: 12px;
  color: #333;
}

.card-actions {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  gap: 8px;
}

.action-btn {
  height: 32px;
  padding: 0 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.edit-btn:hover:not(:disabled) {
  background-color: #e6e6e6;
}

.permission-btn {
  background-color: #e6f7ff;
  color: #0071e4;
}

.permission-btn:hover:not(:disabled) {
  background-color: #bae7ff;
}

.delete-btn {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.delete-btn:hover:not(:disabled) {
  background-color: #ffccc7;
}
</style>