<template>
  <div class="setting-card">
    <div class="card-header">
      <div class="title-container">
        <div class="icon-wrapper" :class="iconColor">
          <component :is="icon" />
        </div>
        <h3 class="title">{{ title }}</h3>
      </div>
    </div>
    
    <div class="card-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    required: true
  },
  iconColor: {
    type: String,
    default: 'orange'
  }
})
</script>

<style scoped>
.setting-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fff8eb;
}

.title-container {
  display: flex;
  align-items: center;
}

.icon-wrapper {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.title {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  color: #333;
}

.card-content {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* 图标颜色类 */
.orange {
  color: #faad14;
}

.blue {
  color: #0071e4;
}

.green {
  color: #52c41a;
}

.purple {
  color: #722ed1;
}
</style> 