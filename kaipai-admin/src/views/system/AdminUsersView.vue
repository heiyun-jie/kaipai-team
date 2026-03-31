<template>
  <PageContainer
    title="后台账号"
    description="当前页面以 `/admin/system/admin-users` 聚合能力为准，支持账号查询、详情、新建、编辑、启停用、重置密码和角色绑定。"
  >
    <template #actions>
      <PermissionButton action="action.system.admin-user.create" type="primary" @click="openCreateDialog">
        新建后台账号
      </PermissionButton>
    </template>

    <FilterPanel description="查询字段与后端 `AdminUserQueryDTO` 保持一致。">
      <el-form :model="filters" inline>
        <el-form-item label="账号">
          <el-input v-model="filters.account" placeholder="后台账号" clearable />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="filters.userName" placeholder="姓名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="filters.phone" placeholder="手机号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="启用中" :value="1" />
            <el-option label="已禁用" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色编码">
          <el-input v-model="filters.roleCode" placeholder="例如 super_admin" clearable />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadUsers">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="adminUserId" label="ID" min-width="90" />
        <el-table-column prop="account" label="账号" min-width="150" />
        <el-table-column prop="userName" label="姓名" min-width="120" />
        <el-table-column label="联系方式" min-width="220">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.phone || '--' }}</strong>
              <span>{{ row.email || '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="220">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag v-for="role in row.roles" :key="role.roleCode" effect="plain">
                {{ role.roleName }}
              </el-tag>
              <span v-if="!row.roles?.length" class="muted">未绑定角色</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <StatusTag v-bind="adminUserStatusMap[row.status] || { label: `状态 ${row.status}`, tone: 'info' }" />
          </template>
        </el-table-column>
        <el-table-column label="最近登录" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.lastLoginTime) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="340">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.adminUserId)">查看详情</el-button>
            <PermissionButton link action="action.system.admin-user.edit" @click="openEditDialog(row)">
              编辑
            </PermissionButton>
            <PermissionButton link action="action.system.admin-user.bind-roles" @click="openBindDialog(row)">
              绑定角色
            </PermissionButton>
            <PermissionButton link action="action.system.admin-user.reset-password" @click="openResetDialog(row)">
              重置密码
            </PermissionButton>
            <PermissionButton
              v-if="row.status === 1"
              link
              type="danger"
              action="action.system.admin-user.disable"
              @click="openStatusDialog('disable', row)"
            >
              禁用
            </PermissionButton>
            <PermissionButton
              v-else
              link
              type="success"
              action="action.system.admin-user.enable"
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
          @current-change="loadUsers"
          @size-change="loadUsers"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="后台账号详情" size="620px">
      <div v-if="detail" class="detail-grid">
        <div v-for="item in detailBlocks" :key="item.label" class="detail-block">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
        <div class="detail-block detail-block--wide">
          <span>角色绑定</span>
          <div class="tag-list">
            <el-tag v-for="role in detail.roles" :key="role.roleCode" effect="plain">
              {{ role.roleName }} ({{ role.roleCode }})
            </el-tag>
            <strong v-if="!detail.roles?.length">未绑定角色</strong>
          </div>
        </div>
      </div>
    </el-drawer>

    <el-dialog v-model="formVisible" :title="formMode === 'create' ? '新建后台账号' : '编辑后台账号'" width="720px" destroy-on-close>
      <el-form label-position="top" :model="form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="账号">
              <el-input v-model="form.account" placeholder="请输入后台账号" />
            </el-form-item>
          </el-col>
          <el-col v-if="formMode === 'create'" :span="12">
            <el-form-item label="初始密码">
              <el-input v-model="form.password" type="password" show-password placeholder="请输入初始密码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名">
              <el-input v-model="form.userName" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col v-if="formMode === 'create'" :span="24">
            <el-form-item label="角色">
              <el-select v-model="form.roleCodes" multiple filterable style="width: 100%" placeholder="选择启用中的角色">
                <el-option v-for="role in activeRoleOptions" :key="role.roleCode" :label="`${role.roleName} (${role.roleCode})`" :value="role.roleCode" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="formSubmitting" @click="submitForm">
          {{ formMode === 'create' ? '创建账号' : '保存修改' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bindVisible" title="绑定后台账号角色" width="560px" destroy-on-close>
      <el-form label-position="top" :model="bindForm">
        <el-form-item label="角色">
          <el-select v-model="bindForm.roleCodes" multiple filterable style="width: 100%" placeholder="选择启用中的角色">
            <el-option v-for="role in activeRoleOptions" :key="role.roleCode" :label="`${role.roleName} (${role.roleCode})`" :value="role.roleCode" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="bindForm.reason" type="textarea" :rows="4" placeholder="请输入角色调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">取消</el-button>
        <el-button type="primary" :loading="bindSubmitting" @click="submitBindRoles">确认绑定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetVisible" title="重置后台账号密码" width="560px" destroy-on-close>
      <el-form label-position="top" :model="resetForm">
        <el-form-item label="新密码">
          <el-input v-model="resetForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="凭证交付方式">
          <el-input v-model="resetForm.credentialDeliveryMode" placeholder="例如：站内信 / 当面交付" />
        </el-form-item>
        <el-form-item label="重置原因">
          <el-input v-model="resetForm.reason" type="textarea" :rows="3" placeholder="请输入重置原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetSubmitting" @click="submitResetPassword">确认重置</el-button>
      </template>
    </el-dialog>

    <AuditConfirmDialog
      v-model="statusVisible"
      :title="statusMode === 'enable' ? '确认启用后台账号' : '确认禁用后台账号'"
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
  bindAdminUserRoles,
  createAdminUser,
  disableAdminUser,
  enableAdminUser,
  fetchAdminRoles,
  fetchAdminUserDetail,
  fetchAdminUsers,
  resetAdminUserPassword,
  updateAdminUser,
} from '@/api/system'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { PERMISSIONS } from '@/constants/permission'
import { adminUserStatusMap } from '@/constants/status'
import { usePermissionStore } from '@/stores/permission'
import type {
  AdminRoleItem,
  AdminUserDetail,
  AdminUserListItem,
  AdminUserQuery,
  AdminUserCreatePayload,
} from '@/types/system'
import { formatDateTime } from '@/utils/format'

type FormMode = 'create' | 'edit'
type StatusMode = 'enable' | 'disable'

const permissionStore = usePermissionStore()
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref<AdminUserDetail | null>(null)
const rows = ref<AdminUserListItem[]>([])
const total = ref(0)
const roleOptions = ref<AdminRoleItem[]>([])
const roleLoading = ref(false)
const currentRow = ref<AdminUserListItem | null>(null)

const formVisible = ref(false)
const formMode = ref<FormMode>('create')
const formSubmitting = ref(false)
const bindVisible = ref(false)
const bindSubmitting = ref(false)
const resetVisible = ref(false)
const resetSubmitting = ref(false)
const statusVisible = ref(false)
const statusMode = ref<StatusMode>('disable')

const filters = reactive<AdminUserQuery>({
  pageNo: 1,
  pageSize: 20,
  account: '',
  userName: '',
  phone: '',
  status: undefined,
  roleCode: '',
})

const form = reactive<AdminUserCreatePayload>({
  account: '',
  password: '',
  userName: '',
  phone: '',
  email: '',
  roleCodes: [],
})

const bindForm = reactive({
  roleCodes: [] as string[],
  reason: '',
})

const resetForm = reactive({
  newPassword: '',
  credentialDeliveryMode: '',
  reason: '',
})

const detailBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '账号 ID', value: detail.value.adminUserId },
    { label: '后台账号', value: detail.value.account },
    { label: '姓名', value: detail.value.userName },
    { label: '手机号', value: detail.value.phone || '--' },
    { label: '邮箱', value: detail.value.email || '--' },
    { label: '状态', value: (adminUserStatusMap[detail.value.status] || { label: `状态 ${detail.value.status}` }).label },
    { label: '最近登录时间', value: formatDateTime(detail.value.lastLoginTime) },
    { label: '最近登录 IP', value: detail.value.lastLoginIp || '--' },
    { label: '创建人', value: detail.value.createUserName || '--' },
    { label: '创建时间', value: formatDateTime(detail.value.createTime) },
    { label: '最后更新人', value: detail.value.updateUserName || '--' },
    { label: '最后更新时间', value: formatDateTime(detail.value.lastUpdate) },
  ]
})

