<template>
  <div class="toggle-switch">
    <label class="switch">
      <input type="checkbox" v-model="localChecked" @change="handleChange">
      <span class="slider"></span>
    </label>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  checked: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:checked', 'change'])

const localChecked = ref(props.checked)

watch(() => props.checked, (newVal) => {
  localChecked.value = newVal
})

const handleChange = () => {
  emit('update:checked', localChecked.value)
  emit('change', localChecked.value)
}
</script>

<style scoped>
.switch {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 28px;
}

.switch input {
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
  border-radius: 28px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #52c41a;
}

input:focus + .slider {
  box-shadow: 0 0 1px #52c41a;
}

input:checked + .slider:before {
  transform: translateX(24px);
}
</style> 