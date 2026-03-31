<template>
  <PageContainer
    title="角色管理"
    description="当前页面以 `/admin/system/roles` 为准，支持角色查询、详情、新建、编辑、启停用和复制。"
  >
    <template #actions>
      <PermissionButton action="action.system.role.create" type="primary" @click="openCreateDialog">
        新建角色
      </PermissionButton>
    </template>

    <FilterPanel description="查询字段与后端 `AdminRoleQueryDTO` 保持一致。">
      <el-form :model="filters" inline>
        <el-form-item label="角色编码">
          <el-input v-model="filters.roleCode" placeholder="角色编码" clearable />
        </el-form-item>
        <el-form-item label="角色名称">
          <el-input v-model="filters.roleName" placeholder="角色名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="启用中" :value="1" />
            <el-option label="已禁用" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadRoles">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="adminRoleId" label="角色 ID" min-width="100" />
        <el-table-column prop="roleCode" label="角色编码" min-width="160" />
        <el-table-column prop="roleName" label="角色名称" min-width="160" />
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <StatusTag v-bind="adminRoleStatusMap[row.status] || fallbackStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column label="权限概览" min-width="220">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>菜单 {{ row.menuPermissions?.length || 0 }} / 页面 {{ row.pagePermissions?.length || 0 }}</strong>
              <span>操作 {{ row.actionPermissions?.length || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column label="更新时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.lastUpdate || row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="280">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.adminRoleId)">查看详情</el-button>
            <PermissionButton link action="action.system.role.edit" @click="openEditDialog(row)">编辑</PermissionButton>
            <PermissionButton link action="action.system.role.copy" @click="openCopyDialog(row)">复制</PermissionButton>
            <PermissionButton
              v-if="row.status === 1"
              link
              type="danger"
              action="action.system.role.disable"
              @click="openStatusDialog('disable', row)"
            >
              禁用
            </PermissionButton>
            <PermissionButton
              v-else
              link
              type="success"
              action="action.system.role.enable"
              @click="openStatusDialog('enable', row)"
            >
              启用
            </PermissionButton>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="filters.pageNo"
          v-model:page-size="filters.pageSize"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[20, 50, 100]"
          :total="total"
          @current-change="loadRoles"
          @size-change="loadRoles"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="角色详情" size="760px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-grid">
          <div v-for="item in detailBlocks" :key="item.label" class="detail-block">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <div class="permission-grid">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>菜单权限</h3></template>
            <div class="tag-list">
              <el-tag v-for="item in detail.menuPermissions || []" :key="item" effect="plain">{{ item }}</el-tag>
              <span v-if="!detail.menuPermissions?.length" class="muted">无</span>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>页面权限</h3></template>
            <div class="tag-list">
              <el-tag v-for="item in detail.pagePermissions || []" :key="item" effect="plain">{{ item }}</el-tag>
              <span v-if="!detail.pagePermissions?.length" class="muted">无</span>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>操作权限</h3></template>
            <div class="tag-list">
              <el-tag v-for="item in detail.actionPermissions || []" :key="item" effect="plain">{{ item }}</el-tag>
              <span v-if="!detail.actionPermissions?.length" class="muted">无</span>
            </div>
          </el-card>
        </div>
      </div>
    </el-drawer>

    <el-dialog v-model="formVisible" :title="formMode === 'create' ? '新建角色' : '编辑角色'" width="860px" destroy-on-close>
      <el-form label-position="top" :model="form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="角色编码">
              <el-input v-model="form.roleCode" placeholder="请输入角色编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色名称">
              <el-input v-model="form.roleName" placeholder="请输入角色名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="启用中" :value="1" />
                <el-option label="已禁用" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入角色说明" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="菜单权限">
              <el-select v-model="form.menuPermissions" multiple filterable allow-create default-first-option style="width: 100%">
                <el-option v-for="item in menuPermissionOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="页面权限">
              <el-select v-model="form.pagePermissions" multiple filterable allow-create default-first-option style="width: 100%">
                <el-option v-for="item in pagePermissionOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="操作权限">
              <el-select v-model="form.actionPermissions" multiple filterable allow-create default-first-option style="width: 100%">
                <el-option v-for="item in actionPermissionOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="formSubmitting" @click="submitForm">
          {{ formMode === 'create' ? '创建角色' : '保存修改' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="copyVisible" title="复制角色" width="560px" destroy-on-close>
      <el-form label-position="top" :model="copyForm">
        <el-form-item label="新角色编码">
          <el-input v-model="copyForm.roleCode" placeholder="请输入新角色编码" />
        </el-form-item>
        <el-form-item label="新角色名称">
          <el-input v-model="copyForm.roleName" placeholder="请输入新角色名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="copyForm.remark" type="textarea" :rows="3" placeholder="请输入复制说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyVisible = false">取消</el-button>
        <el-button type="primary" :loading="copySubmitting" @click="submitCopy">确认复制</el-button>
      </template>
    </el-dialog>

    <AuditConfirmDialog
      v-model="statusVisible"
      :title="statusMode === 'enable' ? '确认启用角色' : '确认禁用角色'"
      :confirm-text="statusMode === 'enable' ? '确认启用' : '确认禁用'"
      reason-label="操作原因"
      placeholder="请输入操作原因"
      :meta="statusMeta"
      @submit="submitStatusChange"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  copyAdminRole,
  createAdminRole,
  disableAdminRole,
  enableAdminRole,
  fetchAdminRoleDetail,
  fetchAdminRoles,
  updateAdminRole,
} from '@/api/system'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { PERMISSIONS } from '@/constants/permission'
import { adminRoleStatusMap } from '@/constants/status'
import type { AdminRoleItem, AdminRoleQuery, AdminRoleSavePayload } from '@/types/system'
import { formatDateTime } from '@/utils/format'

type FormMode = 'create' | 'edit'
type StatusMode = 'enable' | 'disable'

const loading = ref(false)
const rows = ref<AdminRoleItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<AdminRoleItem | null>(null)
const currentRow = ref<AdminRoleItem | null>(null)
const formVisible = ref(false)
const formMode = ref<FormMode>('create')
const formSubmitting = ref(false)
const copyVisible = ref(false)
const copySubmitting = ref(false)
const statusVisible = ref(false)
const statusMode = ref<StatusMode>('disable')

const filters = reactive<AdminRoleQuery>({
  pageNo: 1,
  pageSize: 20,
  roleCode: '',
  roleName: '',
  status: undefined,
})

const form = reactive<AdminRoleSavePayload>({
  roleCode: '',
  roleName: '',
  status: 1,
  remark: '',
  menuPermissions: [],
  pagePermissions: [],
  actionPermissions: [],
})

const copyForm = reactive({
  roleCode: '',
  roleName: '',
  remark: '',
})

const menuPermissionOptions = Object.values(PERMISSIONS.menu)
const pagePermissionOptions = Object.values(PERMISSIONS.page)
const actionPermissionOptions = Object.values(PERMISSIONS.action)

const detailBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '角色 ID', value: detail.value.adminRoleId },
    { label: '角色编码', value: detail.value.roleCode },
    { label: '角色名称', value: detail.value.roleName },
    { label: '状态', value: (adminRoleStatusMap[detail.value.status] || fallbackStatus(detail.value.status)).label },
    { label: '备注', value: detail.value.remark || '--' },
    { label: '创建人', value: detail.value.createUserName || '--' },
    { label: '创建时间', value: formatDateTime(detail.value.createTime) },
    { label: '更新人', value: detail.value.updateUserName || '--' },
    { label: '更新时间', value: formatDateTime(detail.value.lastUpdate) },
  ]
})

