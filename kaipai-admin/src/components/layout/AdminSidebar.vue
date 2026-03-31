<template>
  <aside class="admin-sidebar" :class="{ 'admin-sidebar--collapsed': appStore.sidebarCollapsed }">
    <div class="admin-sidebar__brand">
      <span class="admin-sidebar__mark">KP</span>
      <div v-if="!appStore.sidebarCollapsed">
        <strong>开拍了后台</strong>
        <p>Platform Console</p>
      </div>
    </div>
    <el-scrollbar class="admin-sidebar__scroll">
      <div class="admin-sidebar__section-title" v-if="!appStore.sidebarCollapsed">导航</div>
      <el-menu
        :default-active="route.path"
        :collapse="appStore.sidebarCollapsed"
        router
        class="admin-sidebar__menu"
      >
        <template v-for="item in menus" :key="item.key">
          <el-sub-menu v-if="item.children?.length" :index="item.key">
            <template #title>
              <el-icon><component :is="iconOf(item.icon)" /></el-icon>
              <span>{{ item.label }}</span>
            </template>
            <el-menu-item v-for="child in item.children" :key="child.key" :index="child.route || child.key">
              <el-icon><component :is="iconOf(child.icon)" /></el-icon>
              <span>{{ child.label }}</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.route || item.key">
            <el-icon><component :is="iconOf(item.icon)" /></el-icon>
            <span>{{ item.label }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>
  </aside>
</template>

<script setup lang="ts">
import {
  Avatar,
  Box,
  CircleCheck,
  Connection,
  DataBoard,
  Document,
  Files,
  MagicStick,
  Medal,
  Setting,
  UserFilled,
  Warning,
} from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'

const icons = {
  Avatar,
  Box,
  CircleCheck,
  Connection,
  DataBoard,
  Document,
  Files,
  MagicStick,
  Medal,
  Setting,
  UserFilled,
  Warning,
}

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()
const { menus } = storeToRefs(permissionStore)

function iconOf(name?: string) {
  return icons[(name || 'Document') as keyof typeof icons] || Document
}
</script>

<style scoped lang="scss">
.admin-sidebar {
  display: flex;
  flex-direction: column;
  width: 280px;
  padding: 20px 16px 16px;
  border-right: 1px solid var(--kp-border);
  background:
    linear-gradient(180deg, rgba(255, 252, 247, 0.94), rgba(246, 238, 228, 0.86)),
    rgba(255, 251, 245, 0.92);
  transition: width 0.25s ease;
}

.admin-sidebar--collapsed {
  width: 88px;
}

.admin-sidebar__brand {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 6px 8px 24px;

  strong {
    display: block;
    font-size: 16px;
  }

  p {
    margin: 4px 0 0;
    color: var(--kp-text-secondary);
    font-size: 12px;
  }
}

.admin-sidebar__mark {
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--kp-accent), var(--kp-accent-deep));
  color: white;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.admin-sidebar__section-title {
  padding: 0 12px 10px;
  color: var(--kp-text-secondary);
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.admin-sidebar__scroll {
  flex: 1;
}

:deep(.admin-sidebar__menu) {
  border-right: none;
  background: transparent;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 48px;
  border-radius: 14px;
  margin-bottom: 6px;
}

:deep(.el-menu-item.is-active) {
  background: rgba(196, 77, 52, 0.12);
  color: var(--kp-accent-deep);
}
</style>
