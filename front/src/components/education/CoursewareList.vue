<template>
  <div class="courseware-list">
    <div class="list-header">
      <h3>已上传课件</h3>
      <div class="header-actions">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索课件..." 
          class="search-input"
        />
        <select v-model="filterCategory" class="category-filter">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="filteredCourseware.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <p>暂无课件，请先上传</p>
    </div>

    <div v-else class="courseware-grid">
      <div 
        v-for="courseware in filteredCourseware" 
        :key="courseware.id" 
        class="courseware-item"
        @click="$emit('preview', courseware)"
      >
        <div class="courseware-thumbnail">
          <div class="file-icon" :class="getFileTypeClass(courseware.file_type)">
            <component :is="getFileIcon(courseware.file_type)" />
          </div>
          <div class="file-overlay">
            <button class="preview-btn" @click.stop="$emit('preview', courseware)">
              <EyeIcon />
              预览
            </button>
          </div>
        </div>
        
        <div class="courseware-info">
          <h4 class="courseware-title" :title="courseware.title">
            {{ courseware.title }}
          </h4>
          <p class="courseware-meta">
            <span class="file-size">{{ formatFileSize(courseware.file_size) }}</span>
            <span class="upload-date">{{ formatDate(courseware.created_at) }}</span>
          </p>
          <div class="courseware-tags">
            <span v-for="tag in courseware.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="courseware-actions">
          <button 
            class="action-btn preview" 
            @click.stop="$emit('preview', courseware)"
            title="预览"
          >
            <EyeIcon />
          </button>
          <button 
            class="action-btn download" 
            @click.stop="$emit('download', courseware)"
            title="下载"
          >
            <DownloadIcon />
          </button>
          <button 
            class="action-btn delete" 
            @click.stop="$emit('delete', courseware)"
            title="删除"
          >
            <TrashIcon />
          </button>
        </div>
      </div>
    </div>

    <div v-if="pagination.pages > 1" class="pagination">
      <button 
        class="page-btn" 
        :disabled="!pagination.has_prev"
        @click="$emit('page-change', pagination.current_page - 1)"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ pagination.current_page }} 页 / 共 {{ pagination.pages }} 页
      </span>
      
      <button 
        class="page-btn" 
        :disabled="!pagination.has_next"
        @click="$emit('page-change', pagination.current_page + 1)"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

// 图标组件
import EyeIcon from '@/components/education/icons/EyeIcon.vue'
import DownloadIcon from '@/components/education/icons/DownloadIcon.vue'
import TrashIcon from '@/components/education/icons/TrashIcon.vue'
import PdfIcon from '@/components/education/icons/PdfIcon.vue'
import PptIcon from '@/components/education/icons/PptIcon.vue'
import ImageIcon from '@/components/education/icons/ImageIcon.vue'
import FileIcon from '@/components/education/icons/FileIcon.vue'

const props = defineProps({
  courseware: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({
      current_page: 1,
      pages: 1,
      has_prev: false,
      has_next: false
    })
  }
})

const emit = defineEmits(['preview', 'download', 'delete', 'page-change'])

// 搜索和过滤
const searchQuery = ref('')
const filterCategory = ref('')

// 过滤后的课件列表
const filteredCourseware = computed(() => {
  let filtered = props.courseware

  // 按搜索词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.title.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query)) ||
      (item.tags && item.tags.some(tag => tag.toLowerCase().includes(query)))
    )
  }

  // 按分类过滤
  if (filterCategory.value) {
    filtered = filtered.filter(item => item.category_id === filterCategory.value)
  }

  return filtered
})

// 获取文件类型样式类
const getFileTypeClass = (fileType) => {
  if (fileType.includes('pdf')) return 'pdf'
  if (fileType.includes('powerpoint') || fileType.includes('presentation')) return 'ppt'
  if (fileType.includes('image')) return 'image'
  return 'file'
}

// 获取文件图标组件
const getFileIcon = (fileType) => {
  if (fileType.includes('pdf')) return PdfIcon
  if (fileType.includes('powerpoint') || fileType.includes('presentation')) return PptIcon
  if (fileType.includes('image')) return ImageIcon
  return FileIcon
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
.courseware-list {
  margin-top: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 3px rgba(0, 113, 228, 0.1);
}

.category-filter {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #0071e4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.courseware-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.courseware-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
  background: white;
}

.courseware-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.courseware-thumbnail {
  position: relative;
  height: 120px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.file-icon.pdf {
  background: #dc3545;
  color: white;
}

.file-icon.ppt {
  background: #fd7e14;
  color: white;
}

.file-icon.image {
  background: #198754;
  color: white;
}

.file-icon.file {
  background: #6c757d;
  color: white;
}

.file-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.courseware-item:hover .file-overlay {
  opacity: 1;
}

.preview-btn {
  background: #0071e4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background 0.2s;
}

.preview-btn:hover {
  background: #0056b3;
}

.courseware-info {
  padding: 12px;
}

.courseware-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.courseware-meta {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  display: flex;
  justify-content: space-between;
}

.courseware-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  background: #e6f7ff;
  color: #0071e4;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.courseware-actions {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  color: #666;
}

.action-btn:hover {
  background: #e9ecef;
}

.action-btn.preview:hover {
  background: #e6f7ff;
  color: #0071e4;
}

.action-btn.download:hover {
  background: #f0f9ff;
  color: #0ea5e9;
}

.action-btn.delete:hover {
  background: #fef2f2;
  color: #dc2626;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 16px;
}

.page-btn {
  background: #0071e4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #0056b3;
}

.page-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .courseware-grid {
    grid-template-columns: 1fr;
  }
}
</style>