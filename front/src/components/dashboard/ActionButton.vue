<template>
  <button class="action-button" :class="{ primary: type === 'primary' }" @click="$emit('click')">
    <component :is="icon" class="button-icon" v-if="icon" />
    <span class="button-text">{{ text }}</span>
  </button>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  text: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    default: null
  },
  type: {
    type: String,
    default: 'default' // 'default' 或 'primary'
  }
})

defineEmits(['click'])
</script>

<style scoped>
.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  border: 1px solid #e8e8e8;
  background-color: #fff;
  color: #333;
}

.action-button:hover {
  background-color: #f5f5f5;
}

.primary {
  background-color: #0071e4;
  color: white;
  border: 1px solid #0071e4;
}

.primary:hover {
  background-color: #0062c4;
  border-color: #0062c4;
}

.button-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

.button-text {
  white-space: nowrap;
}
</style> 