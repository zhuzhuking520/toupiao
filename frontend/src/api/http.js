import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
})

// 请求拦截：自动带上 JWT
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 统一踢回登录页
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const detail = err.response?.data?.detail
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      ElMessage.error(detail || '登录已过期，请重新登录')
      window.location.hash = ''
      window.location.href = '/login'
    } else {
      ElMessage.error(detail || '请求失败，请稍后重试')
    }
    return Promise.reject(err)
  }
)

export default http
