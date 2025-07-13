<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input 
        type="text" 
        class="search-input" 
        placeholder="搜索用户名或真实姓名..." 
        v-model="searchQuery"
        @input="handleSearch"
      />
      <button v-if="searchQuery" class="clear-button" @click="clearSearch">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
    
    <div class="filter-dropdown">
      <select v-model="filterRole" @change="handleFilter">
        <option value="all">全部角色</option>
        <option value="admin">管理员</option>
        <option value="operator">操作员</option>
        <option value="viewer">访客</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue'

const emit = defineEmits(['search', 'filter'])

const searchQuery = ref('')
const filterRole = ref('all')

const handleSearch = () => {
  emit('search', searchQuery.value)
}

const handleFilter = () => {
  emit('filter', filterRole.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  emit('search', '')
}
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input-wrapper {
  position: relative;
  flex-grow: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #bfbfbf;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 40px 0 36px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 2px rgba(0, 113, 228, 0.1);
}

.clear-button {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #bfbfbf;
  padding: 0;
}

.clear-button svg {
  width: 14px;
  height: 14px;
}

.filter-dropdown select {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  min-width: 120px;
  cursor: pointer;
}

.filter-dropdown select:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 2px rgba(0, 113, 228, 0.1);
}
</style> 