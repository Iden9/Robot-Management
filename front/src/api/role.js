import request from '@/utils/request'

/**
 * 角色管理相关API
 */

// 获取角色列表
export const getRoleList = (params = {}) => {
  return request.get('/roles', { params })
}

// 获取角色详情
export const getRoleDetail = (roleId) => {
  return request.get(`/roles/${roleId}`)
}

// 创建角色
export const createRole = (data) => {
  return request.post('/roles', data)
}

// 更新角色
export const updateRole = (roleId, data) => {
  return request.put(`/roles/${roleId}`, data)
}

// 删除角色
export const deleteRole = (roleId) => {
  return request.delete(`/roles/${roleId}`)
}

// 获取所有启用的角色（用于下拉选择）
export const getAllActiveRoles = (params = {}) => {
  return request.get('/roles', { params })
}

// 获取角色权限
export const getRolePermissions = (roleId) => {
  return request.get(`/roles/${roleId}/permissions`)
}

// 分配角色权限
export const assignRolePermissions = (roleId, permissionIds) => {
  return request.post(`/roles/${roleId}/permissions`, {
    permission_ids: permissionIds
  })
}

// 批量角色操作
export const batchRoleOperation = (roleIds, operation) => {
  return request.post('/roles/batch-operation', {
    role_ids: roleIds,
    operation
  })
}