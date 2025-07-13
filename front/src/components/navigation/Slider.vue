<template>
  <div class="slider-container">
    <input 
      type="range" 
      class="slider" 
      :min="min" 
      :max="max" 
      :step="step" 
      v-model="localValue"
      @input="handleInput"
    />
    <div class="slider-track">
      <div class="slider-track-fill" :style="{ width: progress + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: 50
  },
  min: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 100
  },
  step: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localValue = ref(Number(props.modelValue))

watch(() => props.modelValue, (newVal) => {
  localValue.value = Number(newVal)
})

const progress = computed(() => {
  return ((localValue.value - props.min) / (props.max - props.min)) * 100
})

const handleInput = () => {
  emit('update:modelValue', localValue.value)
  emit('change', localValue.value)
}
</script>

<style scoped>
.slider-container {
  position: relative;
  height: 20px;
  width: 100%;
  padding: 0;
}

.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: transparent;
  outline: none;
  opacity: 0;
  z-index: 2;
  position: relative;
  cursor: pointer;
}

.slider-track {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: 0;
  height: 4px;
  width: 100%;
  background-color: #e1e1e1;
  border-radius: 2px;
}

.slider-track-fill {
  position: absolute;
  height: 100%;
  background-color: #0071e4;
  border-radius: 2px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #0071e4;
  border-radius: 50%;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #0071e4;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}
</style> 