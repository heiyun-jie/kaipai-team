<template>
  <PageContainer
    title="角色管理"
    description="维护后台角色与权限范围，支持新建、编辑、启停用和复制角色。"
  >
    <template #actions>
      <PermissionButton action="action.system.role.create" type="primary" @click="openCreateDialog">
        新建角色
      </PermissionButton>
    </template>

    <FilterPanel description="按角色编码、名称和状态筛选角色，便于权限治理与排查。">
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
      <template #header>
        <div class="card-head">
          <div>
            <h3>AI 授权收口矩阵</h3>
            <p>确认哪些角色已补齐 AI 新页面 / 动作权限，哪些角色仍依赖旧操作日志 fallback。</p>
          </div>
          <StatusTag v-bind="roleMatrixStatusTag" />
        </div>
      </template>

      <div class="matrix-summary">
        <div v-for="item in matrixSummaryCards" :key="item.label" class="summary-block">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.description }}</small>
        </div>
      </div>

      <el-alert
        :type="roleMatrix?.canRetireFallback ? 'success' : 'warning'"
        :title="roleMatrix?.canRetireFallback ? '启用角色已不再依赖旧日志 fallback' : '仍有启用角色依赖旧日志 fallback'"
        :description="roleMatrixAlertText"
        :closable="false"
        show-icon
      />

      <el-table class="matrix-table" :data="roleMatrixRows" v-loading="matrixLoading" empty-text="暂无 AI 授权矩阵数据">
        <el-table-column label="角色" min-width="220">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.roleName }}</strong>
              <span>{{ row.roleCode }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="adminRoleStatusMap[row.status] || fallbackStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column label="迁移阶段" min-width="150">
          <template #default="{ row }">
            <StatusTag v-bind="getAiGovernanceStageMeta(row.rolloutStage)" />
          </template>
        </el-table-column>
        <el-table-column prop="boundUserCount" label="绑定账号" min-width="110" />
        <el-table-column label="权限覆盖" min-width="360">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag :type="row.hasAiGovernancePage ? 'success' : 'info'" effect="plain">AI 治理页</el-tag>
              <el-tag :type="row.hasAiReviewAction ? 'success' : 'info'" effect="plain">人工复核</el-tag>
              <el-tag :type="row.hasAiResolveAction ? 'success' : 'info'" effect="plain">建议重试</el-tag>
              <el-tag :type="row.hasOperationLogsPage ? 'warning' : 'info'" effect="plain">操作日志 fallback</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="待补权限" min-width="300">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag v-for="item in row.missingPermissions" :key="item" type="warning" effect="plain">
                {{ getPermissionDisplayText(item) }}
              </el-tag>
              <span v-if="!row.missingPermissions?.length" class="muted">已齐备</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="170">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="openDetail(row.adminRoleId)">查看详情</el-button>
              <PermissionButton link action="action.system.role.edit" @click="openEditFromMatrix(row)">
                补权限
              </PermissionButton>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

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
            <div class="table-actions">
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
            </div>
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
              <el-tag v-for="item in detail.menuPermissions || []" :key="item" effect="plain">
                {{ getPermissionDisplayText(item) }}
              </el-tag>
              <span v-if="!detail.menuPermissions?.length" class="muted">无</span>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>页面权限</h3></template>
            <div class="tag-list">
              <el-tag v-for="item in detail.pagePermissions || []" :key="item" effect="plain">
                {{ getPermissionDisplayText(item) }}
              </el-tag>
              <span v-if="!detail.pagePermissions?.length" class="muted">无</span>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>操作权限</h3></template>
            <div class="tag-list">
              <el-tag v-for="item in detail.actionPermissions || []" :key="item" effect="plain">
                {{ getPermissionDisplayText(item) }}
              </el-tag>
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
            <el-form-item label="权限编排">
              <div class="permission-stack">
                <el-alert
                  :title="aiGovernancePresetNotice.title"
                  :description="aiGovernancePresetNotice.description"
                  :type="aiGovernancePresetNotice.type"
                  :closable="false"
                  show-icon
                />

                <div class="ai-governance-bundle-grid">
                  <el-card
                    v-for="bundle in aiGovernancePermissionBundles"
                    :key="bundle.key"
                    class="detail-card ai-governance-bundle-card"
                    shadow="never"
                  >
                    <div class="stack-cell">
                      <strong>{{ bundle.label }}</strong>
                      <span>{{ bundle.description }}</span>
                    </div>
                    <div class="tag-list">
                      <el-tag v-for="item in bundle.codes" :key="item" effect="plain">
                        {{ getPermissionDisplayText(item) }}
                      </el-tag>
                    </div>
                    <div class="bundle-actions">
                      <el-button text type="primary" @click="applyAiGovernanceBundle(bundle)">套用建议权限包</el-button>
                    </div>
                  </el-card>
                </div>

                <PermissionTreeEditor
                  v-model:menu-permissions="form.menuPermissions"
                  v-model:page-permissions="form.pagePermissions"
                  v-model:action-permissions="form.actionPermissions"
                />
              </div>
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
  fetchAdminRoleAiGovernanceMatrix,
  fetchAdminRoleDetail,
  fetchAdminRoles,
  updateAdminRole,
} from '@/api/system'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import PermissionTreeEditor from '@/components/forms/PermissionTreeEditor.vue'
import { PERMISSIONS } from '@/constants/permission'
import { getPermissionDisplayText } from '@/constants/permission-registry'
import { adminRoleStatusMap } from '@/constants/status'
import type {
  AdminRoleAiGovernanceMatrix,
  AdminRoleAiGovernanceMatrixItem,
  AdminRoleItem,
  AdminRoleQuery,
  AdminRoleSavePayload,
} from '@/types/system'
import { formatDateTime } from '@/utils/format'

