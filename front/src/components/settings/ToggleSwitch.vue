<template>
  <label class="toggle-switch">
    <input 
      type="checkbox" 
      :checked="checked" 
      @change="$emit('update:checked', $event.target.checked)"
    />
    <span class="slider"></span>
  </label>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  checked: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:checked'])
</script>

<style scoped>
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #0071e4;
}

input:focus + .slider {
  box-shadow: 0 0 1px #0071e4;
}

input:checked + .slider:before {
  transform: translateX(20px);
}
</style> 