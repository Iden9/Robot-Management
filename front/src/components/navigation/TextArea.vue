<template>
  <div class="text-area">
    <textarea 
      class="text-area-input" 
      :placeholder="placeholder"
      :rows="rows"
      v-model="localValue"
      @input="handleInput"
    ></textarea>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  rows: {
    type: [Number, String],
    default: 4
  }
})

const emit = defineEmits(['update:modelValue', 'input'])

const localValue = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  localValue.value = newVal
})

const handleInput = (event) => {
  emit('update:modelValue', localValue.value)
  emit('input', event)
}
</script>

<style scoped>
.text-area {
  width: 100%;
}

.text-area-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  transition: all 0.3s;
  color: #333;
}

.text-area-input:focus {
  outline: none;
  border-color: #faad14;
  box-shadow: 0 0 0 2px rgba(250, 173, 20, 0.1);
}

.text-area-input::placeholder {
  color: #bfbfbf;
}
</style> 