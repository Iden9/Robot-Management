import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getUserList, 
    getUserDetail, 
    createUser, 
    updateUser, 
    deleteUser,
    batchDeleteUsers,
    resetUserPassword,
    toggleUserStatus,
    getUserPermissions,
    updateUserPermissions,
    getUserOperationLogs,
    exportUserList
} from '@/api/users'

export const useUsersStore = defineStore('users', () => {
    // 状态
    const userList = ref([])
    const currentUser = ref(null)
    const userPermissions = ref([])
    const operationLogs = ref([])
    const isLoading = ref(false)
    const pagination = ref({
        current_page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    })

    // 获取用户列表
    const fetchUserList = async (params = {}) => {
        try {
            isLoading.value = true
            const response = await getUserList(params)
            
            if (response.data) {
                userList.value = response.data.users || []
                pagination.value = {
                    current_page: response.data.current_page || 1,
                    per_page: response.data.per_page || 20,
                    total: response.data.total || 0,
                    pages: response.data.pages || 1,
                    has_next: response.data.has_next || false,
                    has_prev: response.data.has_prev || false
                }
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取用户列表失败' }
        } catch (error) {
            console.error('获取用户列表失败:', error.message)
            return { success: false, message: error.message || '获取用户列表失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取用户详情
    const fetchUserDetail = async (userId) => {
        try {
            const response = await getUserDetail(userId)
            
            if (response.data) {
                currentUser.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取用户详情失败' }
        } catch (error) {
            console.error('获取用户详情失败:', error.message)
            return { success: false, message: error.message || '获取用户详情失败' }
        }
    }

    // 创建用户
    const createUserAction = async (data) => {
        try {
            const response = await createUser(data)
            
            if (response.data) {
                // 刷新用户列表
                await fetchUserList()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建用户失败' }
        } catch (error) {
            console.error('创建用户失败:', error.message)
            return { success: false, message: error.message || '创建用户失败' }
        }
    }

    // 更新用户信息
    const updateUserAction = async (userId, data) => {
        try {
            const response = await updateUser(userId, data)
            
            if (response.data) {
                // 更新本地用户列表中的数据
                const index = userList.value.findIndex(item => item.id === userId)
                if (index !== -1) {
                    userList.value[index] = response.data
                }
                
                // 如果是当前查看的用户，也更新
                if (currentUser.value && currentUser.value.id === userId) {
                    currentUser.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新用户失败' }
        } catch (error) {
            console.error('更新用户失败:', error.message)
            return { success: false, message: error.message || '更新用户失败' }
        }
    }

    // 删除用户
    const deleteUserAction = async (userId) => {
        try {
            const response = await deleteUser(userId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                userList.value = userList.value.filter(item => item.id !== userId)
                
                // 如果删除的是当前查看的用户，清空
                if (currentUser.value && currentUser.value.id === userId) {
                    currentUser.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除用户失败' }
        } catch (error) {
            console.error('删除用户失败:', error.message)
            return { success: false, message: error.message || '删除用户失败' }
        }
    }

    // 批量删除用户
    const batchDeleteUsersAction = async (userIds) => {
        try {
            const response = await batchDeleteUsers(userIds)
            
            if (response.code === 200) {
                // 从本地列表中移除
                userList.value = userList.value.filter(item => !userIds.includes(item.id))
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '批量删除用户失败' }
        } catch (error) {
            console.error('批量删除用户失败:', error.message)
            return { success: false, message: error.message || '批量删除用户失败' }
        }
    }

    // 重置用户密码
    const resetUserPasswordAction = async (userId, data) => {
        try {
            const response = await resetUserPassword(userId, data)
            
            if (response.code === 200) {
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '重置密码失败' }
        } catch (error) {
            console.error('重置密码失败:', error.message)
            return { success: false, message: error.message || '重置密码失败' }
        }
    }

    // 启用/禁用用户
    const toggleUserStatusAction = async (userId, status) => {
        try {
            const response = await toggleUserStatus(userId, status)
            
            if (response.code === 200) {
                // 更新本地用户状态
                const index = userList.value.findIndex(item => item.id === userId)
                if (index !== -1) {
                    userList.value[index].status = status
                }
                
                // 如果是当前查看的用户，也更新
                if (currentUser.value && currentUser.value.id === userId) {
                    currentUser.value.status = status
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '更新用户状态失败' }
        } catch (error) {
            console.error('更新用户状态失败:', error.message)
            return { success: false, message: error.message || '更新用户状态失败' }
        }
    }

    // 获取用户权限
    const fetchUserPermissions = async (userId) => {
        try {
            const response = await getUserPermissions(userId)
            
            if (response.data) {
                userPermissions.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取用户权限失败' }
        } catch (error) {
            console.error('获取用户权限失败:', error.message)
            return { success: false, message: error.message || '获取用户权限失败' }
        }
    }

    // 更新用户权限
    const updateUserPermissionsAction = async (userId, permissions) => {
        try {
            const response = await updateUserPermissions(userId, permissions)
            
            if (response.code === 200) {
                userPermissions.value = permissions
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '更新用户权限失败' }
        } catch (error) {
            console.error('更新用户权限失败:', error.message)
            return { success: false, message: error.message || '更新用户权限失败' }
        }
    }

    // 获取用户操作日志
    const fetchUserOperationLogs = async (userId, params = {}) => {
        try {
            const response = await getUserOperationLogs(userId, params)
            
            if (response.data) {
                operationLogs.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取操作日志失败' }
        } catch (error) {
            console.error('获取操作日志失败:', error.message)
            return { success: false, message: error.message || '获取操作日志失败' }
        }
    }

    // 导出用户列表
    const exportUserListAction = async (params = {}) => {
        try {
            const response = await exportUserList(params)
            
            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'user_list.xlsx')
            document.body.appendChild(link)
            link.click()
            link.remove()
            
            return { success: true, message: '导出成功' }
        } catch (error) {
            console.error('导出用户列表失败:', error.message)
            return { success: false, message: error.message || '导出用户列表失败' }
        }
    }

    // 清空数据
    const clearData = () => {
        userList.value = []
        currentUser.value = null
        userPermissions.value = []
        operationLogs.value = []
        pagination.value = {
            current_page: 1,
            per_page: 20,
            total: 0,
            pages: 1
        }
    }

    return {
        // 状态
        userList,
        currentUser,
        userPermissions,
        operationLogs,
        isLoading,
        pagination,
        
        // 动作
        fetchUserList,
        fetchUserDetail,
        createUserAction,
        updateUserAction,
        deleteUserAction,
        batchDeleteUsersAction,
        resetUserPasswordAction,
        toggleUserStatusAction,
        fetchUserPermissions,
        updateUserPermissionsAction,
        fetchUserOperationLogs,
        exportUserListAction,
        clearData
    }
})