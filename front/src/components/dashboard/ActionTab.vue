<template>
  <div class="action-tab">
    <div class="action-header">
      <div class="title">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="menu-icon">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <span>{{ title }}</span>
      </div>
    </div>
    
    <div class="action-buttons">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  title: {
    type: String,
    default: '快捷操作'
  }
})
</script>

<style scoped>
.action-tab {
  margin-top: 24px;
  margin-bottom: 16px;
}

.action-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.menu-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
</style> 