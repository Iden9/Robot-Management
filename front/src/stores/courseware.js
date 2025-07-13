import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
    getCoursewareList, 
    getCoursewareDetail, 
    uploadCourseware, 
    updateCourseware, 
    deleteCourseware,
    batchDeleteCourseware,
    downloadCourseware,
    getCoursewareCategories,
    createCoursewareCategory,
    previewCourseware,
    getCoursewareUsageStats,
    shareCourseware
} from '@/api/courseware'

export const useCoursewareStore = defineStore('courseware', () => {
    // 状态
    const coursewareList = ref([])
    const currentCourseware = ref(null)
    const categories = ref([])
    const isLoading = ref(false)
    const uploadProgress = ref(0)
    const pagination = ref({
        current_page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    })

    // 获取课件列表
    const fetchCoursewareList = async (params = {}) => {
        try {
            isLoading.value = true
            const response = await getCoursewareList(params)
            
            if (response.data) {
                coursewareList.value = response.data.courseware || []
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
            
            return { success: false, message: response.message || '获取课件列表失败' }
        } catch (error) {
            console.error('获取课件列表失败:', error.message)
            return { success: false, message: error.message || '获取课件列表失败' }
        } finally {
            isLoading.value = false
        }
    }

    // 获取课件详情
    const fetchCoursewareDetail = async (coursewareId) => {
        try {
            const response = await getCoursewareDetail(coursewareId)
            
            if (response.data) {
                currentCourseware.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取课件详情失败' }
        } catch (error) {
            console.error('获取课件详情失败:', error.message)
            return { success: false, message: error.message || '获取课件详情失败' }
        }
    }

    // 上传课件
    const uploadCoursewareAction = async (formData, progressCallback) => {
        try {
            isLoading.value = true
            uploadProgress.value = 0
            
            const response = await uploadCourseware(formData)
            
            if (response.data) {
                // 刷新课件列表
                await fetchCoursewareList()
                uploadProgress.value = 100
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '上传课件失败' }
        } catch (error) {
            console.error('上传课件失败:', error.message)
            return { success: false, message: error.message || '上传课件失败' }
        } finally {
            isLoading.value = false
            uploadProgress.value = 0
        }
    }

    // 更新课件信息
    const updateCoursewareAction = async (coursewareId, data) => {
        try {
            const response = await updateCourseware(coursewareId, data)
            
            if (response.data) {
                // 更新本地课件列表中的数据
                const index = coursewareList.value.findIndex(item => item.id === coursewareId)
                if (index !== -1) {
                    coursewareList.value[index] = response.data
                }
                
                // 如果是当前查看的课件，也更新
                if (currentCourseware.value && currentCourseware.value.id === coursewareId) {
                    currentCourseware.value = response.data
                }
                
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '更新课件失败' }
        } catch (error) {
            console.error('更新课件失败:', error.message)
            return { success: false, message: error.message || '更新课件失败' }
        }
    }

    // 删除课件
    const deleteCoursewareAction = async (coursewareId) => {
        try {
            const response = await deleteCourseware(coursewareId)
            
            if (response.code === 200) {
                // 从本地列表中移除
                coursewareList.value = coursewareList.value.filter(item => item.id !== coursewareId)
                
                // 如果删除的是当前查看的课件，清空
                if (currentCourseware.value && currentCourseware.value.id === coursewareId) {
                    currentCourseware.value = null
                }
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '删除课件失败' }
        } catch (error) {
            console.error('删除课件失败:', error.message)
            return { success: false, message: error.message || '删除课件失败' }
        }
    }

    // 批量删除课件
    const batchDeleteCoursewareAction = async (coursewareIds) => {
        try {
            const response = await batchDeleteCourseware(coursewareIds)
            
            if (response.code === 200) {
                // 从本地列表中移除
                coursewareList.value = coursewareList.value.filter(item => !coursewareIds.includes(item.id))
                
                return { success: true, message: response.message }
            }
            
            return { success: false, message: response.message || '批量删除课件失败' }
        } catch (error) {
            console.error('批量删除课件失败:', error.message)
            return { success: false, message: error.message || '批量删除课件失败' }
        }
    }

    // 下载课件
    const downloadCoursewareAction = async (coursewareId) => {
        try {
            const response = await downloadCourseware(coursewareId)
            
            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `courseware_${coursewareId}`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            
            return { success: true, message: '下载成功' }
        } catch (error) {
            console.error('下载课件失败:', error.message)
            return { success: false, message: error.message || '下载课件失败' }
        }
    }

    // 获取课件分类
    const fetchCategories = async () => {
        try {
            const response = await getCoursewareCategories()
            
            if (response.data) {
                categories.value = response.data
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取课件分类失败' }
        } catch (error) {
            console.error('获取课件分类失败:', error.message)
            return { success: false, message: error.message || '获取课件分类失败' }
        }
    }

    // 创建课件分类
    const createCategoryAction = async (data) => {
        try {
            const response = await createCoursewareCategory(data)
            
            if (response.data) {
                // 刷新分类列表
                await fetchCategories()
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '创建课件分类失败' }
        } catch (error) {
            console.error('创建课件分类失败:', error.message)
            return { success: false, message: error.message || '创建课件分类失败' }
        }
    }

    // 预览课件
    const previewCoursewareAction = async (coursewareId) => {
        try {
            const response = await previewCourseware(coursewareId)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '预览课件失败' }
        } catch (error) {
            console.error('预览课件失败:', error.message)
            return { success: false, message: error.message || '预览课件失败' }
        }
    }

    // 获取课件使用统计
    const fetchUsageStats = async (coursewareId) => {
        try {
            const response = await getCoursewareUsageStats(coursewareId)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '获取使用统计失败' }
        } catch (error) {
            console.error('获取使用统计失败:', error.message)
            return { success: false, message: error.message || '获取使用统计失败' }
        }
    }

    // 分享课件
    const shareCoursewareAction = async (coursewareId, data) => {
        try {
            const response = await shareCourseware(coursewareId, data)
            
            if (response.data) {
                return { success: true, data: response.data }
            }
            
            return { success: false, message: response.message || '分享课件失败' }
        } catch (error) {
            console.error('分享课件失败:', error.message)
            return { success: false, message: error.message || '分享课件失败' }
        }
    }

    // 清空数据
    const clearData = () => {
        coursewareList.value = []
        currentCourseware.value = null
        categories.value = []
        uploadProgress.value = 0
        pagination.value = {
            current_page: 1,
            per_page: 20,
            total: 0,
            pages: 1
        }
    }

    return {
        // 状态
        coursewareList,
        currentCourseware,
        categories,
        isLoading,
        uploadProgress,
        pagination,
        
        // 动作
        fetchCoursewareList,
        fetchCoursewareDetail,
        uploadCoursewareAction,
        updateCoursewareAction,
        deleteCoursewareAction,
        batchDeleteCoursewareAction,
        downloadCoursewareAction,
        fetchCategories,
        createCategoryAction,
        previewCoursewareAction,
        fetchUsageStats,
        shareCoursewareAction,
        clearData
    }
})