<template>
  <PageContainer
    title="邀请规则"
    eyebrow="Referral Policies"
    description="统一维护邀请资格判定门槛、频控限制和自动发放策略，避免前后台规则继续分裂。"
  >
    <template #actions>
      <PermissionButton action="action.referral.policy.create" type="primary" @click="openCreate">
        新建规则
      </PermissionButton>
    </template>

    <FilterPanel description="按规则名称和启用状态筛选，优先确认当前生效规则与资格发放口径是否一致。">
      <el-form :model="filters" inline>
        <el-form-item label="规则名称">
          <el-input v-model="filters.policyName" placeholder="规则名称" clearable />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-select v-model="filters.enabled" clearable style="width: 160px">
            <el-option label="启用中" :value="1" />
            <el-option label="已停用" :value="0" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="policyId" label="规则 ID" min-width="110" />
        <el-table-column prop="policyName" label="规则名称" min-width="180" />
        <el-table-column label="启用状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="referralPolicyEnabledMap[row.enabled || 0] || referralPolicyEnabledMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="实名要求" min-width="100">
          <template #default="{ row }">{{ formatSwitch(row.requireRealAuth) }}</template>
        </el-table-column>
        <el-table-column label="档案完整度" min-width="180">
          <template #default="{ row }">{{ formatProfileRequirement(row) }}</template>
        </el-table-column>
        <el-table-column label="同设备限制" min-width="120">
          <template #default="{ row }">{{ formatLimit('次/设备', row.sameDeviceLimit) }}</template>
        </el-table-column>
        <el-table-column label="小时频控" min-width="120">
          <template #default="{ row }">{{ formatLimit('次/小时', row.hourlyInviteLimit) }}</template>
        </el-table-column>
        <el-table-column label="自动发放" min-width="100">
          <template #default="{ row }">{{ formatSwitch(row.autoGrantEnabled) }}</template>
        </el-table-column>
        <el-table-column label="更新人" min-width="120">
          <template #default="{ row }">{{ row.updateUserName || '--' }}</template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.lastUpdate) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="260">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="openDetail(row.policyId)">查看详情</el-button>
              <PermissionButton link action="action.referral.policy.edit" @click="openEdit(row.policyId)">编辑</PermissionButton>
              <PermissionButton
                v-if="row.enabled === 1"
                link
                type="danger"
                action="action.referral.policy.disable"
                @click="openStatusDialog('disable', row)"
              >
                停用
              </PermissionButton>
              <PermissionButton
                v-else
                link
                type="success"
                action="action.referral.policy.enable"
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
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="邀请规则详情" size="860px" destroy-on-close>
      <div v-loading="detailLoading" class="detail-layout">
        <div v-if="detail" class="detail-actions">
          <PermissionButton link action="action.referral.policy.edit" @click="openEdit(detail.policyId)">
            编辑当前规则
          </PermissionButton>
          <PermissionButton
            v-if="detail.enabled === 1"
            link
            type="danger"
            action="action.referral.policy.disable"
            @click="openStatusDialog('disable', detail)"
          >
            停用当前规则
          </PermissionButton>
          <PermissionButton
            v-else
            link
            type="success"
            action="action.referral.policy.enable"
            @click="openStatusDialog('enable', detail)"
          >
            启用当前规则
          </PermissionButton>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>规则概览</h3></template>
          <div class="detail-grid">
            <div v-for="item in overviewBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>

        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>资格门槛</h3></template>
            <div class="detail-grid">
              <div v-for="item in conditionBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header><h3>频控与发放</h3></template>
            <div class="detail-grid">
              <div v-for="item in grantBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>发放规则 JSON</h3></template>
          <pre class="json-panel">{{ detail?.grantRuleJson || '--' }}</pre>
        </el-card>
      </div>
    </el-drawer>

    <el-dialog v-model="editorVisible" :title="editorMode === 'create' ? '新建邀请规则' : '编辑邀请规则'" width="760px" destroy-on-close>
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="规则名称">
              <el-input v-model="form.policyName" placeholder="例如：实名会员邀请策略" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实名要求">
              <el-select v-model="form.requireRealAuth" style="width: 100%">
                <el-option label="开启" :value="1" />
                <el-option label="关闭" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="自动发放">
              <el-select v-model="form.autoGrantEnabled" style="width: 100%">
                <el-option label="开启" :value="1" />
                <el-option label="关闭" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="档案完整度要求">
              <el-select v-model="form.requireProfileCompletion" style="width: 100%">
                <el-option label="开启" :value="1" />
                <el-option label="关闭" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="完整度阈值(%)">
              <el-input-number v-model="form.profileCompletionThreshold" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="同设备邀请上限">
              <el-input-number v-model="form.sameDeviceLimit" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单小时邀请上限">
              <el-input-number v-model="form.hourlyInviteLimit" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="发放规则 JSON">
              <el-input
                v-model="form.grantRuleJson"
                type="textarea"
                :rows="6"
                placeholder='{"grantType":"invite_eligibility","sourceType":"policy"}'
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEditor">
          {{ editorMode === 'create' ? '创建规则' : '保存修改' }}
        </el-button>
      </template>
    </el-dialog>

    <AuditConfirmDialog
      v-model="statusVisible"
      :title="statusMode === 'enable' ? '启用邀请规则' : '停用邀请规则'"
      :confirm-text="statusMode === 'enable' ? '确认启用' : '确认停用'"
      :placeholder="statusMode === 'enable' ? '请输入启用说明，可留空' : '请输入停用原因，可留空'"
      :loading="statusSubmitting"
      :meta="statusMeta"
      @submit="submitStatusChange"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createReferralPolicy,
  disableReferralPolicy,
  enableReferralPolicy,
  fetchReferralPolicies,
  fetchReferralPolicyDetail,
  updateReferralPolicy,
} from '@/api/referral'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { referralPolicyEnabledMap } from '@/constants/status'
import type {
  ReferralPolicyDetail,
  ReferralPolicyItem,
  ReferralPolicyQuery,
  ReferralPolicySavePayload,
} from '@/types/referral'
import { formatDateTime } from '@/utils/format'

