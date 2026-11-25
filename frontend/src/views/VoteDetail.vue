<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import http from '../api/http'

const route = useRoute()
const voteId = Number(route.params.id)

const vote = ref(null)
const result = ref(null)
const loading = ref(true)
const submitting = ref(false)
const selected = ref([]) // 单选为 id，多选为 id 数组
let chart = null

const isSingle = computed(() => vote.value?.vote_type === 'single')
const openNow = computed(
  () => vote.value?.status === 'open' && new Date(vote.value.deadline) > new Date()
)
const showForm = computed(
  () => vote.value && openNow.value && !vote.value.voted
)
const fmtDeadline = computed(() =>
  vote.value ? new Date(vote.value.deadline).toLocaleString('zh-CN', { hour12: false }) : ''
)

const load = async () => {
  loading.value = true
  try {
    vote.value = await http.get(`/api/votes/${voteId}`)
    if (!showForm.value) {
      result.value = await http.get(`/api/votes/${voteId}/result`)
      await nextTick()
      renderChart()
    }
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  const el = document.getElementById('result-chart')
  if (!el || !result.value) return
  if (chart) chart.dispose()
  chart = echarts.init(el)
  const opts = result.value.options
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 16, right: 24, top: 24, bottom: 24, containLabel: true },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: opts.map((o) => o.content) },
    series: [
      {
        type: 'bar',
        data: opts.map((o) => o.count),
        label: {
          show: true,
          position: 'right',
          formatter: (p) => `${p.value} 票（${opts[p.dataIndex].percent}%）`,
        },
        itemStyle: { color: '#409eff', borderRadius: [0, 4, 4, 0] },
      },
    ],
  })
  window.addEventListener('resize', () => chart?.resize())
}

const submit = async () => {
  const choice = isSingle.value ? [selected.value] : selected.value
  if (!choice.length || choice.some((v) => v === undefined || v === null || v === '')) {
    return ElMessage.error('请先选择选项')
  }
  if (!isSingle.value && choice.length > vote.value.max_choices) {
    return ElMessage.error(`最多可选 ${vote.value.max_choices} 项`)
  }
  submitting.value = true
  try {
    await http.post(`/api/votes/${voteId}/ballot`, { option_ids: choice })
    ElMessage.success('投票成功！')
    await load()
  } finally {
    submitting.value = false
  }
}

const share = async () => {
  const url = `${location.origin}/vote/${voteId}`
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('分享链接已复制：' + url)
  } catch {
    ElMessage.info('分享链接：' + url)
  }
}

onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <el-card v-if="vote">
      <template #header>
        <div class="head">
          <div class="title">
            {{ vote.title }}
            <el-tag :type="openNow ? 'success' : 'info'" size="small">
              {{ openNow ? '进行中' : '已结束' }}
            </el-tag>
            <el-tag v-if="!isSingle" type="warning" size="small">
              多选（最多 {{ vote.max_choices }} 项）
            </el-tag>
          </div>
          <el-button size="small" plain @click="share">🔗 复制分享链接</el-button>
        </div>
      </template>

      <div v-if="vote.description" class="desc">{{ vote.description }}</div>
      <div class="meta">
        发起人：{{ vote.creator }} · 截止时间：{{ fmtDeadline }}
        · {{ vote.anonymous ? '匿名投票' : '实名投票' }}
      </div>

      <!-- 未投且开放：显示投票表单 -->
      <template v-if="showForm">
        <el-divider content-position="left">请作出你的选择</el-divider>
        <el-radio-group v-if="isSingle" v-model="selected" class="options">
          <el-radio v-for="o in vote.options" :key="o.id" :value="o.id" border class="opt">
            {{ o.content }}
          </el-radio>
        </el-radio-group>
        <el-checkbox-group v-else v-model="selected" class="options">
          <el-checkbox v-for="o in vote.options" :key="o.id" :value="o.id" border class="opt">
            {{ o.content }}
          </el-checkbox>
        </el-checkbox-group>
        <div class="actions">
          <el-button type="primary" :loading="submitting" @click="submit">提交投票</el-button>
        </div>
      </template>

      <!-- 已投 / 已结束：显示结果 -->
      <template v-else>
        <el-divider content-position="left">
          投票结果（{{ result?.total_voters || 0 }} 人参与）
          <el-tag v-if="vote.voted" type="success" size="small" style="margin-left: 8px">你已投过票</el-tag>
        </el-divider>
        <div id="result-chart" class="chart" />
        <el-table v-if="result" :data="result.options" stripe class="result-table">
          <el-table-column prop="content" label="选项" />
          <el-table-column prop="count" label="票数" width="80" />
          <el-table-column prop="percent" label="占比 %" width="90" />
          <el-table-column v-if="!vote.anonymous" label="投票人" min-width="160">
            <template #default="{ row }">{{ row.voters.join('、') || '—' }}</template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 17px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.desc {
  white-space: pre-wrap;
  color: #606266;
  margin-bottom: 8px;
}
.meta {
  font-size: 13px;
  color: #909399;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
}
.opt {
  width: 100%;
  margin: 0;
}
.actions {
  margin-top: 16px;
}
.chart {
  width: 100%;
  height: 300px;
}
.result-table {
  margin-top: 16px;
}
</style>
