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
        <div>
          <strong>后台服务正常</strong>
          <p>可继续处理运营事项</p>
        </div>
      </div>
      <el-dropdown>
        <div class="admin-topbar__user">
          <div class="admin-topbar__user-copy">
            <span class="admin-topbar__user-label">当前账号</span>
            <strong>{{ authStore.session?.userName || '未登录' }}</strong>
          </div>
          <span class="admin-topbar__role">{{ currentRoleLabel }}</span>
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
const currentRoleLabel = computed(() => authStore.session?.roleCodes?.join(' / ') || 'GUEST')
const currentDescription = computed(() => {
  if (route.meta.placeholder) {
    return '当前页面入口已预留，待对应业务能力补齐后继续交付。'
  }
  return '统一查看数据、处理待办并执行后台操作。'
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
  flex-wrap: wrap;
}

.admin-topbar__left,
.admin-topbar__right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-topbar__right {
  margin-left: auto;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.admin-topbar__left strong {
  display: block;
  font-size: 19px;
}

.admin-topbar__left p {
  margin: 4px 0 0;
  color: var(--kp-text-secondary);
  font-size: 13px;
}

.admin-topbar__signal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid rgba(47, 125, 87, 0.14);
  background: rgba(252, 249, 243, 0.82);
  color: var(--kp-text-secondary);
  font-size: 12px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.admin-topbar__signal strong {
  display: block;
  color: var(--kp-text);
  font-size: 12px;
}

.admin-topbar__signal p {
  margin: 2px 0 0;
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
  gap: 12px;
  padding: 8px 8px 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(80, 63, 47, 0.12);
  background: rgba(255, 251, 245, 0.9);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
  cursor: pointer;
}

.admin-topbar__user-copy {
  display: grid;
  gap: 2px;
  min-width: 96px;
}

.admin-topbar__user-label {
  color: var(--kp-text-secondary);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.admin-topbar__role {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(196, 77, 52, 0.12);
  color: var(--kp-accent-deep);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}
</style>