type EditorMode = 'create' | 'edit'
type StatusMode = 'enable' | 'disable'
type ReferralPolicyEditorForm = Omit<ReferralPolicySavePayload, 'enabled'>

const loading = ref(false)
const detailLoading = ref(false)
const submitting = ref(false)
const statusSubmitting = ref(false)
const rows = ref<ReferralPolicyItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const editorVisible = ref(false)
const statusVisible = ref(false)
const detail = ref<ReferralPolicyDetail | null>(null)
const currentDetailId = ref<number | null>(null)
const currentRow = ref<ReferralPolicyItem | null>(null)
const editorMode = ref<EditorMode>('create')
const statusMode = ref<StatusMode>('enable')

const filters = reactive<ReferralPolicyQuery>({
  pageNo: 1,
  pageSize: 20,
  policyName: '',
  enabled: undefined,
})

const form = reactive<ReferralPolicyEditorForm>({
  policyName: '',
  requireRealAuth: 1,
  requireProfileCompletion: 0,
  profileCompletionThreshold: undefined,
  sameDeviceLimit: undefined,
  hourlyInviteLimit: undefined,
  autoGrantEnabled: 0,
  grantRuleJson: '',
})

const overviewBlocks = computed(() => {
  const policy = detail.value
  if (!policy) {
    return []
  }
  return [
    { label: '规则 ID', value: policy.policyId ?? '--' },
    { label: '规则名称', value: policy.policyName || '--' },
    { label: '启用状态', value: (referralPolicyEnabledMap[policy.enabled || 0] || referralPolicyEnabledMap[0]).label },
    { label: '更新人', value: policy.updateUserName || '--' },
    { label: '更新时间', value: formatDateTime(policy.lastUpdate) },
    { label: '版本备注', value: policy.versionRemark || '--' },
  ]
})

const conditionBlocks = computed(() => {
  const policy = detail.value
  return [
    { label: '实名要求', value: formatSwitch(policy?.requireRealAuth) },
    { label: '档案完整度要求', value: formatSwitch(policy?.requireProfileCompletion) },
    { label: '完整度阈值', value: formatPercent(policy?.profileCompletionThreshold) },
  ]
})

const grantBlocks = computed(() => {
  const policy = detail.value
  return [
    { label: '同设备邀请上限', value: formatLimit('次/设备', policy?.sameDeviceLimit) },
    { label: '单小时邀请上限', value: formatLimit('次/小时', policy?.hourlyInviteLimit) },
    { label: '自动发放', value: formatSwitch(policy?.autoGrantEnabled) },
  ]
})

const statusMeta = computed(() => [
  { label: '规则 ID', value: currentRow.value?.policyId },
  { label: '规则名称', value: currentRow.value?.policyName || '--' },
  {
    label: '当前状态',
    value: currentRow.value == null ? '--' : (referralPolicyEnabledMap[currentRow.value.enabled || 0] || referralPolicyEnabledMap[0]).label,
  },
])

function formatSwitch(value?: number | null) {
  if (value == null) {
    return '--'
  }
  return value === 1 ? '开启' : '关闭'
}

function formatProfileRequirement(row?: Pick<ReferralPolicyItem, 'requireProfileCompletion' | 'profileCompletionThreshold'> | null) {
  if (!row || row.requireProfileCompletion !== 1) {
    return '关闭'
  }
  return row.profileCompletionThreshold == null ? '开启' : `开启 / ${row.profileCompletionThreshold}%`
}

