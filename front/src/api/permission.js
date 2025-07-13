import request from '@/utils/request'

/**
 * 权限管理相关API
 */

// 获取权限列表
export const getPermissionList = (params = {}) => {
  return request.get('/permissions', { params })
}

// 获取按模块分组的权限列表
export const getGroupedPermissions = (params = {}) => {
  return request.get('/permissions/grouped', { params })
}

// 获取所有启用的权限（用于分配权限）
export const getAllActivePermissions = () => {
  return request.get('/permissions/all')
}

// 获取权限详情
export const getPermissionDetail = (permissionId) => {
  return request.get(`/permissions/${permissionId}`)
}

// 创建权限
export const createPermission = (data) => {
  return request.post('/permissions', data)
}

// 更新权限
export const updatePermission = (permissionId, data) => {
  return request.put(`/permissions/${permissionId}`, data)
}

// 删除权限
export const deletePermission = (permissionId) => {
  return request.delete(`/permissions/${permissionId}`)
}

// 获取权限模块列表
export const getPermissionModules = () => {
  return request.get('/permissions/modules')
}

// 批量权限操作
export const batchPermissionOperation = (permissionIds, operation) => {
  return request.post('/permissions/batch-operation', {
    permission_ids: permissionIds,
    operation
  })
}