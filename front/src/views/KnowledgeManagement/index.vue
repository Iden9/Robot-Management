<template>
  <div class="knowledge-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>知识库管理</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCreateModal">
          <PlusIcon /> 新增知识库
        </button>
      </div>
    </div>

    <!-- 搜索和过滤 -->
    <div class="search-filters">
      <div class="search-bar">
        <input
          v-model="searchForm.keyword"
          type="text"
          placeholder="搜索知识库..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <SearchIcon />
        </button>
      </div>
      
      <div class="filters">
        <select v-model="searchForm.category" @change="handleSearch">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        
        <select v-model="searchForm.status" @change="handleSearch">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
        
        <select v-model="searchForm.type" @change="handleSearch">
          <option value="">全部类型</option>
          <option value="text">文本</option>
          <option value="document">文档</option>
          <option value="link">链接</option>
          <option value="faq">FAQ</option>
        </select>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="knowledge-list">
      <div class="list-header">
        <span>共 {{ pagination.total }} 条记录</span>
        <div class="view-controls">
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
          >
            <GridIcon />
          </button>
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            <ListIcon />
          </button>
        </div>
      </div>
      <div :class="['knowledge-items', viewMode]">
        <div 
          v-for="item in knowledgeList" 
          :key="item.id" 
          class="knowledge-item"
        >
          <div class="item-header">
            <h3 class="item-title" @click="viewKnowledge(item)">{{ item.title }}</h3>
            <div class="item-actions">
              <button class="action-btn" @click="viewKnowledge(item)">
                <EyeIcon />
              </button>
              <button class="action-btn" @click="editKnowledge(item)">
                <EditIcon />
              </button>
              <button class="action-btn danger" @click="deleteKnowledge(item)">
                <TrashIcon />
              </button>
            </div>
          </div>
          
          <div class="item-content">
            <p class="item-description">{{ item.description || '暂无描述' }}</p>
            <div class="item-meta">
              <span class="meta-item">
                <span class="meta-label">分类:</span>
                <span class="meta-value">{{ item.category || '未分类' }}</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">类型:</span>
                <span class="meta-value">{{ getTypeLabel(item.type) }}</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">状态:</span>
                <span class="meta-value" :class="getStatusClass(item.status)">
                  {{ getStatusLabel(item.status) }}
                </span>
              </span>
            </div>
            
            <div class="item-stats">
              <span class="stat-item">
                <EyeIcon class="stat-icon" />
                {{ item.view_count }}
              </span>
              <span class="stat-item">
                <UsageIcon class="stat-icon" />
                {{ item.usage_count }}
              </span>
              <span class="stat-item">
                <TimeIcon class="stat-icon" />
                {{ formatDate(item.created_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button 
          class="page-btn" 
          :disabled="pagination.page <= 1"
          @click="changePage(pagination.page - 1)"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ pagination.page }} 页 / 共 {{ pagination.pages }} 页
        </span>
        
        <button 
          class="page-btn" 
          :disabled="pagination.page >= pagination.pages"
          @click="changePage(pagination.page + 1)"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 知识库详情模态框 -->
    <KnowledgeModal
      v-if="showModal"
      :knowledge="selectedKnowledge"
      :is-edit="isEdit"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { 
  getKnowledgeList, 
  deleteKnowledge as deleteKnowledgeApi,
  getKnowledgeCategories 
} from '@/api/knowledge'
import { success as showSuccess, error as showError, confirm } from '@/utils/alert'
import { formatDate } from '@/utils/date'
import KnowledgeModal from './components/KnowledgeModal.vue'
import PlusIcon from '@/components/common/icons/PlusIcon.vue'
import SearchIcon from '@/components/common/icons/SearchIcon.vue'
import GridIcon from '@/components/common/icons/GridIcon.vue'
import ListIcon from '@/components/common/icons/ListIcon.vue'
import EyeIcon from '@/components/common/icons/EyeIcon.vue'
import EditIcon from '@/components/common/icons/EditIcon.vue'
import TrashIcon from '@/components/common/icons/TrashIcon.vue'
import UsageIcon from '@/components/common/icons/UsageIcon.vue'
import TimeIcon from '@/components/common/icons/TimeIcon.vue'

// 响应式数据
const knowledgeList = ref([])
const categories = ref([])
const viewMode = ref('grid')
const showModal = ref(false)
const selectedKnowledge = ref(null)
const isEdit = ref(false)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
  type: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

// 获取知识库列表
const loadKnowledgeList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    
    const response = await getKnowledgeList(params)
    
    if (response.message === 'success') {
      knowledgeList.value = response.data.items
      pagination.total = response.data.total
      pagination.pages = response.data.pages
    }
  } catch (error) {
    showError('获取知识库列表失败')
  } finally {
    loading.value = false
  }
}

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

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  loadKnowledgeList()
}