const activeRoleOptions = computed(() => roleOptions.value.filter((item) => item.status === 1))

const statusMeta = computed(() => [
  { label: '账号 ID', value: currentRow.value?.adminUserId },
  { label: '后台账号', value: currentRow.value?.account },
  { label: '姓名', value: currentRow.value?.userName },
  { label: '目标状态', value: statusMode.value === 'enable' ? '启用' : '禁用' },
])

function resetFormModel() {
  form.account = ''
  form.password = ''
  form.userName = ''
  form.phone = ''
  form.email = ''
  form.roleCodes = []
}

async function loadUsers() {
  loading.value = true
  try {
    const result = await fetchAdminUsers(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  if (!permissionStore.hasPage(PERMISSIONS.page.systemRoles)) {
    roleOptions.value = []
    return
  }
  roleLoading.value = true
  try {
    const result = await fetchAdminRoles({
      pageNo: 1,
      pageSize: 200,
      roleCode: '',
      roleName: '',
      status: undefined,
    })
    roleOptions.value = result.list
  } catch (error) {
    roleOptions.value = []
  } finally {
    roleLoading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchAdminUserDetail(id)
  detailVisible.value = true
}

function openCreateDialog() {
  formMode.value = 'create'
  resetFormModel()
  formVisible.value = true
}

function openEditDialog(row: AdminUserListItem) {
  formMode.value = 'edit'
  currentRow.value = row
  form.account = row.account
  form.password = ''
  form.userName = row.userName
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.roleCodes = row.roles?.map((item) => item.roleCode) || []
  formVisible.value = true
}

function openBindDialog(row: AdminUserListItem) {
  currentRow.value = row
  bindForm.roleCodes = row.roles?.map((item) => item.roleCode) || []
  bindForm.reason = ''
  bindVisible.value = true
}

function openResetDialog(row: AdminUserListItem) {
  currentRow.value = row
  resetForm.newPassword = ''
  resetForm.credentialDeliveryMode = ''
  resetForm.reason = ''
  resetVisible.value = true
}

function openStatusDialog(mode: StatusMode, row: AdminUserListItem) {
  currentRow.value = row
  statusMode.value = mode
  statusVisible.value = true
}

async function submitForm() {
  if (!form.account || !form.userName) {
    ElMessage.warning('请补齐账号和姓名')
    return
  }
  if (formMode.value === 'create' && !form.password) {
    ElMessage.warning('请填写初始密码')
    return
  }
  formSubmitting.value = true
  try {
    if (formMode.value === 'create') {
      await createAdminUser({
        account: form.account,
        password: form.password,
        userName: form.userName,
        phone: form.phone,
        email: form.email,
        roleCodes: form.roleCodes,
      })
      ElMessage.success('后台账号已创建')
    } else if (currentRow.value) {
      await updateAdminUser(currentRow.value.adminUserId, {
        account: form.account,
        userName: form.userName,
        phone: form.phone,
        email: form.email,
      })
      ElMessage.success('后台账号已更新')
    }
    formVisible.value = false
    await loadUsers()
  } finally {
    formSubmitting.value = false
  }
}

async function submitBindRoles() {
  if (!currentRow.value) {
    return
  }
  bindSubmitting.value = true
  try {
    await bindAdminUserRoles(currentRow.value.adminUserId, {
      roleCodes: bindForm.roleCodes,
      reason: bindForm.reason,
    })
    ElMessage.success('角色绑定已更新')
    bindVisible.value = false
    await loadUsers()
    if (detailVisible.value) {
      detail.value = await fetchAdminUserDetail(currentRow.value.adminUserId)
    }
  } finally {
    bindSubmitting.value = false
  }
}

async function submitResetPassword() {
  if (!currentRow.value) {
    return
  }
  if (!resetForm.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  resetSubmitting.value = true
  try {
    await resetAdminUserPassword(currentRow.value.adminUserId, {
      newPassword: resetForm.newPassword,
      credentialDeliveryMode: resetForm.credentialDeliveryMode,
      reason: resetForm.reason,
      resetResult: 'success',
    })
    ElMessage.success('密码已重置')
    resetVisible.value = false
  } finally {
    resetSubmitting.value = false
  }
}

async function submitStatusChange(reason: string) {
  if (!currentRow.value) {
    return
  }
  if (statusMode.value === 'enable') {
    await enableAdminUser(currentRow.value.adminUserId, { reason })
    ElMessage.success('后台账号已启用')
  } else {
    await disableAdminUser(currentRow.value.adminUserId, { reason })
    ElMessage.success('后台账号已禁用')
  }
  statusVisible.value = false
  await loadUsers()
  if (detailVisible.value) {
    detail.value = await fetchAdminUserDetail(currentRow.value.adminUserId)
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.account = ''
  filters.userName = ''
  filters.phone = ''
  filters.status = undefined
  filters.roleCode = ''
  loadUsers()
}

onMounted(() => {
  loadUsers()
  loadRoles()
})
</script>

<style scoped lang="scss">
.table-card {
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

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.muted {
  color: var(--kp-text-secondary);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.detail-grid {
  display: grid;
  gap: 14px;
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

.detail-block--wide {
  grid-column: 1 / -1;
}

@media (max-width: 820px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
