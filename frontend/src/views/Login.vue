<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/auth'

const router = useRouter()
const { loading, login } = useAuth()

const form = reactive({ username: '', password: '' })

async function onSubmit() {
  await login({ username: form.username, password: form.password })
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2 class="title">登录 WebVote</h2>
      <el-form :model="form" label-position="top" @submit.prevent="onSubmit">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button
          type="primary"
          class="submit-btn"
          :loading="loading"
          @click="onSubmit"
        >
          登录
        </el-button>
        <div class="footer-link">
          还没有账号？
          <el-link type="primary" @click="router.push('/register')">去注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding-top: 10vh;
}
.auth-card {
  width: 380px;
}
.title {
  text-align: center;
  margin: 0 0 20px;
}
.submit-btn {
  width: 100%;
}
.footer-link {
  margin-top: 12px;
  text-align: center;
  font-size: 13px;
  color: #909399;
}
</style>
