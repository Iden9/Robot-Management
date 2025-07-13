<template>
  <div class="role-search-bar">
    <div class="search-input-wrapper">
      <SearchIcon class="search-icon" />
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索角色名称、编码或描述..."
        class="search-input"
        @input="handleSearch"
      />
      <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
        <ClearIcon />
      </button>
    </div>
    
    <div class="filter-tabs">
      <button
        v-for="filter in filters"
        :key="filter.value"
        :class="['filter-tab', { active: currentFilter === filter.value }]"
        @click="handleFilter(filter.value)"
      >
        {{ filter.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SearchIcon from '@/components/account/icons/SearchIcon.vue'
import ClearIcon from '@/components/account/icons/ClearIcon.vue'

const emit = defineEmits(['search', 'filter'])

const searchQuery = ref('')
const currentFilter = ref('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' },
  { label: '系统角色', value: 'system' },
  { label: '自定义角色', value: 'custom' }
]

const handleSearch = () => {
  emit('search', searchQuery.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  emit('search', '')
}

const handleFilter = (filter) => {
  currentFilter.value = filter
  emit('filter', filter)
}
</script>

<style scoped>
.role-search-bar {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.search-input-wrapper {
  position: relative;
  margin-bottom: 16px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #666;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 40px 0 40px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  background-color: #fff;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #0071e4;
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.clear-btn:hover {
  background-color: #f0f0f0;
}

.clear-btn svg {
  width: 16px;
  height: 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  background-color: #fff;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.filter-tab:hover {
  border-color: #0071e4;
  color: #0071e4;
}

.filter-tab.active {
  background-color: #0071e4;
  border-color: #0071e4;
  color: #fff;
}
</style>