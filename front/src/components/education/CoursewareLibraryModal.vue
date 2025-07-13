<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="library-modal" @click.stop>
      <div class="modal-header">
        <div class="header-left">
          <div class="icon-wrapper">
            <LibraryIcon />
          </div>
          <h2>课件库</h2>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <SearchIcon class="search-icon" />
            <input 
              v-model="searchKeyword" 
              type="text" 
              placeholder="搜索课件..."
              class="search-input"
              @input="handleSearch"
            />
          </div>
          <button @click="$emit('close')" class="close-btn">
            <CloseIcon />
          </button>
        </div>
      </div>

      <div class="modal-body">
        <!-- 过滤器 -->
        <div class="filters">
          <select v-model="selectedCategory" @change="applyFilters" class="filter-select">
            <option value="">所有分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          
          <select v-model="selectedFileType" @change="applyFilters" class="filter-select">
            <option value="">所有类型</option>
            <option value="pdf">PDF</option>
            <option value="ppt">PPT</option>
            <option value="jpg">图片</option>
            <option value="mp4">视频</option>
          </select>
          
          <div class="results-info">
            共找到 {{ filteredCourseware.length }} 个课件
          </div>
        </div>

        <!-- 课件网格 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="filteredCourseware.length === 0" class="empty-state">
          <DocumentIcon class="empty-icon" />
          <p>暂无课件</p>
        </div>

        <div v-else class="courseware-grid">
          <div 
            v-for="courseware in filteredCourseware" 
            :key="courseware.id"
            class="courseware-card"
            @click="openPreview(courseware)"
          >
            <div class="card-thumbnail">
              <div class="file-icon">
                <component :is="getFileIcon(courseware.file_type)" />
              </div>
              <div class="file-type-badge">{{ courseware.file_type.toUpperCase() }}</div>
              <div class="preview-overlay">
                <EyeIcon class="preview-icon" />
                <span class="preview-text">预览</span>
              </div>
            </div>
            
            <div class="card-content">
              <h4 class="card-title" :title="courseware.title">
                {{ courseware.title }}
              </h4>
              <div class="card-meta">
                <span class="file-size">{{ formatFileSize(courseware.file_size) }}</span>
                <span class="upload-date">{{ formatDate(courseware.created_at) }}</span>
              </div>
              <div class="card-stats">
                <span class="stat-item">
                  <EyeIcon class="stat-icon" />
                  {{ courseware.view_count || 0 }}
                </span>
                <span class="stat-item">
                  <DownloadIcon class="stat-icon" />
                  {{ courseware.download_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 预览模态 -->
      <CoursewarePreviewModal 
        :show="showPreview"
        :courseware="selectedCourseware"
        @close="closePreview"
        @select="handleSelectCourseware"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCoursewareStore } from '@/stores/courseware'
import CoursewarePreviewModal from './CoursewarePreviewModal.vue'

// 图标组件
import LibraryIcon from './icons/LibraryIcon.vue'
import SearchIcon from './icons/SearchIcon.vue'
import CloseIcon from './icons/CloseIcon.vue'
import DocumentIcon from './icons/DocumentIcon.vue'
import EyeIcon from './icons/EyeIcon.vue'
import DownloadIcon from './icons/DownloadIcon.vue'
import PdfIcon from './icons/PdfIcon.vue'
import ImageIcon from './icons/ImageIcon.vue'
import FileIcon from './icons/FileIcon.vue'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'select'])

// Store
const coursewareStore = useCoursewareStore()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedFileType = ref('')
const showPreview = ref(false)
const selectedCourseware = ref(null)

// 计算属性
const categories = computed(() => coursewareStore.categories)
const coursewareList = computed(() => coursewareStore.coursewareList)

const filteredCourseware = computed(() => {
  let filtered = coursewareList.value

  // 搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.title.toLowerCase().includes(keyword) ||
      (item.description && item.description.toLowerCase().includes(keyword))
    )
  }

  // 分类过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(item => item.category_id === parseInt(selectedCategory.value))
  }

  // 文件类型过滤
  if (selectedFileType.value) {
    filtered = filtered.filter(item => item.file_type === selectedFileType.value)
  }

  return filtered
})

// 方法
const handleOverlayClick = () => {
  emit('close')
}

const loadData = async () => {
  try {
    loading.value = true
    await Promise.all([
      coursewareStore.fetchCoursewareList(),
      coursewareStore.fetchCategories()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索是响应式的，不需要额外处理
}

const applyFilters = () => {
  // 过滤器变化时自动更新，不需要额外处理
}

const openPreview = (courseware) => {
  selectedCourseware.value = courseware
  showPreview.value = true
}

const closePreview = () => {
  showPreview.value = false
  selectedCourseware.value = null
}

const handleSelectCourseware = (courseware) => {
  emit('select', courseware)
  emit('close') // 选择后关闭库模态框
}

const getFileIcon = (fileType) => {
  const typeMap = {
    'pdf': PdfIcon,
    'ppt': DocumentIcon,
    'pptx': DocumentIcon,
    'doc': DocumentIcon,
    'docx': DocumentIcon,
    'jpg': ImageIcon,
    'jpeg': ImageIcon,
    'png': ImageIcon,
    'gif': ImageIcon,
    'mp4': FileIcon,
    'mp3': FileIcon
  }
  return typeMap[fileType] || FileIcon
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 监听显示状态
watch(() => props.show, (show) => {
  if (show) {
    loadData()
  }
})

// 组件挂载时加载数据
onMounted(() => {
  if (props.show) {
    loadData()
  }
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
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.library-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 90vw;
  max-width: 1200px;
  height: 80vh;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  background: white;
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.icon-wrapper {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0071e4;
  margin-right: 10px;
}

.modal-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: #999;
  z-index: 1;
}

.search-input {
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 8px 12px 8px 36px;
  color: #333;
  font-size: 14px;
  width: 250px;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: #999;
}

.search-input:focus {
  outline: none;
  border-color: #0071e4;
  background: white;
}

.close-btn {
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e8e8e8;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.filters {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.results-info {
  margin-left: auto;
  color: #6b7280;
  font-size: 14px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.courseware-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.courseware-card {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.courseware-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-color: #0071e4;
}

.card-thumbnail {
  position: relative;
  height: 120px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.file-icon {
  width: 48px;
  height: 48px;
  color: #0071e4;
}

.file-type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #0071e4;
  color: white;
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 113, 228, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.courseware-card:hover .preview-overlay {
  opacity: 1;
}

.preview-icon {
  width: 24px;
  height: 24px;
  color: white;
}

.preview-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.card-content {
  padding: 16px;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 12px;
  color: #6b7280;
}

.card-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.stat-icon {
  width: 12px;
  height: 12px;
}
</style>