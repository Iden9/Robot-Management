<template>
  <div 
    class="upload-area"
    @dragover.prevent="dragover = true"
    @dragleave.prevent="dragover = false"
    @drop.prevent="onDrop"
    @click="triggerFileInput"
  >
    <input 
      type="file" 
      ref="fileInput" 
      @change="onFileSelected" 
      accept=".ppt,.pptx,.pdf,.jpg,.jpeg,.png" 
      style="display: none"
    >

    <div class="upload-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="17 8 12 3 7 8"></polyline>
        <line x1="12" y1="3" x2="12" y2="15"></line>
      </svg>
    </div>
    
    <div class="upload-text">
      <p>点击或拖拽放PPT/PDF/图片文件到此处</p>
      <p class="upload-hint">支持PPTX, PDF, JPG, PNG格式</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { defineEmits } from 'vue'

const emit = defineEmits(['file-selected'])

const fileInput = ref(null)
const dragover = ref(false)

const triggerFileInput = () => {
  fileInput.value.click()
}

const onFileSelected = (event) => {
  const files = event.target.files
  if (files && files.length) {
    emit('file-selected', files[0])
  }
}

const onDrop = (event) => {
  dragover.value = false
  const files = event.dataTransfer.files
  if (files && files.length) {
    emit('file-selected', files[0])
  }
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed #e8e8e8;
  border-radius: 8px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #0071e4;
  background-color: rgba(0, 113, 228, 0.02);
}

.upload-icon {
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
  color: #666;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
</style> 