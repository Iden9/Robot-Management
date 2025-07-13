import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserProfile, register } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const token = ref(localStorage.getItem('token') || '')
    const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
    const isLoading = ref(false)

    // 计算属性
    const isLoggedIn = computed(() => !!token.value)
    const isAuthenticated = computed(() => !!token.value && !!userInfo.value)
    const userRole = computed(() => userInfo.value?.role || '')
    const userName = computed(() => userInfo.value?.real_name || userInfo.value?.username || '')

    // 权限检查
    const hasPermission = computed(() => (permission) => {
        if (!userInfo.value) return false
        const permissions = userInfo.value.permissions || []
        return permissions.includes(permission)
    })

    const isAdmin = computed(() => userRole.value === 'admin')
    const isOperator = computed(() => userRole.value === 'operator')
    const isViewer = computed(() => userRole.value === 'viewer')

    // 动作
    const setToken = (newToken) => {
        token.value = newToken
        localStorage.setItem('token', newToken)
    }

    const setUserInfo = (info) => {
        userInfo.value = info
        localStorage.setItem('userInfo', JSON.stringify(info))
    }

    const clearAuth = () => {
        token.value = ''
        userInfo.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
    }

    // 登录
    const loginAction = async (credentials) => {
        try {
            isLoading.value = true
            const response = await login(credentials)
            
            if (response.data) {
                setToken(response.data.token)
                // 合并用户信息和权限
                const userWithPermissions = {
                    ...response.data.user,
                    permissions: response.data.permissions || []
                }
                setUserInfo(userWithPermissions)
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '登录失败' }
        } catch (error) {
            return { success: false, message: error.message || '登录失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 登出
    const logoutAction = async () => {
        try {
            await logout()
        } catch (error) {
            console.warn('登出请求失败:', error.message)
        } finally {
            clearAuth()
        }
    }

    // 获取用户信息
    const fetchUserProfile = async () => {
        try {
            const response = await getUserProfile()
            if (response.data) {
                // 如果响应中包含权限信息，合并进用户信息
                const userWithPermissions = {
                    ...response.data.user || response.data,
                    permissions: response.data.permissions || response.data.user?.permissions || []
                }
                setUserInfo(userWithPermissions)
                return { success: true, data: response.data }
            }
            return { success: false, message: response.message || '获取用户信息失败' }
        } catch (error) {
            console.error('获取用户信息失败:', error.message)
            if (error.code === 401) {
                clearAuth()
            }
            return { success: false, message: error.message || '获取用户信息失败' }
        }
    }

    // 检查token有效性
    const checkTokenValidity = async () => {
        if (!token.value) return false
        
        try {
            const result = await fetchUserProfile()
            return result.success
        } catch (error) {
            clearAuth()
            return false
        }
    }

    // 注册
    const registerAction = async (userData) => {
        try {
            isLoading.value = true
            const response = await register(userData)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '注册失败' }
        } catch (error) {
            return { success: false, message: error.message || '注册失败' }
        } finally {
            isLoading.value = false
        }
    }

    return {
        // 状态
        token,
        userInfo,
        isLoading,
        
        // 计算属性
        isLoggedIn,
        isAuthenticated,
        userRole,
        userName,
        hasPermission,
        isAdmin,
        isOperator,
        isViewer,
        
        // 动作
        setToken,
        setUserInfo,
        clearAuth,
        loginAction,
        logoutAction,
        fetchUserProfile,
        checkTokenValidity,
        registerAction
    }
})