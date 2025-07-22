<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEdit ? '编辑提示词' : (prompt ? '查看提示词' : '新增提示词') }}</h3>
        <button class="close-btn" @click="closeModal">
          <CloseIcon />
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>标题 <span class="required">*</span></label>
            <input 
              v-model="form.title"
              type="text"
              class="form-control"
              placeholder="请输入提示词标题"
              :disabled="!isEdit && prompt"
              required
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <select 
                v-model="form.category"
                class="form-control"
                :disabled="!isEdit && prompt"
              >
                <option value="">选择分类</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>类型</label>
              <select 
                v-model="form.type"
                class="form-control"
                :disabled="!isEdit && prompt"
              >
                <option value="system">系统提示词</option>
                <option value="user">用户提示词</option>
                <option value="assistant">助手提示词</option>
                <option value="general">通用提示词</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="form.description"
              class="form-control"
              rows="3"
              placeholder="请输入提示词描述"
              :disabled="!isEdit && prompt"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>提示词内容 <span class="required">*</span></label>
            <textarea 
              v-model="form.content"
              class="form-control content-textarea"
              rows="10"
              placeholder="请输入提示词内容"
              :disabled="!isEdit && prompt"
              required
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>变量定义 (JSON格式)</label>
            <textarea 
              v-model="form.variables"
              class="form-control"
              rows="4"
              placeholder='例如: {"name": "用户名", "age": "年龄"}'
              :disabled="!isEdit && prompt"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>示例输入</label>
              <textarea 
                v-model="form.example_input"
                class="form-control"
                rows="3"
                placeholder="请输入示例输入"
                :disabled="!isEdit && prompt"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>示例输出</label>
              <textarea 
                v-model="form.example_output"
                class="form-control"
                rows="3"
                placeholder="请输入示例输出"
                :disabled="!isEdit && prompt"
              ></textarea>
            </div>
          </div>
          
          <div class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <div class="tag-item" v-for="(tag, index) in form.tags" :key="index">
                {{ tag }}
                <button 
                  v-if="isEdit || !prompt"
                  type="button" 
                  class="tag-remove"
                  @click="removeTag(index)"
                >
                  ×
                </button>
              </div>
              <input 
                v-if="isEdit || !prompt"
                v-model="newTag"
                type="text"
                class="tag-input"
                placeholder="输入标签后按回车添加"
                @keyup.enter="addTag"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>模型类型</label>
              <input 
                v-model="form.model_type"
                type="text"
                class="form-control"
                placeholder="例如: GPT-4, Claude"
                :disabled="!isEdit && prompt"
              />
            </div>
            
            <div class="form-group">
              <label>温度参数</label>
              <input 
                v-model.number="form.temperature"
                type="number"
                class="form-control"
                min="0"
                max="2"
                step="0.1"
                :disabled="!isEdit && prompt"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>最大Token数</label>
              <input 
                v-model.number="form.max_tokens"
                type="number"
                class="form-control"
                min="1"
                :disabled="!isEdit && prompt"
              />
            </div>
            
            <div class="form-group">
              <label>优先级</label>
              <input 
                v-model.number="form.priority"
                type="number"
                class="form-control"
                min="0"
                max="100"
                :disabled="!isEdit && prompt"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>状态</label>
              <select 
                v-model="form.status"
                class="form-control"
                :disabled="!isEdit && prompt"
              >
                <option value="draft">草稿</option>
                <option value="published">已发布</option>
                <option value="archived">已归档</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>
                <input 
                  v-model="form.is_public"
                  type="checkbox"
                  :disabled="!isEdit && prompt"
                />
                公开显示
              </label>
            </div>
          </div>
          
          <div v-if="prompt && !isEdit" class="prompt-stats">
            <div class="stat-item">
              <strong>查看次数:</strong> {{ prompt.view_count }}
            </div>
            <div class="stat-item">
              <strong>使用次数:</strong> {{ prompt.usage_count }}
            </div>
            <div class="stat-item">
              <strong>创建时间:</strong> {{ formatDate(prompt.created_at) }}
            </div>
            <div class="stat-item">
              <strong>更新时间:</strong> {{ formatDate(prompt.updated_at) }}
            </div>
            <div class="stat-item">
              <strong>创建者:</strong> {{ prompt.creator_name }}
            </div>
          </div>
          
          <div v-if="prompt && !isEdit" class="prompt-actions">
            <button 
              type="button" 
              class="btn btn-success"
              @click="copyContent"
            >
              复制内容
            </button>
            <button 
              type="button" 
              class="btn btn-info"
              @click="recordUsage"
            >
              记录使用
            </button>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="closeModal">
          取消
        </button>
        <button 
          v-if="isEdit || !prompt"
          type="button" 
          class="btn btn-primary"
          @click="handleSubmit"
          :disabled="saving"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { createPrompt, updatePrompt, getPromptCategories, recordPromptUsage } from '@/api/prompt'