function formatPercent(value?: number | null) {
  return value == null ? '--' : `${value}%`
}

function formatLimit(unit: string, value?: number | null) {
  return value == null ? '--' : `${value}${unit}`
}

function resetEditorForm() {
  form.policyName = ''
  form.requireRealAuth = 1
  form.requireProfileCompletion = 0
  form.profileCompletionThreshold = undefined
  form.sameDeviceLimit = undefined
  form.hourlyInviteLimit = undefined
  form.autoGrantEnabled = 0
  form.grantRuleJson = ''
}

function assignForm(policy: ReferralPolicyDetail) {
  form.policyName = policy.policyName || ''
  form.requireRealAuth = policy.requireRealAuth == null ? 1 : policy.requireRealAuth
  form.requireProfileCompletion = policy.requireProfileCompletion == null ? 0 : policy.requireProfileCompletion
  form.profileCompletionThreshold = policy.profileCompletionThreshold == null ? undefined : policy.profileCompletionThreshold
  form.sameDeviceLimit = policy.sameDeviceLimit == null ? undefined : policy.sameDeviceLimit
  form.hourlyInviteLimit = policy.hourlyInviteLimit == null ? undefined : policy.hourlyInviteLimit
  form.autoGrantEnabled = policy.autoGrantEnabled == null ? 0 : policy.autoGrantEnabled
  form.grantRuleJson = policy.grantRuleJson || ''
}

function buildSavePayload(): ReferralPolicySavePayload {
  return {
    policyName: form.policyName.trim(),
    requireRealAuth: form.requireRealAuth,
    requireProfileCompletion: form.requireProfileCompletion,
    profileCompletionThreshold: form.profileCompletionThreshold,
    sameDeviceLimit: form.sameDeviceLimit,
    hourlyInviteLimit: form.hourlyInviteLimit,
    autoGrantEnabled: form.autoGrantEnabled,
    grantRuleJson: form.grantRuleJson?.trim() || undefined,
  }
}

async function loadList() {
  loading.value = true
  try {
    const result = await fetchReferralPolicies(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  currentDetailId.value = id
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await fetchReferralPolicyDetail(id)
    currentRow.value = rows.value.find((item) => item.policyId === id) || detail.value
  } finally {
    detailLoading.value = false
  }
}

function openCreate() {
  editorMode.value = 'create'
  currentRow.value = null
  resetEditorForm()
  editorVisible.value = true
}

async function openEdit(id: number) {
  editorMode.value = 'edit'
  currentRow.value = rows.value.find((item) => item.policyId === id) || null
  resetEditorForm()
  const policy = await fetchReferralPolicyDetail(id)
  assignForm(policy)
  currentRow.value = policy
  editorVisible.value = true
}

function openStatusDialog(mode: StatusMode, row: ReferralPolicyItem) {
  statusMode.value = mode
  currentRow.value = row
  statusVisible.value = true
}

async function submitEditor() {
  if (!form.policyName.trim()) {
    ElMessage.warning('请填写规则名称')
    return
  }

  if (form.grantRuleJson?.trim()) {
    try {
      JSON.parse(form.grantRuleJson)
    } catch {
      ElMessage.warning('发放规则 JSON 格式不正确')
      return
    }
  }

  submitting.value = true
  try {
    if (editorMode.value === 'create') {
      await createReferralPolicy({
        ...buildSavePayload(),
        enabled: 0,
      })
      ElMessage.success('邀请规则已创建')
    } else {
      const id = currentRow.value?.policyId
      if (!id) {
        ElMessage.warning('未找到可编辑的规则')
        return
      }
      await updateReferralPolicy(id, buildSavePayload())
      ElMessage.success('邀请规则已更新')
    }

    editorVisible.value = false
    await loadList()
    if (currentDetailId.value) {
      await openDetail(currentDetailId.value)
    }
  } finally {
    submitting.value = false
  }
}

async function submitStatusChange(reason: string) {
  const id = currentRow.value?.policyId
  if (!id) {
    return
  }

  statusSubmitting.value = true
  try {
    if (statusMode.value === 'enable') {
      await enableReferralPolicy(id, { reason: reason || undefined })
      ElMessage.success('邀请规则已启用')
    } else {
      await disableReferralPolicy(id, { reason: reason || undefined })
      ElMessage.success('邀请规则已停用')
    }

    statusVisible.value = false
    await loadList()
    if (currentDetailId.value) {
      await openDetail(currentDetailId.value)
    }
  } finally {
    statusSubmitting.value = false
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.policyName = ''
  filters.enabled = undefined
  loadList()
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.table-card,
.detail-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.table-actions,
.detail-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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

.detail-split {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.json-panel {
  margin: 0;
  padding: 16px;
  border-radius: 16px;
  background: rgba(47, 36, 27, 0.05);
  color: var(--kp-text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 960px) {
  .detail-split,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
