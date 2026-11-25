import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import VoteList from '../views/VoteList.vue'
import VoteDetail from '../views/VoteDetail.vue'
import CreateVote from '../views/CreateVote.vue'
import MyVotes from '../views/MyVotes.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login, meta: { public: true } },
    { path: '/register', component: Register, meta: { public: true } },
    { path: '/', component: VoteList },
    { path: '/vote/:id', component: VoteDetail },
    { path: '/create', component: CreateVote },
    { path: '/mine', component: MyVotes },
  ],
})

// 路由守卫：未登录跳转登录页
router.beforeEach((to) => {
  const isPublic = to.meta.public
  const hasToken = !!localStorage.getItem('token')
  if (!isPublic && !hasToken) return '/login'
  if (isPublic && hasToken) return '/'
  return true
})

export default router
