<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="import-modal" @click.stop>
      <div class="modal-header">
        <div class="header-left">
          <div class="icon-wrapper">
            <UploadIcon />
          </div>
          <h2>批量导入设备</h2>
        </div>
        <button @click="$emit('close')" class="close-btn">
          <CloseIcon />
        </button>
      </div>

      <div class="modal-body">
        <!-- 步骤指示器 -->
        <div class="steps">
          <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
            <div class="step-number">1</div>
            <span>选择文件</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
            <div class="step-number">2</div>
            <span>上传导入</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 3 }">
            <div class="step-number">3</div>
            <span>导入结果</span>
          </div>
        </div>

        <!-- 步骤1: 文件选择 -->
        <div v-if="currentStep === 1" class="step-content">
          <div class="instructions">
            <h3>导入说明</h3>
            <ul>
              <li>支持Excel (.xlsx) 和 CSV (.csv) 格式</li>
              <li>文件大小不超过 10MB</li>
              <li>必填字段：设备ID、设备位置</li>
              <li>可选字段：IP地址、描述信息</li>
              <li>设备ID必须唯一，重复的设备将被跳过</li>
            </ul>
            
            <div class="template-download">
              <p>建议先下载模板文件，按照格式填写设备信息：</p>
              <button @click="downloadTemplate" class="btn template-btn" :disabled="templateLoading">
                <DownloadIcon class="btn-icon" />
                {{ templateLoading ? '下载中...' : '下载导入模板' }}
              </button>
            </div>
          </div>

          <div class="file-upload">
            <div 
              class="upload-area" 
              :class="{ 'drag-over': isDragOver, 'has-file': selectedFile }"
              @dragover.prevent="handleDragOver"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
              @click="triggerFileSelect"
            >
              <input 
                ref="fileInput" 
                type="file" 
                accept=".xlsx,.xls,.csv" 
                @change="handleFileSelect"
                style="display: none"
              />
              
              <div v-if="!selectedFile" class="upload-placeholder">
                <UploadIcon class="upload-icon" />
                <p class="upload-text">点击选择文件或拖拽文件到此处</p>
                <p class="upload-hint">支持 .xlsx, .xls, .csv 格式</p>
              </div>
              
              <div v-else class="file-preview">
                <div class="file-info">
                  <div class="file-icon">
                    <DocumentIcon />
                  </div>
                  <div class="file-details">
                    <p class="file-name">{{ selectedFile.name }}</p>
                    <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                </div>
                <button @click.stop="removeFile" class="remove-btn">
                  <TrashIcon />
                </button>
              </div>
            </div>
            
            <div v-if="fileError" class="error-message">
              {{ fileError }}
            </div>
          </div>
        </div>

        <!-- 步骤2: 上传进度 -->
        <div v-if="currentStep === 2" class="step-content">
          <div class="upload-progress">
            <div class="progress-info">
              <h3>正在导入设备数据...</h3>
              <p>请耐心等待，不要关闭窗口</p>
            </div>
            
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            
            <div class="progress-text">{{ uploadProgress }}%</div>
          </div>
        </div>

        <!-- 步骤3: 导入结果 -->
        <div v-if="currentStep === 3" class="step-content">
          <div class="import-result">
            <div class="result-header">
              <div class="result-icon" :class="{ success: importResult.success_count > 0, error: importResult.failed_count > 0 }">
                <CheckIcon v-if="importResult.failed_count === 0" />
                <ExclamationIcon v-else />
              </div>
              <h3>导入完成</h3>
            </div>
            
            <div class="result-stats">
              <div class="stat-item success">
                <span class="stat-number">{{ importResult.success_count }}</span>
                <span class="stat-label">成功导入</span>
              </div>
              <div class="stat-item error">
                <span class="stat-number">{{ importResult.failed_count }}</span>
                <span class="stat-label">导入失败</span>
              </div>
              <div class="stat-item total">
                <span class="stat-number">{{ importResult.total_count }}</span>
                <span class="stat-label">总计</span>
              </div>
            </div>
            
            <div v-if="importResult.failed_items && importResult.failed_items.length > 0" class="failed-items">
              <h4>失败详情</h4>
              <div class="failed-list">
                <div v-for="item in importResult.failed_items" :key="item.row" class="failed-item">
                  <span class="row-number">第{{ item.row }}行</span>
                  <span class="error-reason">{{ item.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="btn secondary">
          {{ currentStep === 3 ? '关闭' : '取消' }}
        </button>
        
        <button 
          v-if="currentStep === 1" 
          @click="startImport" 
          :disabled="!selectedFile || importing"
          class="btn primary"
        >
          开始导入
        </button>
        
        <button 
          v-if="currentStep === 3 && importResult.success_count > 0" 
          @click="handleComplete"
          class="btn primary"
        >
          完成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// 图标组件
import UploadIcon from './icons/UploadIcon.vue'
import CloseIcon from './icons/CloseIcon.vue'
import DownloadIcon from './icons/DownloadIcon.vue'
import DocumentIcon from './icons/DocumentIcon.vue'
import TrashIcon from './icons/TrashIcon.vue'
import CheckIcon from './icons/CheckIcon.vue'
import ExclamationIcon from './icons/ExclamationIcon.vue'

// API
import { batchImportEquipment, downloadImportTemplate } from '@/api/equipment'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'success'])

// 状态
const currentStep = ref(1)
const selectedFile = ref(null)
const fileError = ref('')
const isDragOver = ref(false)
const importing = ref(false)
const uploadProgress = ref(0)
const templateLoading = ref(false)

// 导入结果
const importResult = ref({
  success_count: 0,
  failed_count: 0,
  total_count: 0,
  failed_items: []
})

// 文件输入引用
const fileInput = ref(null)

