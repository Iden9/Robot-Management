<template>
  <button 
    class="action-button" 
    :class="[
      type, 
      { 'has-icon': !!icon }
    ]"
    @click="$emit('click')"
  >
    <component v-if="icon" :is="icon" class="button-icon" />
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
  type: {
    type: String,
    default: 'primary'  // 'primary', 'secondary'
  },
  icon: {
    type: Object,
    default: null
  }
})

defineEmits(['click'])
</script>

<style scoped>
.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  height: 40px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.primary {
  background-color: #0071e4;
  color: white;
}

.primary:hover {
  background-color: #0062c4;
}

.secondary {
  background-color: #f5f5f5;
  color: #333;
}

.secondary:hover {
  background-color: #e8e8e8;
}

.button-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
}
</style> 