import request from '@/utils/request'

// 获取知识库列表
export const getKnowledgeList = (params) => {
  return request({
    url: '/knowledge',
    method: 'GET',
    params
  })
}

// 获取知识库详情
export const getKnowledgeDetail = (id) => {
  return request({
    url: `/knowledge/${id}`,
    method: 'GET'
  })
}

// 创建知识库
export const createKnowledge = (data) => {
  return request({
    url: '/knowledge',
    method: 'POST',
    data
  })
}

// 更新知识库
export const updateKnowledge = (id, data) => {
  return request({
    url: `/knowledge/${id}`,
    method: 'PUT',
    data
  })
}

// 删除知识库
export const deleteKnowledge = (id) => {
  return request({
    url: `/knowledge/${id}`,
    method: 'DELETE'
  })
}

// 搜索知识库
export const searchKnowledge = (keyword) => {
  return request({
    url: '/knowledge/search',
    method: 'GET',
    params: { keyword }
  })
}

// 获取知识库分类
export const getKnowledgeCategories = () => {
  return request({
    url: '/knowledge/categories',
    method: 'GET'
  })
}

// 获取热门知识库
export const getPopularKnowledge = (limit = 10) => {
  return request({
    url: '/knowledge/popular',
    method: 'GET',
    params: { limit }
  })
}

// 记录知识库使用
export const recordKnowledgeUsage = (id) => {
  return request({
    url: `/knowledge/${id}/usage`,
    method: 'POST'
  })
}