// 方法
const handleOverlayClick = () => {
  if (currentStep.value !== 2) { // 上传中不允许关闭
    emit('close')
  }
}

const triggerFileSelect = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file) => {
  fileError.value = ''
  
  // 检查文件类型
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
    'application/vnd.ms-excel', // .xls
    'text/csv' // .csv
  ]
  
  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx?|csv)$/i)) {
    fileError.value = '不支持的文件格式，请选择 .xlsx, .xls 或 .csv 文件'
    return
  }
  
  // 检查文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    fileError.value = '文件大小不能超过 10MB'
    return
  }
  
  selectedFile.value = file
}

const removeFile = () => {
  selectedFile.value = null
  fileError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const downloadTemplate = async () => {
  try {
    templateLoading.value = true
    const response = await downloadImportTemplate()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '设备导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载模板失败:', error)
    fileError.value = '下载模板失败，请重试'
  } finally {
    templateLoading.value = false
  }
}

const startImport = async () => {
  if (!selectedFile.value) return
  
  try {
    importing.value = true
    currentStep.value = 2
    uploadProgress.value = 0
    
    // 创建FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 20
      }
    }, 200)
    
    // 调用批量导入API
    const response = await batchImportEquipment(formData)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    // 设置导入结果
    if (response.code === 200) {
      importResult.value = response.data
    } else {
      importResult.value = {
        success_count: 0,
        failed_count: 1,
        total_count: 1,
        failed_items: [{ row: 0, error: response.message || '导入失败' }]
      }
    }
    
    // 短暂延迟后显示结果
    setTimeout(() => {
      currentStep.value = 3
    }, 500)
    
  } catch (error) {
    console.error('导入失败:', error)
    clearInterval && clearInterval(progressInterval)
    // 处理错误
    importResult.value = {
      success_count: 0,
      failed_count: 1,
      total_count: 1,
      failed_items: [{ row: 0, error: error.response?.data?.message || error.message || '导入过程中发生错误' }]
    }
    currentStep.value = 3
  } finally {
    importing.value = false
  }
}

const handleComplete = () => {
  emit('success')
  emit('close')
}

// 重置状态
const resetState = () => {
  currentStep.value = 1
  selectedFile.value = null
  fileError.value = ''
  isDragOver.value = false
  importing.value = false
  uploadProgress.value = 0
  importResult.value = {
    success_count: 0,
    failed_count: 0,
    total_count: 0,
    failed_items: []
  }
}

// 监听显示状态
watch(() => props.show, (show) => {
  if (show) {
    resetState()
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

.import-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 90vw;
  max-width: 600px;
  max-height: 90vh;
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
  padding: 20px;
  overflow-y: auto;
}

/* 步骤指示器 */
.steps {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 16px;
  right: -50%;
  width: 100%;
  height: 2px;
  background: #f0f0f0;
  z-index: 1;
}

.step.completed:not(:last-child)::after {
  background: #52c41a;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
}

.step.active .step-number {
  background: #0071e4;
  color: white;
}

.step.completed .step-number {
  background: #52c41a;
  color: white;
}

.step span {
  font-size: 12px;
  color: #999;
}

.step.active span,
.step.completed span {
  color: #333;
  font-weight: 500;
}

/* 步骤内容 */
.step-content {
  min-height: 300px;
}

/* 文件上传步骤 */
.instructions {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.instructions h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.instructions ul {
  margin: 0 0 16px 0;
  padding-left: 16px;
}

.instructions li {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.template-download {
  border-top: 1px solid #e8e8e8;
  padding-top: 16px;
}

.template-download p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #666;
}

.template-btn {
  background: #f5f5f5;
  color: #333;
}

.template-btn:hover {
  background: #e8e8e8;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #0071e4;
  background: #f0f8ff;
}

.upload-area.has-file {
  border-style: solid;
  border-color: #52c41a;
  background: #f6ffed;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: #999;
  margin-bottom: 16px;
}

.upload-text {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.file-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 32px;
  height: 32px;
  color: #0071e4;
}

.file-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.file-size {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.remove-btn {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  color: #ff4d4f;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #ff4d4f;
  color: white;
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

.error-message {
  margin-top: 12px;
  padding: 8px 12px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  color: #ff4d4f;
  font-size: 12px;
}

/* 上传进度 */
.upload-progress {
  text-align: center;
}

.progress-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.progress-info p {
  margin: 0 0 24px 0;
  font-size: 12px;
  color: #999;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: #0071e4;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
}

/* 导入结果 */
.import-result {
  text-align: center;
}

.result-header {
  margin-bottom: 24px;
}

.result-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-icon.success {
  background: #f6ffed;
  color: #52c41a;
}

.result-icon.error {
  background: #fff2f0;
  color: #ff4d4f;
}

.result-icon svg {
  width: 32px;
  height: 32px;
}

.result-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-item.success .stat-number {
  color: #52c41a;
}

.stat-item.error .stat-number {
  color: #ff4d4f;
}

.stat-item.total .stat-number {
  color: #0071e4;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.failed-items {
  text-align: left;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 16px;
}

.failed-items h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #ff4d4f;
}

.failed-list {
  max-height: 150px;
  overflow-y: auto;
}

.failed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #ffebe6;
}

.failed-item:last-child {
  border-bottom: none;
}

.row-number {
  font-size: 12px;
  color: #ff4d4f;
  font-weight: 500;
  white-space: nowrap;
}

.error-reason {
  font-size: 12px;
  color: #ff4d4f;
  flex: 1;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.secondary {
  background: #f5f5f5;
  color: #333;
}

.btn.secondary:hover:not(:disabled) {
  background: #e8e8e8;
}

.btn.primary {
  background: #0071e4;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #0062c4;
}

.btn-icon {
  width: 16px;
  height: 16px;
}
</style>