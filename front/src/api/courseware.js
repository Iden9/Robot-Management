import request from '@/utils/request'

/**
 * 课件管理相关API
 */

// 获取课件列表
export const getCoursewareList = (params = {}) => {
    return request({
        url: '/courseware',
        method: 'GET',
        params
    })
}

// 获取课件详情
export const getCoursewareDetail = (coursewareId) => {
    return request({
        url: `/courseware/${coursewareId}`,
        method: 'GET'
    })
}

// 上传课件
export const uploadCourseware = (formData) => {
    return request({
        url: '/courseware/upload',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 更新课件信息
export const updateCourseware = (coursewareId, data) => {
    return request({
        url: `/courseware/${coursewareId}`,
        method: 'PUT',
        data
    })
}

// 删除课件
export const deleteCourseware = (coursewareId) => {
    return request({
        url: `/courseware/${coursewareId}`,
        method: 'DELETE'
    })
}

// 批量删除课件
export const batchDeleteCourseware = (coursewareIds) => {
    return request({
        url: '/courseware/batch-delete',
        method: 'POST',
        data: { courseware_ids: coursewareIds }
    })
}

// 下载课件
export const downloadCourseware = (coursewareId) => {
    return request({
        url: `/courseware/${coursewareId}/download`,
        method: 'GET',
        responseType: 'blob'
    })
}

// 获取课件分类
export const getCoursewareCategories = () => {
    return request({
        url: '/courseware/categories',
        method: 'GET'
    })
}

// 创建课件分类
export const createCoursewareCategory = (data) => {
    return request({
        url: '/courseware/categories',
        method: 'POST',
        data
    })
}

// 课件预览（获取预览信息，不是文件本身）
export const previewCourseware = (coursewareId) => {
    return request({
        url: `/courseware/${coursewareId}/preview-info`,
        method: 'GET'
    })
}

// 获取课件使用统计
export const getCoursewareUsageStats = (coursewareId) => {
    return request({
        url: `/courseware/${coursewareId}/usage-stats`,
        method: 'GET'
    })
}

// 课件分享
export const shareCourseware = (coursewareId, data) => {
    return request({
        url: `/courseware/${coursewareId}/share`,
        method: 'POST',
        data
    })
}