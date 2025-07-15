<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEdit ? '编辑知识库' : (knowledge ? '查看知识库' : '新增知识库') }}</h3>
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
              placeholder="请输入知识库标题"
              :disabled="!isEdit && knowledge"
              required
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <select 
                v-model="form.category"
                class="form-control"
                :disabled="!isEdit && knowledge"
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
                :disabled="!isEdit && knowledge"
              >
                <option value="text">文本</option>
                <option value="document">文档</option>
                <option value="link">链接</option>
                <option value="faq">FAQ</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="form.description"
              class="form-control"
              rows="3"
              placeholder="请输入知识库描述"
              :disabled="!isEdit && knowledge"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>内容 <span class="required">*</span></label>
            <textarea 
              v-model="form.content"
              class="form-control content-textarea"
              rows="10"
              placeholder="请输入知识库内容"
              :disabled="!isEdit && knowledge"
              required
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <div class="tag-item" v-for="(tag, index) in form.tags" :key="index">
                {{ tag }}
                <button 
                  v-if="isEdit || !knowledge"
                  type="button" 
                  class="tag-remove"
                  @click="removeTag(index)"
                >
                  ×
                </button>
              </div>
              <input 
                v-if="isEdit || !knowledge"
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
              <label>状态</label>
              <select 
                v-model="form.status"
                class="form-control"
                :disabled="!isEdit && knowledge"
              >
                <option value="draft">草稿</option>
                <option value="published">已发布</option>
                <option value="archived">已归档</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>优先级</label>
              <input 
                v-model.number="form.priority"
                type="number"
                class="form-control"
                min="0"
                max="100"
                :disabled="!isEdit && knowledge"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>来源链接</label>
            <input 
              v-model="form.source_url"
              type="url"
              class="form-control"
              placeholder="请输入来源链接"
              :disabled="!isEdit && knowledge"
            />
          </div>
          
          <div class="form-group">
            <label>
              <input 
                v-model="form.is_public"
                type="checkbox"
                :disabled="!isEdit && knowledge"
              />
              公开显示
            </label>
          </div>
          
          <div v-if="knowledge && !isEdit" class="knowledge-stats">
            <div class="stat-item">
              <strong>查看次数:</strong> {{ knowledge.view_count }}
            </div>
            <div class="stat-item">
              <strong>使用次数:</strong> {{ knowledge.usage_count }}
            </div>
            <div class="stat-item">
              <strong>创建时间:</strong> {{ formatDate(knowledge.created_at) }}
            </div>
            <div class="stat-item">
              <strong>更新时间:</strong> {{ formatDate(knowledge.updated_at) }}
            </div>
            <div class="stat-item">
              <strong>创建者:</strong> {{ knowledge.creator_name }}
            </div>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="closeModal">
          取消
        </button>
        <button 
          v-if="isEdit || !knowledge"
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
import { createKnowledge, updateKnowledge, getKnowledgeCategories } from '@/api/knowledge'
import { success as showSuccess, error as showError } from '@/utils/alert'
import { formatDate } from '@/utils/date'
import CloseIcon from '@/components/common/icons/CloseIcon.vue'

const props = defineProps({
  knowledge: {
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
  type: 'text',
  status: 'published',
  priority: 0,
  is_public: true,
  source_url: '',
  tags: []
})

// 监听知识库数据变化
watch(() => props.knowledge, (newValue) => {
  if (newValue) {
    form.title = newValue.title || ''
    form.content = newValue.content || ''
    form.description = newValue.description || ''
    form.category = newValue.category || ''
    form.type = newValue.type || 'text'
    form.status = newValue.status || 'published'
    form.priority = newValue.priority || 0
    form.is_public = newValue.is_public !== undefined ? newValue.is_public : true
    form.source_url = newValue.source_url || ''
    form.tags = newValue.tags || []
  } else {
    // 重置表单
    form.title = ''
    form.content = ''
    form.description = ''
    form.category = ''
    form.type = 'text'
    form.status = 'published'
    form.priority = 0
    form.is_public = true
    form.source_url = ''
    form.tags = []
  }
}, { immediate: true })

// 获取分类列表
const loadCategories = async () => {
  try {
    const response = await getKnowledgeCategories()
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
      source_url: form.source_url,
      tags: form.tags
    }
    
    let response
    if (props.knowledge && props.isEdit) {
      response = await updateKnowledge(props.knowledge.id, data)
    } else {
      response = await createKnowledge(data)
    }
    
    if (response.success) {
      showSuccess(props.knowledge && props.isEdit ? '更新成功' : '创建成功')
      emit('save')
    }
  } catch (error) {
    showError(props.knowledge && props.isEdit ? '更新失败' : '创建失败')
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
  max-width: 800px;
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

.knowledge-stats {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.stat-item {
  margin-bottom: 8px;
  font-size: 14px;
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
</style>