type FormMode = 'create' | 'edit'
type StatusMode = 'enable' | 'disable'
type PermissionBundlePreset = {
  key: string
  label: string
  description: string
  menuPermissions: string[]
  pagePermissions: string[]
  actionPermissions: string[]
  codes: string[]
}

const aiGovernancePermissionBundles: PermissionBundlePreset[] = [
  {
    key: 'ai-governance-read',
    label: 'AI 治理只读',
    description: '适合查看概览、历史、失败样本和治理动作，不包含人工处置动作。',
    menuPermissions: [PERMISSIONS.menu.system],
    pagePermissions: [PERMISSIONS.page.systemAiResumeGovernance],
    actionPermissions: [],
    codes: [PERMISSIONS.menu.system, PERMISSIONS.page.systemAiResumeGovernance],
  },
  {
    key: 'ai-governance-operate',
    label: 'AI 治理处置',
    description: '适合运营或风控处理失败样本，包含人工复核和建议重试动作。',
    menuPermissions: [PERMISSIONS.menu.system],
    pagePermissions: [PERMISSIONS.page.systemAiResumeGovernance],
    actionPermissions: [PERMISSIONS.action.systemAiResumeReview, PERMISSIONS.action.systemAiResumeResolve],
    codes: [
      PERMISSIONS.menu.system,
      PERMISSIONS.page.systemAiResumeGovernance,
      PERMISSIONS.action.systemAiResumeReview,
      PERMISSIONS.action.systemAiResumeResolve,
    ],
  },
]

const loading = ref(false)
const rows = ref<AdminRoleItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<AdminRoleItem | null>(null)
const currentRow = ref<AdminRoleItem | null>(null)
const matrixLoading = ref(false)
const roleMatrix = ref<AdminRoleAiGovernanceMatrix | null>(null)
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

const roleMatrixRows = computed(() => roleMatrix.value?.list || [])
const matrixSummaryCards = computed(() => [
  {
    label: '启用角色',
    value: roleMatrix.value?.enabledRoleCount ?? 0,
    description: '当前仍在生效的后台角色数',
  },
  {
    label: 'AI 已就绪',
    value: roleMatrix.value?.aiReadyRoleCount ?? 0,
    description: '已补齐 AI 页面与两类动作权限',
  },
  {
    label: '仍靠 Fallback',
    value: roleMatrix.value?.fallbackRoleCount ?? 0,
    description: '移除旧日志兜底前必须先迁移的角色',
  },
  {
    label: '受影响账号',
    value: roleMatrix.value?.fallbackBoundUserCount ?? 0,
    description: '当前绑定在 fallback 角色上的后台账号数',
  },
])
const roleMatrixStatusTag = computed(() =>
  roleMatrix.value?.canRetireFallback
    ? { label: '可评估下线 Fallback', tone: 'success' as const }
    : { label: '仍需兼容过渡', tone: 'warning' as const },
)
const roleMatrixAlertText = computed(() => {
  if (!roleMatrix.value) {
    return '正在加载 AI 授权矩阵。'
  }
  if (roleMatrix.value.canRetireFallback) {
    return '当前启用角色已不依赖 `page.system.operation-logs` 兜底，可在真环境授权验证完成后评估下线兼容逻辑。'
  }
  return `仍有 ${roleMatrix.value.fallbackRoleCount} 个启用角色、${roleMatrix.value.fallbackBoundUserCount} 个后台账号依赖旧日志兜底，不能直接移除 fallback。`
})

