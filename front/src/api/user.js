import request from '@/utils/request'

/**
 * 用户管理相关API
 */

// 获取用户列表
export const getUserList = (params = {}) => {
  return request.get('/users', { params })
}

// 获取用户详情
export const getUserDetail = (userId) => {
  return request.get(`/users/${userId}`)
}

// 创建用户
export const createUser = (data) => {
  return request.post('/users', data)
}

// 更新用户
export const updateUser = (userId, data) => {
  return request.put(`/users/${userId}`, data)
}

// 删除用户
export const deleteUser = (userId) => {
  return request.delete(`/users/${userId}`)
}

// 重置用户密码
export const resetUserPassword = (userId, data) => {
  return request.post(`/users/${userId}/reset-password`, data)
}

// 切换用户状态
export const toggleUserStatus = (userId, status) => {
  return request.put(`/users/${userId}/status`, { status })
}