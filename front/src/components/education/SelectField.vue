<template>
  <div class="select-field">
    <label v-if="label" class="field-label">{{ label }}</label>
    <div class="select-wrapper">
      <select class="select-control" v-model="selected" @change="handleChange">
        <option v-for="option in options" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <div class="select-arrow">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selected = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  selected.value = newValue
})

const handleChange = () => {
  emit('update:modelValue', selected.value)
  emit('change', selected.value)
}
</script>

<style scoped>
.select-field {
  margin-bottom: 16px;
  width: 100%;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.select-wrapper {
  position: relative;
}

.select-control {
  width: 100%;
  height: 40px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 0 12px;
  appearance: none;
  background-color: #fff;
  transition: all 0.3s;
  color: #333;
  font-size: 14px;
}

.select-control:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 2px rgba(0, 113, 228, 0.1);
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #999;
}
</style> 