const statusMeta = computed(() => [
  { label: '角色 ID', value: currentRow.value?.adminRoleId },
  { label: '角色编码', value: currentRow.value?.roleCode },
  { label: '角色名称', value: currentRow.value?.roleName },
  { label: '目标状态', value: statusMode.value === 'enable' ? '启用' : '禁用' },
])
const aiGovernancePresetNotice = computed(() => {
  const hasIndependentPage = form.pagePermissions.includes(PERMISSIONS.page.systemAiResumeGovernance)
  const hasReviewAction = form.actionPermissions.includes(PERMISSIONS.action.systemAiResumeReview)
  const hasResolveAction = form.actionPermissions.includes(PERMISSIONS.action.systemAiResumeResolve)
  const hasLegacyFallbackOnly =
    form.pagePermissions.includes(PERMISSIONS.page.systemOperationLogs) &&
    !hasIndependentPage &&
    !hasReviewAction &&
    !hasResolveAction

  if (hasIndependentPage && hasReviewAction && hasResolveAction) {
    return {
      title: '当前角色已具备 AI 治理处置权限',
      description: '该角色可直接进入 AI 治理页，并执行人工复核与建议重试动作。',
      type: 'success' as const,
    }
  }

  if (hasIndependentPage) {
    return {
      title: '当前角色已具备 AI 治理页面权限',
      description: '若还需要人工处置失败样本，可继续补 action.system.ai-resume.review / resolve。',
      type: 'info' as const,
    }
  }

  if (hasLegacyFallbackOnly) {
    return {
      title: '当前角色仍依赖 operation-logs 兼容兜底',
      description: '旧角色可继续兼容访问，但新授权应优先发放独立 AI 页面 / 动作权限，便于后续下线 fallback。',
      type: 'warning' as const,
    }
  }

  return {
    title: '建议优先套用独立 AI 治理权限包',
    description: '角色页权限树已支持真实分配 page.system.ai-resume-governance 与 action.system.ai-resume.*，不建议再把 operation-logs 当成新授权入口。',
    type: 'info' as const,
  }
})

function fallbackStatus(status?: number) {
  return { label: `状态 ${status ?? '--'}`, tone: 'info' as const }
}

function getAiGovernanceStageMeta(stage?: string) {
  if (stage === 'ai_ready') {
    return { label: '新权限已齐备', tone: 'success' as const }
  }
  if (stage === 'compat_transition') {
    return { label: '兼容迁移中', tone: 'warning' as const }
  }
  if (stage === 'fallback_only') {
    return { label: '仅旧权限兜底', tone: 'danger' as const }
  }
  if (stage === 'partial_ai') {
    return { label: '新权限不完整', tone: 'warning' as const }
  }
  return { label: '未接入 AI', tone: 'info' as const }
}

function mergeUniquePermissions(current: string[], next: string[]) {
  return Array.from(new Set([...current, ...next]))
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

function applyAiGovernanceBundle(bundle: PermissionBundlePreset) {
  form.menuPermissions = mergeUniquePermissions(form.menuPermissions, bundle.menuPermissions)
  form.pagePermissions = mergeUniquePermissions(form.pagePermissions, bundle.pagePermissions)
  form.actionPermissions = mergeUniquePermissions(form.actionPermissions, bundle.actionPermissions)
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

async function loadRoleMatrix() {
  matrixLoading.value = true
  try {
    roleMatrix.value = await fetchAdminRoleAiGovernanceMatrix()
  } finally {
    matrixLoading.value = false
  }
}

async function reloadRoleData() {
  await Promise.all([loadRoles(), loadRoleMatrix()])
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

async function openEditFromMatrix(row: AdminRoleAiGovernanceMatrixItem) {
  const detailRow = await fetchAdminRoleDetail(row.adminRoleId)
  openEditDialog(detailRow)
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
    await reloadRoleData()
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
    await reloadRoleData()
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
  await reloadRoleData()
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
onMounted(loadRoleMatrix)
</script>

<style scoped lang="scss">
.table-card,
.detail-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;

  h3 {
    margin: 0;
    font-size: 18px;
  }

  p {
    margin: 6px 0 0;
    color: var(--kp-text-secondary);
    font-size: 13px;
    line-height: 1.6;
  }
}

.matrix-summary {
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.summary-block {
  display: grid;
  gap: 6px;
  padding: 16px;
  border: 1px solid rgba(47, 36, 27, 0.08);
  border-radius: 16px;
  background: rgba(47, 36, 27, 0.04);

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }

  strong {
    font-size: 24px;
    line-height: 1.1;
  }

  small {
    color: var(--kp-text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}

.matrix-table {
  margin-top: 16px;
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

.permission-stack {
  display: grid;
  gap: 12px;
  width: 100%;
}

.ai-governance-bundle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.ai-governance-bundle-card {
  display: grid;
  gap: 12px;
}

.bundle-actions {
  display: flex;
  justify-content: flex-end;
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
  .card-head {
    flex-direction: column;
  }

  .matrix-summary {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
