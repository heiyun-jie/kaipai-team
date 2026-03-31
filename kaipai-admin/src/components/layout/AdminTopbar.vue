<template>
  <header class="admin-topbar">
    <div class="admin-topbar__left">
      <el-button circle plain @click="appStore.toggleSidebar()">
        <el-icon><Fold /></el-icon>
      </el-button>
      <div>
        <strong>{{ currentTitle }}</strong>
        <p>{{ currentDescription }}</p>
      </div>
    </div>
    <div class="admin-topbar__right">
      <div class="admin-topbar__signal">
        <span class="admin-topbar__signal-dot" />
        <span>后台链路已接通 `/api/admin/**`</span>
      </div>
      <el-dropdown>
        <div class="admin-topbar__user">
          <div>
            <strong>{{ authStore.session?.userName || '未登录' }}</strong>
            <p>{{ authStore.session?.roleCodes?.join(' / ') || 'guest' }}</p>
          </div>
          <el-avatar>{{ (authStore.session?.userName || 'A').slice(0, 1) }}</el-avatar>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Fold } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

const currentTitle = computed(() => String(route.meta.title || '工作台'))
const currentDescription = computed(() => {
  if (route.meta.placeholder) {
    return '该页面壳层已接入，待后端聚合接口就绪后继续实现。'
  }
  return '列表、详情、操作确认和权限控制都在这个后台工程内统一收口。'
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.admin-topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 24px 32px 14px;
}

.admin-topbar__left,
.admin-topbar__right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-topbar__left strong {
  display: block;
  font-size: 18px;
}

.admin-topbar__left p,
.admin-topbar__user p {
  margin: 4px 0 0;
  color: var(--kp-text-secondary);
  font-size: 13px;
}

.admin-topbar__signal {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 251, 245, 0.65);
  color: var(--kp-text-secondary);
  font-size: 12px;
}

.admin-topbar__signal-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--kp-success);
  box-shadow: 0 0 0 5px rgba(47, 125, 87, 0.12);
}

.admin-topbar__user {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 6px 6px 6px 16px;
  border-radius: 999px;
  background: rgba(255, 251, 245, 0.8);
  cursor: pointer;
}
</style>
