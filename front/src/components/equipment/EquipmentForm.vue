<template>
  <div class="equipment-form">
    <h2 class="form-title">{{ title }}</h2>
    
    <div class="form-fields">
      <div class="form-group">
        <label>设备ID <span class="required">*</span></label>
        <input 
          type="text" 
          v-model="formData.id" 
          placeholder="请输入设备ID" 
          :class="{ 'error': errors.id }"
        />
        <span v-if="errors.id" class="error-message">{{ errors.id }}</span>
      </div>

      <div class="form-group">
        <label>设备位置 <span class="required">*</span></label>
        <input 
          type="text" 
          v-model="formData.location" 
          placeholder="请输入设备所在位置" 
          :class="{ 'error': errors.location }"
        />
        <span v-if="errors.location" class="error-message">{{ errors.location }}</span>
      </div>

      <div class="form-group">
        <label>IP地址 <span class="required">*</span></label>
        <input 
          type="text" 
          v-model="formData.ip_address" 
          placeholder="请输入IP地址（如: 192.168.1.100）" 
          :class="{ 'error': errors.ip_address }"
        />
        <span v-if="errors.ip_address" class="error-message">{{ errors.ip_address }}</span>
      </div>
      
      <div class="form-group">
        <label>设备类型</label>
        <select v-model="formData.device_type">
          <option value="G1_EDU">G1 EDU机器人</option>
          <option value="G1_PRO">G1 PRO机器人</option>
          <option value="OTHER">其他设备</option>
        </select>
      </div>

      <div class="form-group">
        <label>设备描述</label>
        <textarea 
          v-model="formData.description" 
          placeholder="请输入设备描述信息"
          rows="3"
        ></textarea>
      </div>
    </div>
    
    <div class="form-actions">
      <button class="action-btn cancel-btn" @click="$emit('cancel')">取消</button>
      <button class="action-btn submit-btn" @click="handleSubmit">保存</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  equipment: {
    type: Object,
    default: () => ({
      id: '',
      location: '',
      ip_address: '',
      device_type: 'G1_EDU',
      description: ''
    })
  },
  title: {
    type: String,
    default: '添加设备'
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref({
  id: props.equipment?.id || '',
  location: props.equipment?.location || '',
  ip_address: props.equipment?.ip_address || '',
  device_type: props.equipment?.device_type || 'G1_EDU',
  description: props.equipment?.description || ''
})

const errors = ref({})

// 监听 props 变化
watch(() => props.equipment, (newEquipment) => {
  if (newEquipment) {
    formData.value = {
      id: newEquipment.id || '',
      location: newEquipment.location || '',
      ip_address: newEquipment.ip_address || '',
      device_type: newEquipment.device_type || 'G1_EDU',
      description: newEquipment.description || ''
    }
  }
}, { immediate: true })

// IP地址验证
const validateIP = (ip) => {
  const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip)
}

// 表单验证
const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.id.trim()) {
    errors.value.id = '设备ID不能为空'
  } else if (formData.value.id.length < 3) {
    errors.value.id = '设备ID至少需3个字符'
  }
  
  if (!formData.value.location.trim()) {
    errors.value.location = '设备位置不能为空'
  }
  
  if (!formData.value.ip_address.trim()) {
    errors.value.ip_address = 'IP地址不能为空'
  } else if (!validateIP(formData.value.ip_address)) {
    errors.value.ip_address = '请输入正确的IP地址格式'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) {
    return
  }
  
  // 构建提交数据
  const submitData = {
    id: formData.value.id.trim(),
    location: formData.value.location.trim(),
    ip_address: formData.value.ip_address.trim(),
    device_type: formData.value.device_type,
    description: formData.value.description.trim()
  }
  
  emit('submit', submitData)
}
</script>

<style scoped>
.equipment-form {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  width: 100%;
  min-width: 550px;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-top: 0;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.form-fields {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input,
.form-group select {
  height: 40px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #0071e4;
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #ff4d4f;
}

.required {
  color: #ff4d4f;
}

.error-message {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  height: 40px;
  padding: 0 16px;
  margin-left: 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e6e6e6;
}

.submit-btn {
  background-color: #0071e4;
  color: white;
}

.submit-btn:hover {
  background-color: #0062c4;
}
</style> 