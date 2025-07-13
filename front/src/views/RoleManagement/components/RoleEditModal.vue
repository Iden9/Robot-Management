<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">{{ isEdit ? '编辑角色' : '新增角色' }}</h3>
        <button @click="$emit('close')" class="close-btn">
          <ClearIcon />
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="role-form">
          <div class="form-group">
            <label class="form-label" for="roleName">角色名称 *</label>
            <input
              id="roleName"
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="请输入角色名称"
              :class="{ error: errors.name }"
              required
            />
            <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="roleCode">角色编码 *</label>
            <input
              id="roleCode"
              v-model="formData.code"
              type="text"
              class="form-input"
              placeholder="请输入角色编码（字母、数字、下划线）"
              :class="{ error: errors.code }"
              pattern="^[a-zA-Z][a-zA-Z0-9_]*$"
              required
            />
            <div v-if="errors.code" class="error-message">{{ errors.code }}</div>
            <div class="form-hint">编码必须以字母开头，只能包含字母、数字和下划线</div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="roleDescription">角色描述</label>
            <textarea
              id="roleDescription"
              v-model="formData.description"
              class="form-textarea"
              placeholder="请输入角色描述"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="sortOrder">排序</label>
            <input
              id="sortOrder"
              v-model.number="formData.sort_order"
              type="number"
              class="form-input"
              placeholder="数字越小排序越靠前"
              min="0"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">状态</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.status"
                  type="checkbox"
                  class="checkbox-input"
                />
                <span class="checkbox-text">启用角色</span>
              </label>
            </div>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-cancel">取消</button>
        <button @click="handleSubmit" class="btn btn-primary" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import ClearIcon from '@/components/account/icons/ClearIcon.vue'

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

const saving = ref(false)
const errors = reactive({})

const formData = reactive({
  name: '',
  code: '',
  description: '',
  sort_order: 0,
  status: true
})

const isEdit = computed(() => props.role && props.role.id)

// 监听角色数据变化
watch(() => props.role, (newRole) => {
  if (newRole) {
    // 编辑模式：填充表单
    Object.assign(formData, {
      name: newRole.name || '',
      code: newRole.code || '',
      description: newRole.description || '',
      sort_order: newRole.sort_order || 0,
      status: newRole.status !== false
    })
  } else {
    // 新增模式：重置表单
    Object.assign(formData, {
      name: '',
      code: '',
      description: '',
      sort_order: 0,
      status: true
    })
  }
  // 清除错误
  Object.keys(errors).forEach(key => delete errors[key])
}, { immediate: true })

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key])
  
  if (!formData.name.trim()) {
    errors.name = '角色名称不能为空'
  } else if (formData.name.trim().length < 2) {
    errors.name = '角色名称至少2个字符'
  }
  
  if (!formData.code.trim()) {
    errors.code = '角色编码不能为空'
  } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(formData.code.trim())) {
    errors.code = '角色编码必须以字母开头，只能包含字母、数字和下划线'
  }
  
  return Object.keys(errors).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  saving.value = true
  try {
    const data = {
      name: formData.name.trim(),
      code: formData.code.trim(),
      description: formData.description.trim() || null,
      sort_order: formData.sort_order,
      status: formData.status
    }
    
    await emit('save', data)
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
  width: 500px;
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

.role-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input, .form-textarea {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #0071e4;
}

.form-input.error, .form-textarea.error {
  border-color: #ff4d4f;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}

.error-message {
  margin-top: 4px;
  font-size: 12px;
  color: #ff4d4f;
}

.checkbox-group {
  margin-top: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-input {
  margin-right: 8px;
  width: 16px;
  height: 16px;
}

.checkbox-text {
  font-size: 14px;
  color: #333;
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