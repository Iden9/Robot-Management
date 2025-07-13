<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">分配权限</h3>
        <button @click="$emit('close')" class="close-btn">
          <ClearIcon />
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="role" class="role-info">
          <h4>角色：{{ role.name }}</h4>
          <p>{{ role.description || '暂无描述' }}</p>
        </div>
        
        <div class="permission-section">
          <div class="section-header">
            <h5>权限列表</h5>
            <div class="batch-actions">
              <button @click="selectAll" class="batch-btn">全选</button>
              <button @click="selectNone" class="batch-btn">全不选</button>
            </div>
          </div>
          
          <div v-if="loading" class="loading">
            加载权限列表中...
          </div>
          
          <div v-else class="permission-tree">
            <div 
              v-for="module in permissionModules" 
              :key="module.module" 
              class="module-group"
            >
              <div class="module-header">
                <label class="module-label">
                  <input
                    type="checkbox"
                    :checked="isModuleChecked(module)"
                    :indeterminate.prop="isModuleIndeterminate(module)"
                    @change="handleModuleCheck(module, $event.target.checked)"
                    class="module-checkbox"
                  />
                  <span class="module-name">{{ module.module }}</span>
                </label>
              </div>
              
              <div class="permission-list">
                <label
                  v-for="permission in module.permissions"
                  :key="permission.id"
                  class="permission-item"
                >
                  <input
                    type="checkbox"
                    :value="permission.id"
                    v-model="selectedPermissions"
                    class="permission-checkbox"
                  />
                  <span class="permission-info">
                    <span class="permission-name">{{ permission.name }}</span>
                    <span class="permission-type" :class="getPermissionTypeClass(permission.permission_type)">
                      {{ getPermissionTypeText(permission.permission_type) }}
                    </span>
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-cancel">取消</button>
        <button @click="handleSave" class="btn btn-primary" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import ClearIcon from '@/components/account/icons/ClearIcon.vue'
import { getAllActivePermissions } from '@/api/permission'
import { getRolePermissions } from '@/api/role'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  role: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const saving = ref(false)
const permissionModules = ref([])
const selectedPermissions = ref([])

// 监听弹窗显示状态
watch(() => props.show, async (show) => {
  if (show && props.role) {
    await loadPermissions()
    await loadRolePermissions()
  }
})

// 加载权限列表
const loadPermissions = async () => {
  loading.value = true
  try {
    const response = await getAllActivePermissions()
    if (response.code === 200) {
      permissionModules.value = response.data
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载角色权限
const loadRolePermissions = async () => {
  if (!props.role?.id) return
  
  try {
    const response = await getRolePermissions(props.role.id)
    if (response.code === 200) {
      selectedPermissions.value = response.data.map(p => p.id)
    }
  } catch (error) {
    console.error('加载角色权限失败:', error)
  }
}

// 检查模块是否全选
const isModuleChecked = (module) => {
  const modulePermissionIds = module.permissions.map(p => p.id)
  return modulePermissionIds.length > 0 && 
         modulePermissionIds.every(id => selectedPermissions.value.includes(id))
}

// 检查模块是否部分选中
const isModuleIndeterminate = (module) => {
  const modulePermissionIds = module.permissions.map(p => p.id)
  const checkedCount = modulePermissionIds.filter(id => selectedPermissions.value.includes(id)).length
  return checkedCount > 0 && checkedCount < modulePermissionIds.length
}

// 处理模块选择
const handleModuleCheck = (module, checked) => {
  const modulePermissionIds = module.permissions.map(p => p.id)
  
  if (checked) {
    // 选中所有该模块的权限
    modulePermissionIds.forEach(id => {
      if (!selectedPermissions.value.includes(id)) {
        selectedPermissions.value.push(id)
      }
    })
  } else {
    // 取消选中该模块的所有权限
    selectedPermissions.value = selectedPermissions.value.filter(
      id => !modulePermissionIds.includes(id)
    )
  }
}

// 全选
const selectAll = () => {
  const allPermissionIds = []
  permissionModules.value.forEach(module => {
    module.permissions.forEach(permission => {
      allPermissionIds.push(permission.id)
    })
  })
  selectedPermissions.value = [...allPermissionIds]
}

// 全不选
const selectNone = () => {
  selectedPermissions.value = []
}

// 获取权限类型样式类
const getPermissionTypeClass = (type) => {
  const classMap = {
    'menu': 'type-menu',
    'button': 'type-button',
    'api': 'type-api'
  }
  return classMap[type] || 'type-default'
}

// 获取权限类型文本
const getPermissionTypeText = (type) => {
  const textMap = {
    'menu': '菜单',
    'button': '按钮',
    'api': '接口'
  }
  return textMap[type] || type
}

// 保存权限
const handleSave = async () => {
  saving.value = true
  try {
    await emit('save', selectedPermissions.value)
  } finally {
    saving.value = false
  }
}

const handleOverlayClick = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 700px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: #666;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: #f0f0f0;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.role-info {
  margin-bottom: 20px;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.role-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.role-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.permission-section {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.section-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.batch-btn {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  background-color: white;
  color: #666;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.batch-btn:hover {
  border-color: #0071e4;
  color: #0071e4;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #666;
}

.permission-tree {
  max-height: 400px;
  overflow-y: auto;
}

.module-group {
  border-bottom: 1px solid #f0f0f0;
}

.module-group:last-child {
  border-bottom: none;
}

.module-header {
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

.module-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  color: #333;
}

.module-checkbox {
  margin-right: 8px;
  width: 16px;
  height: 16px;
}

.module-name {
  font-size: 14px;
}

.permission-list {
  padding: 8px 0;
}

.permission-item {
  display: flex;
  align-items: flex-start;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.permission-item:hover {
  background-color: #f8f9fa;
}

.permission-checkbox {
  margin-right: 12px;
  margin-top: 2px;
  width: 16px;
  height: 16px;
}

.permission-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.permission-name {
  font-size: 14px;
  color: #333;
}

.permission-type {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
  max-width: fit-content;
}

.type-menu {
  background-color: #e6f7ff;
  color: #0071e4;
}

.type-button {
  background-color: #f6ffed;
  color: #52c41a;
}

.type-api {
  background-color: #fff2e8;
  color: #fa8c16;
}

.type-default {
  background-color: #f0f0f0;
  color: #666;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  height: 36px;
  padding: 0 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #333;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #e6e6e6;
}

.btn-primary {
  background-color: #0071e4;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #005bb5;
}
</style>