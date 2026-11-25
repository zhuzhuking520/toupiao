<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  voteType: 'single',
  maxChoices: 1,
  anonymous: true,
  deadline: '',
  options: ['', ''],
})

// 单选时最多可选 1 项
watch(
  () => form.voteType,
  (t) => {
    if (t === 'single') form.maxChoices = 1
  }
)

const addOption = () => {
  if (form.options.length >= 20) {
    ElMessage.warning('最多 20 个选项')
    return
  }
  form.options.push('')
}

const removeOption = (index) => {
  if (form.options.length <= 2) {
    ElMessage.warning('至少保留 2 个选项')
    return
  }
  form.options.splice(index, 1)
}

const disabledDate = (date) => date.getTime() < Date.now() - 24 * 3600 * 1000

const submit = async () => {
  if (!form.title.trim()) return ElMessage.error('请填写投票标题')
  const filled = form.options.map((s) => s.trim()).filter(Boolean)
  if (filled.length < 2) return ElMessage.error('至少需要 2 个非空选项')
  if (new Set(filled).size !== filled.length) return ElMessage.error('选项内容不能重复')
  if (!form.deadline) return ElMessage.error('请选择截止时间')
  if (new Date(form.deadline) <= new Date()) return ElMessage.error('截止时间必须晚于当前时间')
  if (form.voteType === 'multiple' && form.maxChoices > filled.length) {
    return ElMessage.error('最多可选项数不能超过选项总数')
  }

  submitting.value = true
  try {
    await http.post('/api/votes', {
      title: form.title.trim(),
      description: form.description.trim(),
      vote_type: form.voteType,
      max_choices: form.maxChoices,
      anonymous: form.anonymous,
      deadline: form.deadline,
      options: filled.map((s) => ({ content: s })),
    })
    ElMessage.success('投票发布成功！')
    router.push('/mine')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <el-card>
    <template #header><b>发起投票</b></template>
    <el-form label-width="110px" label-position="left">
      <el-form-item label="投票标题" required>
        <el-input v-model="form.title" maxlength="100" show-word-limit placeholder="例如：班级春游地点投票" />
      </el-form-item>
      <el-form-item label="补充说明">
        <el-input v-model="form.description" type="textarea" :rows="2" maxlength="2000" placeholder="选填" />
      </el-form-item>
      <el-form-item label="投票类型">
        <el-radio-group v-model="form.voteType">
          <el-radio value="single">单选</el-radio>
          <el-radio value="multiple">多选</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="form.voteType === 'multiple'" label="最多可选">
        <el-input-number v-model="form.maxChoices" :min="1" :max="20" />
        <span class="tip">投票人最多可勾选的选项数</span>
      </el-form-item>
      <el-form-item label="匿名投票">
        <el-switch v-model="form.anonymous" active-text="匿名" inactive-text="实名" />
      </el-form-item>
      <el-form-item label="截止时间" required>
        <el-date-picker
          v-model="form.deadline"
          type="datetime"
          placeholder="选择投票截止时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DDTHH:mm:ss"
          :disabled-date="disabledDate"
        />
      </el-form-item>
      <el-form-item label="投票选项" required>
        <div class="options">
          <div v-for="(opt, i) in form.options" :key="i" class="option-row">
            <el-input v-model="form.options[i]" :placeholder="`选项 ${i + 1}`" maxlength="200" />
            <el-button type="danger" text :disabled="form.options.length <= 2" @click="removeOption(i)">
              删除
            </el-button>
          </div>
          <el-button plain @click="addOption">+ 添加选项</el-button>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="submit">发布投票</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<style scoped>
.tip {
  margin-left: 10px;
  color: #999;
  font-size: 12px;
}
.options {
  width: 100%;
}
.option-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
</style>
