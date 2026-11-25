import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

export function useAuth() {
  const router = useRouter()
  const loading = ref(false)

  async function login(payload) {
    loading.value = true
    try {
      const data = await http.post('/api/auth/login', payload)
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.user.username)
      ElMessage.success('登录成功')
      router.push('/')
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      await http.post('/api/auth/register', payload)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } finally {
      loading.value = false
    }
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return { loading, login, register, logout }
}