// 分页处理
const changePage = (page) => {
  pagination.page = page
  loadKnowledgeList()
}

// 显示创建模态框
const showCreateModal = () => {
  selectedKnowledge.value = null
  isEdit.value = false
  showModal.value = true
}

// 查看知识库
const viewKnowledge = (knowledge) => {
  selectedKnowledge.value = knowledge
  isEdit.value = false
  showModal.value = true
}

// 编辑知识库
const editKnowledge = (knowledge) => {
  selectedKnowledge.value = knowledge
  isEdit.value = true
  showModal.value = true
}

// 删除知识库
const deleteKnowledge = async (knowledge) => {
  try {
    // 使用confirm方法进行确认
    const confirmed = await confirm(`确定要删除知识库"${knowledge.title}"吗？`, {
      title: '确认删除'
    });
    
    if (!confirmed) {
      return;
    }
    
    const response = await deleteKnowledgeApi(knowledge.id);
    
    // 根据response.code判断操作是否成功
    if (response && response.code === 200) {
      showSuccess(response.message || '删除成功');
      loadKnowledgeList();
    } else {
      showError(response?.message || '删除失败');
    }
  } catch (error) {
    showError(error.message || '删除失败');
    console.error('删除知识库失败:', error);
  }
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  selectedKnowledge.value = null
}

// 保存处理
const handleSave = (result) => {
  console.log('父组件收到保存结果:', result);
  
  // 正确检查API响应结构
  if (result && result.code === 200) {
    showSuccess(result.message || '知识库保存成功')
  } else if (result && result.success) {
    // 兼容使用success字段的API
    showSuccess(result.message || '知识库保存成功')
  }
  loadKnowledgeList()
  closeModal()
}

// 工具函数
const getTypeLabel = (type) => {
  const types = {
    text: '文本',
    document: '文档',
    link: '链接',
    faq: 'FAQ'
  }
  return types[type] || type
}

const getStatusLabel = (status) => {
  const statuses = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return statuses[status] || status
}

const getStatusClass = (status) => {
  return `status-${status}`
}

// 页面加载
onMounted(() => {
  loadKnowledgeList()
  loadCategories()
})
</script>

<style scoped>
.knowledge-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background-color: #0071e4;
  color: white;
}

.btn-primary:hover {
  background-color: #005bb5;
}

.search-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.search-bar {
  display: flex;
  flex: 1;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn {
  padding: 8px 12px;
  background: #0071e4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.filters {
  display: flex;
  gap: 10px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.knowledge-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 6px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.view-btn.active {
  background: #0071e4;
  color: white;
}

.knowledge-items {
  padding: 20px;
}

.knowledge-items.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.knowledge-items.list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.knowledge-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  transition: box-shadow 0.3s;
}

.knowledge-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.item-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  flex: 1;
}

.item-title:hover {
  color: #0071e4;
}

.item-actions {
  display: flex;
  gap: 5px;
}

.action-btn {
  padding: 4px;
  border: none;
  background: none;
  cursor: pointer;
  color: #666;
}

.action-btn:hover {
  color: #0071e4;
}

.action-btn.danger:hover {
  color: #e74c3c;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-description {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
}

.meta-item {
  display: flex;
  gap: 5px;
}

.meta-label {
  color: #999;
}

.meta-value {
  color: #333;
}

.status-draft {
  color: #f39c12;
}

.status-published {
  color: #27ae60;
}

.status-archived {
  color: #95a5a6;
}

.item-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 3px;
}

.stat-icon {
  width: 14px;
  height: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>