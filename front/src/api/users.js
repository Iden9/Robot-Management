import request from '@/utils/request'

/**
 * 用户管理相关API
 */

// 获取用户列表
export const getUserList = (params = {}) => {
    return request({
        url: '/users',
        method: 'GET',
        params
    })
}

// 获取用户详情
export const getUserDetail = (userId) => {
    return request({
        url: `/users/${userId}`,
        method: 'GET'
    })
}

// 创建用户
export const createUser = (data) => {
    return request({
        url: '/users',
        method: 'POST',
        data
    })
}

// 更新用户信息
export const updateUser = (userId, data) => {
    return request({
        url: `/users/${userId}`,
        method: 'PUT',
        data
    })
}

// 删除用户
export const deleteUser = (userId) => {
    return request({
        url: `/users/${userId}`,
        method: 'DELETE'
    })
}

// 批量删除用户
export const batchDeleteUsers = (userIds) => {
    return request({
        url: '/users/batch-delete',
        method: 'POST',
        data: { user_ids: userIds }
    })
}

// 重置用户密码
export const resetUserPassword = (userId, data) => {
    return request({
        url: `/users/${userId}/reset-password`,
        method: 'POST',
        data
    })
}

// 启用/禁用用户
export const toggleUserStatus = (userId, status) => {
    return request({
        url: `/users/${userId}/toggle-status`,
        method: 'POST',
        data: { status }
    })
}

// 获取用户权限
export const getUserPermissions = (userId) => {
    return request({
        url: `/users/${userId}/permissions`,
        method: 'GET'
    })
}

// 更新用户权限
export const updateUserPermissions = (userId, permissions) => {
    return request({
        url: `/users/${userId}/permissions`,
        method: 'PUT',
        data: { permissions }
    })
}

// 获取用户操作日志
export const getUserOperationLogs = (userId, params = {}) => {
    return request({
        url: `/users/${userId}/logs`,
        method: 'GET',
        params
    })
}

// 导出用户列表
export const exportUserList = (params = {}) => {
    return request({
        url: '/users/export',
        method: 'GET',
        params,
        responseType: 'blob'
    })
}