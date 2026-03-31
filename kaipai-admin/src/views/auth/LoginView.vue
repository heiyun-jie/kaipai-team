<template>
  <div class="login-view">
    <div class="login-view__panel">
      <section class="login-view__intro">
        <p class="login-view__eyebrow">PLATFORM CONTROL ROOM</p>
        <h1>开拍了平台后台</h1>
        <p class="login-view__copy">
          这是一套服务平台运营、审核与配置人员的独立后台。当前首批接入实名认证、会员和模板配置工作流。
        </p>
        <div class="login-view__signals">
          <span>统一权限模型</span>
          <span>高风险操作确认</span>
          <span>按 `/api/admin/**` 聚合接口接入</span>
        </div>
      </section>

      <el-card class="login-view__card" shadow="never">
        <div class="login-view__card-head">
          <p>后台登录</p>
          <strong>Admin Session</strong>
        </div>
        <el-form :model="form" label-position="top" @submit.prevent="submit">
          <el-form-item label="账号">
            <el-input v-model="form.account" placeholder="请输入后台账号" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入后台密码" />
          </el-form-item>
          <el-button type="primary" size="large" class="login-view__submit" :loading="loading" @click="submit">
            进入后台
          </el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  account: '',
  password: '',
})

async function submit() {
  if (!form.account || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.account, form.password)
    router.replace(String(route.query.redirect || '/dashboard'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-view {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
}

.login-view__panel {
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 24px;
}

.login-view__intro,
.login-view__card {
  border: 1px solid var(--kp-border);
  backdrop-filter: blur(16px);
  box-shadow: var(--kp-shadow);
}

.login-view__intro {
  padding: 48px;
  border-radius: 32px;
  background:
    linear-gradient(150deg, rgba(255, 248, 240, 0.88), rgba(237, 228, 213, 0.72)),
    rgba(255, 251, 245, 0.8);

  h1 {
    margin: 10px 0 16px;
    font-size: clamp(42px, 4vw, 68px);
    line-height: 1.02;
  }
}

.login-view__eyebrow {
  margin: 0;
  color: var(--kp-accent);
  letter-spacing: 0.24em;
  font-size: 12px;
}

.login-view__copy {
  max-width: 520px;
  margin: 0;
  color: var(--kp-text-secondary);
  font-size: 16px;
  line-height: 1.7;
}

.login-view__signals {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;

  span {
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(47, 36, 27, 0.06);
    color: var(--kp-text-secondary);
  }
}

.login-view__card {
  align-self: end;
  background: var(--kp-surface-strong);
}

.login-view__card-head {
  margin-bottom: 20px;

  p {
    margin: 0 0 6px;
    color: var(--kp-text-secondary);
  }

  strong {
    font-size: 26px;
  }
}

.login-view__submit {
  width: 100%;
}

@media (max-width: 900px) {
  .login-view__panel {
    grid-template-columns: 1fr;
  }

  .login-view__intro {
    padding: 32px;
  }
}
</style>
