import axios from 'axios'

const request = axios.create({
    baseURL: '/api',
    timeout: 10000
})

// 请求拦截器 - 添加认证token
request.interceptors.request.use(config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
}, error => {
    return Promise.reject(error)
})

// 响应拦截器 - 统一处理响应和错误
request.interceptors.response.use(
    response => {
        const { data } = response
        
        // 如果是blob类型的响应（文件下载），直接返回
        if (response.config.responseType === 'blob') {
            return response
        }
        
        // 后端返回的标准格式: { code, message, data }
        if (data.code === 200) {
            return data
        } else {
            // 处理业务错误
            const error = new Error(data.message || '请求失败')
            error.code = data.code
            return Promise.reject(error)
        }
    },
    error => {
        // 处理HTTP错误
        if (error.response) {
            const { status, data } = error.response
            
            switch (status) {
                case 401:
                    // token过期或无效，清除本地存储并跳转登录页
                    localStorage.removeItem('token')
                    localStorage.removeItem('userInfo')
                    window.location.href = '/login'
                    break
                case 403:
                    console.error('权限不足')
                    break
                case 404:
                    console.error('请求的资源不存在')
                    break
                case 500:
                    console.error('服务器内部错误')
                    break
                default:
                    console.error(`请求错误: ${status}`)
            }
            
            error.message = data?.message || error.message
        } else if (error.request) {
            error.message = '网络请求失败，请检查网络连接'
        } else {
            error.message = '请求配置错误'
        }
        
        return Promise.reject(error)
    }
)

export default request