const statusMeta = computed(() => [
  { label: '角色 ID', value: currentRow.value?.adminRoleId },
  { label: '角色编码', value: currentRow.value?.roleCode },
  { label: '角色名称', value: currentRow.value?.roleName },
  { label: '目标状态', value: statusMode.value === 'enable' ? '启用' : '禁用' },
])

function fallbackStatus(status?: number) {
  return { label: `状态 ${status ?? '--'}`, tone: 'info' as const }
}

function resetFormModel() {
  form.roleCode = ''
  form.roleName = ''
  form.status = 1
  form.remark = ''
  form.menuPermissions = []
  form.pagePermissions = []
  form.actionPermissions = []
}

async function loadRoles() {
  loading.value = true
  try {
    const result = await fetchAdminRoles(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchAdminRoleDetail(id)
  detailVisible.value = true
}

function openCreateDialog() {
  formMode.value = 'create'
  resetFormModel()
  formVisible.value = true
}

function openEditDialog(row: AdminRoleItem) {
  currentRow.value = row
  formMode.value = 'edit'
  form.roleCode = row.roleCode
  form.roleName = row.roleName
  form.status = row.status
  form.remark = row.remark || ''
  form.menuPermissions = [...(row.menuPermissions || [])]
  form.pagePermissions = [...(row.pagePermissions || [])]
  form.actionPermissions = [...(row.actionPermissions || [])]
  formVisible.value = true
}

function openCopyDialog(row: AdminRoleItem) {
  currentRow.value = row
  copyForm.roleCode = `${row.roleCode}_copy`
  copyForm.roleName = `${row.roleName}副本`
  copyForm.remark = row.remark || ''
  copyVisible.value = true
}

function openStatusDialog(mode: StatusMode, row: AdminRoleItem) {
  currentRow.value = row
  statusMode.value = mode
  statusVisible.value = true
}

async function submitForm() {
  if (!form.roleCode || !form.roleName) {
    ElMessage.warning('请补齐角色编码和角色名称')
    return
  }
  formSubmitting.value = true
  try {
    if (formMode.value === 'create') {
      await createAdminRole(form)
      ElMessage.success('角色已创建')
    } else if (currentRow.value) {
      await updateAdminRole(currentRow.value.adminRoleId, form)
      ElMessage.success('角色已更新')
    }
    formVisible.value = false
    await loadRoles()
  } finally {
    formSubmitting.value = false
  }
}

async function submitCopy() {
  if (!currentRow.value) {
    return
  }
  if (!copyForm.roleCode || !copyForm.roleName) {
    ElMessage.warning('请补齐新角色编码和名称')
    return
  }
  copySubmitting.value = true
  try {
    await copyAdminRole(currentRow.value.adminRoleId, {
      roleCode: copyForm.roleCode,
      roleName: copyForm.roleName,
      remark: copyForm.remark,
    })
    ElMessage.success('角色已复制')
    copyVisible.value = false
    await loadRoles()
  } finally {
    copySubmitting.value = false
  }
}

async function submitStatusChange(reason: string) {
  if (!currentRow.value) {
    return
  }
  if (statusMode.value === 'enable') {
    await enableAdminRole(currentRow.value.adminRoleId, { reason })
    ElMessage.success('角色已启用')
  } else {
    await disableAdminRole(currentRow.value.adminRoleId, { reason })
    ElMessage.success('角色已禁用')
  }
  statusVisible.value = false
  await loadRoles()
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.roleCode = ''
  filters.roleName = ''
  filters.status = undefined
  loadRoles()
}

onMounted(loadRoles)
</script>

<style scoped lang="scss">
.table-card,
.detail-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.stack-cell {
  display: grid;

  strong {
    font-size: 13px;
  }

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.detail-layout {
  display: grid;
  gap: 16px;
}

.detail-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-block {
  display: grid;
  gap: 6px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(47, 36, 27, 0.05);

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }

  strong {
    font-size: 14px;
    line-height: 1.6;
    word-break: break-all;
  }
}

.permission-grid {
  display: grid;
  gap: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.muted {
  color: var(--kp-text-secondary);
}

@media (max-width: 820px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
