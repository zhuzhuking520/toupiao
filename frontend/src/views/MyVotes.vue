<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'

const votes = ref([])
const loading = ref(false)

const typeText = { single: '单选', multiple: '多选' }

const fmtDeadline = (iso) => new Date(iso).toLocaleString('zh-CN', { hour12: false })

const load = async () => {
  loading.value = true
  try {
    votes.value = await http.get('/api/votes/mine/list')
  } finally {
    loading.value = false
  }
}

const closeVote = async (vote) => {
  await ElMessageBox.confirm(`确定提前关闭「${vote.title}」吗？关闭后不能再投票。`, '提前关闭', {
    confirmButtonText: '确定关闭',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await http.patch(`/api/votes/${vote.id}/close`)
  ElMessage.success('已关闭')
  load()
}

const deleteVote = async (vote) => {
  await ElMessageBox.confirm(
    `确定删除「${vote.title}」吗？投票记录将一并删除，不可恢复！`,
    '删除投票',
    { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error' }
  )
  await http.delete(`/api/votes/${vote.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <b>我的投票</b>
        <el-button type="primary" size="small" @click="$router.push('/create')">+ 发起投票</el-button>
      </div>
    </template>
    <el-table v-loading="loading" :data="votes" stripe>
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column label="类型" width="70">
        <template #default="{ row }">{{ typeText[row.vote_type] }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'open' ? 'success' : 'info'">
            {{ row.status === 'open' ? '进行中' : '已关闭' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="截止时间" width="160">
        <template #default="{ row }">{{ fmtDeadline(row.deadline) }}</template>
      </el-table-column>
      <el-table-column prop="option_count" label="选项数" width="70" />
      <el-table-column prop="voter_count" label="参与人数" width="80" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'open'"
            size="small"
            type="warning"
            plain
            @click="closeVote(row)"
          >
            关闭
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteVote(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>还没有发起过投票，点右上角「发起投票」试试</template>
    </el-table>
  </el-card>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
