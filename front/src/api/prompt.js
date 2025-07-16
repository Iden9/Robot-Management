import request from '@/utils/request'

// 获取提示词模板列表
export const getPromptList = (params) => {
  return request({
    url: '/prompt',
    method: 'GET',
    params
  })
}

// 获取提示词模板详情
export const getPromptDetail = (id) => {
  return request({
    url: `/prompt/${id}`,
    method: 'GET'
  })
}

// 创建提示词模板
export const createPrompt = (data) => {
  return request({
    url: '/prompt',
    method: 'POST',
    data
  })
}

// 更新提示词模板
export const updatePrompt = (id, data) => {
  return request({
    url: `/prompt/${id}`,
    method: 'PUT',
    data
  })
}

// 删除提示词模板
export const deletePrompt = (id) => {
  return request({
    url: `/prompt/${id}`,
    method: 'DELETE'
  })
}

// 搜索提示词模板
export const searchPrompt = (keyword) => {
  return request({
    url: '/prompt/search',
    method: 'GET',
    params: { keyword }
  })
}

// 获取提示词模板分类
export const getPromptCategories = () => {
  return request({
    url: '/prompt/categories',
    method: 'GET'
  })
}

// 获取热门提示词模板
export const getPopularPrompt = (limit = 10) => {
  return request({
    url: '/prompt/popular',
    method: 'GET',
    params: { limit }
  })
}

// 记录提示词模板使用
export const recordPromptUsage = (id) => {
  return request({
    url: `/prompt/${id}/usage`,
    method: 'POST'
  })
}

// 获取提示词模板类型
export const getPromptTypes = () => {
  return request({
    url: '/prompt/types',
    method: 'GET'
  })
}