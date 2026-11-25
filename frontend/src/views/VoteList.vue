<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'

const votes = ref([])
const loading = ref(true)

async function loadVotes() {
  loading.value = true
  try {
    votes.value = await http.get('/api/votes')
  } finally {
    loading.value = false
  }
}

function statusTag(status) {
  return status === 'open' ? 'success' : 'info'
}

function statusText(status) {
  return status === 'open' ? '进行中' : '已截止'
}

onMounted(loadVotes)
</script>

<template>
  <div v-loading="loading">
    <div class="page-head">
      <h2>投票列表</h2>
      <el-tag type="info" effect="plain">共 {{ votes.length }} 个投票</el-tag>
      <el-button type="primary" size="small" style="margin-left: auto" @click="$router.push('/create')">
        + 发起投票
      </el-button>
    </div>

    <el-empty v-if="!loading && votes.length === 0" description="还没有投票，等你来创建" />

    <el-card v-for="v in votes" :key="v.id" class="vote-card" shadow="hover" @click="$router.push(`/vote/${v.id}`)">
      <div class="vote-row">
        <div>
          <div class="vote-title">
            {{ v.title }}
            <el-tag :type="statusTag(v.status)" size="small">{{ statusText(v.status) }}</el-tag>
            <el-tag v-if="v.vote_type === 'multiple'" type="warning" size="small">多选</el-tag>
          </div>
          <div class="vote-meta">
            发起人：{{ v.creator }} · {{ v.option_count }} 个选项 · 截止 {{ v.deadline.slice(0, 16).replace('T', ' ') }}
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.page-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.vote-card {
  margin-bottom: 12px;
  cursor: pointer;
}
.vote-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.vote-meta {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}
</style>
