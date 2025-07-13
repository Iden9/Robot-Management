<template>
  <button 
    class="action-button" 
    :class="{ primary }"
    @click="$emit('click')"
  >
    <span class="icon" v-if="icon">
      <component :is="icon" />
    </span>
    <span class="text">{{ text }}</span>
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
  primary: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>

<style scoped>
.action-button {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-button:hover {
  background-color: #e6e6e6;
}

.action-button.primary {
  background-color: #0071e4;
  color: white;
}

.action-button.primary:hover {
  background-color: #0062c4;
}

.icon {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.icon svg {
  width: 18px;
  height: 18px;
}
</style> 