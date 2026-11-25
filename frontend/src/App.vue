<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from './composables/auth'

const router = useRouter()
const { logout } = useAuth()
const username = computed(() => localStorage.getItem('username'))
</script>

<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand" @click="router.push('/')">🗳️ WebVote 在线投票系统</div>
      <div v-if="username" class="user-area">
        <el-menu mode="horizontal" :ellipsis="false" router class="nav">
          <el-menu-item index="/">投票大厅</el-menu-item>
          <el-menu-item index="/create">发起投票</el-menu-item>
          <el-menu-item index="/mine">我的投票</el-menu-item>
        </el-menu>
        <span>你好，{{ username }}</span>
        <el-button size="small" text @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f7fa;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.brand {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav {
  border-bottom: none;
  margin-right: 12px;
}
.main {
  max-width: 960px;
  margin: 0 auto;
  width: 100%;
}
</style>
