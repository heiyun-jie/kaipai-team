<template>
  <div class="permission-editor">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="按模块、权限名称或权限码过滤" clearable />
      <div class="toolbar-actions">
        <el-tag effect="plain">菜单 {{ checkedSummary.menu }}</el-tag>
        <el-tag effect="plain">页面 {{ checkedSummary.page }}</el-tag>
        <el-tag effect="plain">操作 {{ checkedSummary.action }}</el-tag>
        <el-tag v-if="unknownCodes.length" type="warning" effect="plain">异常 {{ unknownCodes.length }}</el-tag>
        <el-button text @click="expandAll">全部展开</el-button>
        <el-button text @click="collapseAll">全部收起</el-button>
        <el-button text type="danger" @click="clearSelection">清空标准权限</el-button>
      </div>
    </div>

    <el-alert
      v-if="unknownCodes.length"
      type="warning"
      :closable="false"
      title="存在未登记权限码"
      description="以下权限码未进入当前权限矩阵 registry，提交时会继续保留，避免保存时被静默丢失。"
      show-icon
    />

    <div v-if="unknownCodes.length" class="unknown-list">
      <el-tag v-for="code in unknownCodes" :key="code" type="warning" closable @close="removeUnknownCode(code)">
        {{ code }}
      </el-tag>
      <el-button text type="danger" @click="clearUnknownCodes">移除全部未登记权限</el-button>
    </div>

    <el-tree
      ref="treeRef"
      class="permission-tree"
      node-key="key"
      show-checkbox
      :data="permissionTreeData"
      :filter-node-method="filterNode"
      @check="syncFromTree"
    >
      <template #default="{ data }">
        <div class="tree-node">
          <span>{{ data.label }}</span>
          <code v-if="data.permissionCode">{{ data.permissionCode }}</code>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { ElTree } from 'element-plus'
import {
  getUnknownPermissionCodes,
  mergePermissionCodes,
  permissionTreeData,
  splitPermissionCodes,
} from '@/constants/permission-registry'

const props = defineProps<{
  menuPermissions?: string[]
  pagePermissions?: string[]
  actionPermissions?: string[]
}>()

const emit = defineEmits<{
  'update:menuPermissions': [string[]]
  'update:pagePermissions': [string[]]
  'update:actionPermissions': [string[]]
}>()

const keyword = ref('')
const treeRef = ref<InstanceType<typeof ElTree>>()

const mergedCodes = computed(() => mergePermissionCodes(props))
const unknownCodes = computed(() => getUnknownPermissionCodes(mergedCodes.value))
const checkedSummary = computed(() => ({
  menu: props.menuPermissions?.length || 0,
  page: props.pagePermissions?.length || 0,
  action: props.actionPermissions?.length || 0,
}))

watch(keyword, (value) => {
  treeRef.value?.filter(value)
})

watch(
  () => mergedCodes.value,
  async () => {
    await nextTick()
    syncTreeCheckedKeys()
  },
  { deep: true, immediate: true },
)

function filterNode(value: string, data: { label: string; permissionCode?: string }) {
  if (!value) {
    return true
  }

  return data.label.includes(value) || data.permissionCode?.includes(value)
}

function syncTreeCheckedKeys() {
  treeRef.value?.setCheckedKeys(mergedCodes.value.filter((code) => !unknownCodes.value.includes(code)))
}

function syncFromTree() {
  const checkedLeafCodes = ((treeRef.value?.getCheckedKeys(true) || []) as string[]).filter(
    (item) => !item.startsWith('module:') && !item.startsWith('group:'),
  )
  const nextSelection = splitPermissionCodes([...checkedLeafCodes, ...unknownCodes.value])
  emit('update:menuPermissions', nextSelection.menuPermissions)
  emit('update:pagePermissions', nextSelection.pagePermissions)
  emit('update:actionPermissions', nextSelection.actionPermissions)
}

function clearSelection() {
  const nextSelection = splitPermissionCodes([...unknownCodes.value])
  emit('update:menuPermissions', nextSelection.menuPermissions)
  emit('update:pagePermissions', nextSelection.pagePermissions)
  emit('update:actionPermissions', nextSelection.actionPermissions)
}

function removeUnknownCode(code: string) {
  const nextSelection = splitPermissionCodes(mergedCodes.value.filter((item) => item !== code))
  emit('update:menuPermissions', nextSelection.menuPermissions)
  emit('update:pagePermissions', nextSelection.pagePermissions)
  emit('update:actionPermissions', nextSelection.actionPermissions)
}

function clearUnknownCodes() {
  const nextSelection = splitPermissionCodes(mergedCodes.value.filter((code) => !unknownCodes.value.includes(code)))
  emit('update:menuPermissions', nextSelection.menuPermissions)
  emit('update:pagePermissions', nextSelection.pagePermissions)
  emit('update:actionPermissions', nextSelection.actionPermissions)
}

function expandAll() {
  setExpanded(true)
}

function collapseAll() {
  setExpanded(false)
}

function setExpanded(expanded: boolean) {
  const nodesMap =
    (treeRef.value as unknown as { store?: { nodesMap?: Record<string, { level: number; expanded: boolean }> } })?.store?.nodesMap ||
    {}
  Object.values(nodesMap).forEach((node) => {
    if (node.level <= 2) {
      node.expanded = expanded
    }
  })
}
</script>

<style scoped lang="scss">
.permission-editor {
  display: grid;
  gap: 12px;
}

.toolbar {
  display: grid;
  gap: 12px;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.unknown-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.permission-tree {
  padding: 12px;
  border: 1px solid var(--kp-border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
}

.tree-node {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;

  code {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }
}
</style>
