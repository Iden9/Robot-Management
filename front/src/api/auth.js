import request from '@/utils/request'

/**
 * 认证相关API
 */

// 用户登录
export const login = (data) => {
    return request({
        url: '/auth/login',
        method: 'POST',
        data
    })
}

// 用户登出
export const logout = () => {
    return request({
        url: '/auth/logout',
        method: 'POST'
    })
}

// 获取用户信息
export const getUserProfile = () => {
    return request({
        url: '/auth/profile',
        method: 'GET'
    })
}

// 获取用户会话列表
export const getUserSessions = () => {
    return request({
        url: '/auth/sessions',
        method: 'GET'
    })
}

// 终止指定会话
export const terminateSession = (sessionId) => {
    return request({
        url: `/auth/sessions/${sessionId}`,
        method: 'DELETE'
    })
}

// 修改密码
export const changePassword = (data) => {
    return request({
        url: '/auth/change-password',
        method: 'POST',
        data
    })
}

// 用户注册
export const register = (data) => {
    return request({
        url: '/auth/register',
        method: 'POST',
        data
    })
}