import { success as showSuccess, error as showError } from '@/utils/alert'
import { formatDate } from '@/utils/date'
import CloseIcon from '@/components/common/icons/CloseIcon.vue'

const props = defineProps({
  prompt: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

// 响应式数据
const saving = ref(false)
const newTag = ref('')
const categories = ref([])

// 表单数据
const form = reactive({
  title: '',
  content: '',
  description: '',
  category: '',
  type: 'general',
  status: 'published',
  priority: 0,
  is_public: true,
  variables: '',
  example_input: '',
  example_output: '',
  model_type: '',
  temperature: 0.7,
  max_tokens: null,
  tags: []
})

// 监听提示词数据变化
watch(() => props.prompt, (newValue) => {
  if (newValue) {
    form.title = newValue.title || ''
    form.content = newValue.content || ''
    form.description = newValue.description || ''
    form.category = newValue.category || ''
    form.type = newValue.type || 'general'
    form.status = newValue.status || 'published'
    form.priority = newValue.priority || 0
    form.is_public = newValue.is_public !== undefined ? newValue.is_public : true
    form.variables = newValue.variables || ''
    form.example_input = newValue.example_input || ''
    form.example_output = newValue.example_output || ''
    form.model_type = newValue.model_type || ''
    form.temperature = newValue.temperature || 0.7
    form.max_tokens = newValue.max_tokens || null
    form.tags = newValue.tags || []
  } else {
    // 重置表单
    form.title = ''
    form.content = ''
    form.description = ''
    form.category = ''
    form.type = 'general'
    form.status = 'published'
    form.priority = 0
    form.is_public = true
    form.variables = ''
    form.example_input = ''
    form.example_output = ''
    form.model_type = ''
    form.temperature = 0.7
    form.max_tokens = null
    form.tags = []
  }
}, { immediate: true })

// 获取分类列表
const loadCategories = async () => {
  try {
    const response = await getPromptCategories()
    if (response.success) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 添加标签
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
    newTag.value = ''
  }
}

// 删除标签
const removeTag = (index) => {
  form.tags.splice(index, 1)
}

// 复制内容
const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(props.prompt.content)
    showSuccess('内容已复制到剪贴板')
  } catch (error) {
    showError('复制失败')
  }
}

// 记录使用
const recordUsage = async () => {
  try {
    await recordPromptUsage(props.prompt.id)
    showSuccess('使用记录成功')
    emit('save')
  } catch (error) {
    showError('记录失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!form.title.trim()) {
    showError('请输入标题')
    return
  }
  
  if (!form.content.trim()) {
    showError('请输入内容')
    return
  }
  
  // 验证JSON格式
  if (form.variables && form.variables.trim()) {
    try {
      JSON.parse(form.variables)
    } catch (error) {
      showError('变量定义格式错误，请使用正确的JSON格式')
      return
    }
  }
  
  try {
    saving.value = true
    
    const data = {
      title: form.title,
      content: form.content,
      description: form.description,
      category: form.category,
      type: form.type,
      status: form.status,
      priority: form.priority,
      is_public: form.is_public,
      variables: form.variables,
      example_input: form.example_input,
      example_output: form.example_output,
      model_type: form.model_type,
      temperature: form.temperature,
      max_tokens: form.max_tokens,
      tags: form.tags
    }
    
    let response
    if (props.prompt && props.isEdit) {
      response = await updatePrompt(props.prompt.id, data)
    } else {
      response = await createPrompt(data)
    }
    
    console.log('API Response:', response)
    
    // API成功返回时，response就是包含code=200的对象
    // 失败时会在catch块中处理
    emit('save', response)
  } catch (error) {
    showError(error.message || (props.prompt && props.isEdit ? '更新失败' : '创建失败'))
  } finally {
    saving.value = false
  }
}

// 关闭模态框
const closeModal = () => {
  emit('close')
}

// 页面加载
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 24px;
  height: 24px;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #0071e4;
}

.content-textarea {
  min-height: 200px;
  resize: vertical;
  font-family: monospace;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 40px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  background: #e3f2fd;
  border-radius: 4px;
  font-size: 12px;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
}

.tag-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  min-width: 100px;
}

.prompt-stats {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.stat-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.prompt-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-primary {
  background: #0071e4;
  color: white;
}

.btn-primary:hover {
  background: #005bb5;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover {
  background: #138496;
}
</style>