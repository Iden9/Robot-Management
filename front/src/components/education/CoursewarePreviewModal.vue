<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="modal-title">
          <h3>{{ courseware?.title || '课件预览' }}</h3>
          <div class="file-info">
            <span class="file-type">{{ getFileTypeText(courseware?.file_type) }}</span>
            <span class="file-size">{{ formatFileSize(courseware?.file_size) }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button @click="$emit('select', courseware)" class="select-btn">
            <CheckIcon class="select-icon" />
            选择此课件
          </button>
          <button @click="$emit('close')" class="close-btn">
            <CloseIcon />
          </button>
        </div>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载预览中...</p>
        </div>

        <div v-else-if="error" class="error-container">
          <div class="error-icon">❌</div>
          <p>{{ error }}</p>
          <button class="retry-btn" @click="loadPreview">重试</button>
        </div>

        <div v-else class="preview-container">
          <!-- PDF 预览 -->
          <div v-if="isPdf" class="pdf-preview">
            <iframe 
              :src="previewUrl" 
              class="pdf-iframe"
              frameborder="0"
              scrolling="auto"
              allowfullscreen
              referrerpolicy="no-referrer-when-downgrade"
            ></iframe>
          </div>

          <!-- 图片预览 -->
          <div v-else-if="isImage" class="image-preview">
            <img 
              :src="previewUrl" 
              :alt="courseware?.title"
              class="preview-image"
              @load="handleImageLoad"
              @error="handleImageError"
            />
          </div>

          <!-- PPT 预览（使用图片或PDF格式） -->
          <div v-else-if="isPpt" class="ppt-preview">
            <div v-if="pptPages.length > 0" class="ppt-viewer">
              <div class="ppt-navigation">
                <button 
                  class="nav-btn" 
                  :disabled="currentPage === 0"
                  @click="currentPage = Math.max(0, currentPage - 1)"
                >
                  上一页
                </button>
                <span class="page-info">
                  {{ currentPage + 1 }} / {{ pptPages.length }}
                </span>
                <button 
                  class="nav-btn" 
                  :disabled="currentPage === pptPages.length - 1"
                  @click="currentPage = Math.min(pptPages.length - 1, currentPage + 1)"
                >
                  下一页
                </button>
              </div>
              <div class="ppt-slide">
                <img 
                  :src="pptPages[currentPage]" 
                  :alt="`第 ${currentPage + 1} 页`"
                  class="slide-image"
                />
              </div>
            </div>
            <div v-else class="ppt-fallback">
              <div class="fallback-icon">📄</div>
              <p>PPT 文件预览功能开发中</p>
              <p class="fallback-hint">您可以下载文件查看完整内容</p>
            </div>
          </div>

          <!-- 不支持的文件类型 -->
          <div v-else class="unsupported-preview">
            <div class="unsupported-icon">📁</div>
            <p>不支持该文件类型的在线预览</p>
            <p class="unsupported-hint">文件类型：{{ courseware?.file_type }}</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div class="courseware-meta">
          <div class="meta-item">
            <span class="meta-label">上传时间：</span>
            <span class="meta-value">{{ formatDate(courseware?.created_at) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">文件大小：</span>
            <span class="meta-value">{{ formatFileSize(courseware?.file_size) }}</span>
          </div>
          <div v-if="courseware?.tags?.length" class="meta-item">
            <span class="meta-label">标签：</span>
            <div class="tags">
              <span v-for="tag in courseware.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>

        <div class="footer-actions">
          <button class="btn btn-secondary" @click="$emit('download', courseware)">
            <DownloadIcon />
            下载
          </button>
          <button class="btn btn-primary" @click="$emit('use', courseware)">
            使用此课件
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import { useCoursewareStore } from '@/stores/courseware'

// 图标组件
import CloseIcon from '@/components/education/icons/CloseIcon.vue'
import DownloadIcon from '@/components/education/icons/DownloadIcon.vue'
import CheckIcon from '@/components/education/icons/CheckIcon.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  courseware: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'select'])

const coursewareStore = useCoursewareStore()

// 状态
const loading = ref(false)
const error = ref('')
const previewUrl = ref('')
const pptPages = ref([])
const currentPage = ref(0)

// 重置预览状态
const resetPreview = () => {
  loading.value = false
  error.value = ''
  previewUrl.value = ''
  pptPages.value = []
  currentPage.value = 0
}

// 加载预览
const loadPreview = async () => {
  if (!props.courseware) return

  try {
    loading.value = true
    error.value = ''
    
    // 对于可直接预览的文件类型，直接构建预览URL
    const previewableTypes = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3']
    
    if (previewableTypes.includes(props.courseware.file_type?.toLowerCase())) {
      // 直接构建带token的预览URL
      const token = localStorage.getItem('token')
      previewUrl.value = `/api/courseware/${props.courseware.id}/preview?token=${token}`
    } else {
      // 对于不支持直接预览的文件，调用API获取预览信息
      const result = await coursewareStore.previewCoursewareAction(props.courseware.id)
      
      if (result.success) {
        if (result.data.preview_url) {
          previewUrl.value = result.data.preview_url
        } else if (result.data.pages) {
          // PPT 分页预览
          pptPages.value = result.data.pages
          currentPage.value = 0
        } else if (result.data.preview_type === 'info') {
          // 显示文件信息而不是预览
          error.value = result.data.message || '该文件类型不支持在线预览'
        }
      } else {
        error.value = result.message || '预览加载失败'
      }
    }
  } catch (err) {
    console.error('预览加载失败:', err)
    error.value = '预览加载失败，请重试'
  } finally {
    loading.value = false
  }
}

// 计算属性
const isPdf = computed(() => {
  return props.courseware?.file_type?.toLowerCase() === 'pdf'
})

const isImage = computed(() => {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
  return imageTypes.includes(props.courseware?.file_type?.toLowerCase())
})

const isPpt = computed(() => {
  const pptTypes = ['ppt', 'pptx']
  return pptTypes.includes(props.courseware?.file_type?.toLowerCase())
})

// 监听课件变化，加载预览
watch(() => [props.show, props.courseware], ([show, courseware]) => {
  if (show && courseware) {
    loadPreview()
  } else {
    resetPreview()
  }
}, { immediate: true })

// 处理遮罩点击
const handleOverlayClick = () => {
  emit('close')
}

// 处理图片加载
const handleImageLoad = () => {
  loading.value = false
}

// 处理图片错误
const handleImageError = () => {
  error.value = '图片加载失败'
}

// 获取文件类型文本
const getFileTypeText = (fileType) => {
  if (!fileType) return '未知类型'
  if (fileType.includes('pdf')) return 'PDF 文档'
  if (fileType.includes('powerpoint') || fileType.includes('presentation')) return 'PowerPoint 演示文稿'
  if (fileType.includes('image')) return '图片文件'
  return fileType
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
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 90vw;
  max-width: 1000px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.file-info {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.file-type {
  background: #e6f7ff;
  color: #0071e4;
  padding: 2px 6px;
  border-radius: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.select-btn {
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.select-btn:hover {
  background: #389e0d;
}

.select-icon {
  width: 16px;
  height: 16px;
}

.close-btn {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0071e4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  background: #0071e4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}

.preview-container {
  height: 100%;
  overflow: auto;
}

.pdf-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  position: relative;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  min-height: 600px;
  background: white;
  flex: 1;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.image-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ppt-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ppt-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.nav-btn {
  background: #0071e4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: #0056b3;
}

.nav-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.ppt-slide {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
}

.slide-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ppt-fallback,
.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  color: #6b7280;
}

.fallback-icon,
.unsupported-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.fallback-hint,
.unsupported-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.courseware-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.meta-label {
  color: #6b7280;
  font-weight: 500;
}

.meta-value {
  color: #374151;
}

.tags {
  display: flex;
  gap: 4px;
}

.tag {
  background: #e6f7ff;
  color: #0071e4;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.footer-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary {
  background: #0071e4;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .modal-container {
    width: 95vw;
    height: 95vh;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-title h3 {
    font-size: 16px;
  }

  .courseware-meta {
    flex-direction: column;
    gap: 8px;
  }

  .footer-actions {
    flex-direction: column;
  }

  .btn {
    justify-content: center;
  }
}
</style>