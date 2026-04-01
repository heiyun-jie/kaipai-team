<template>
  <PageContainer
    title="邀请资格"
    eyebrow="Referral Eligibility"
    description="管理邀请资格发放、延期与撤销，核对资格来源和邀请记录是否保持同一事实链。"
  >
    <FilterPanel description="按用户、资格码、资格类型和来源筛选资格记录，手工发放动作要求填写明确来源。">
      <el-form :model="filters" inline>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="filters.phone" placeholder="手机号" clearable />
        </el-form-item>
        <el-form-item label="资格类型">
          <el-input v-model="filters.grantType" placeholder="invite_eligibility" clearable />
        </el-form-item>
        <el-form-item label="资格码">
          <el-input v-model="filters.grantCode" placeholder="资格码" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="生效中" :value="1" />
            <el-option label="已过期" :value="2" />
            <el-option label="已撤销" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="filters.sourceType" placeholder="manual / policy / payment" clearable />
        </el-form-item>
      </el-form>
      <template #actions>
        <PermissionButton action="action.referral.eligibility.grant" type="primary" @click="openAction('grant')">
          手工发放
        </PermissionButton>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="grantId" label="资格 ID" min-width="110" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.nickname || '--' }}</strong>
              <span>{{ `${row.userId ?? '--'} / ${maskPhone(row.phone)}` }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="grantType" label="资格类型" min-width="150" />
        <el-table-column prop="grantCode" label="资格码" min-width="160" />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="entitlementStatusMap[row.status || 0] || fallbackStatusTag" />
          </template>
        </el-table-column>
        <el-table-column label="生效时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.effectiveTime) }}</template>
        </el-table-column>
        <el-table-column label="过期时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.expireTime) }}</template>
        </el-table-column>
        <el-table-column label="来源" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.sourceType || '--' }}</strong>
              <span>{{ row.sourceRefId ?? '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" min-width="220">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="openDetail(row.grantId)">查看详情</el-button>
              <PermissionButton v-if="isActive(row.status)" link action="action.referral.eligibility.extend" @click="openAction('extend', row)">
                延期
              </PermissionButton>
              <PermissionButton v-if="isActive(row.status)" link type="danger" action="action.referral.eligibility.revoke" @click="openAction('revoke', row)">
                撤销
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

    <el-drawer v-model="detailVisible" title="资格详情" size="860px" destroy-on-close>
      <div v-loading="detailLoading" class="detail-layout">
        <el-card class="detail-card" shadow="never">
          <template #header><h3>资格概览</h3></template>
          <div class="detail-grid">
            <div v-for="item in grantBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>

        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>来源信息</h3></template>
            <div class="detail-grid">
              <div v-for="item in sourceBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header><h3>关联策略</h3></template>
            <div class="detail-grid">
              <div v-for="item in policyBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>关联订单</h3></template>
          <div class="detail-grid">
            <div v-for="item in orderBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>操作日志</h3></template>
          <el-table :data="detail?.operatorLogSummary?.recentLogs || []" empty-text="暂无操作日志">
            <el-table-column prop="operationLogId" label="日志 ID" min-width="110" />
            <el-table-column label="操作人" min-width="140">
              <template #default="{ row }">{{ row.adminUserName || row.adminUserId || '--' }}</template>
            </el-table-column>
            <el-table-column prop="operationCode" label="操作" min-width="140" />
            <el-table-column label="结果" min-width="100">
              <template #default="{ row }">
                <StatusTag :label="row.operationResult === 1 ? '成功' : '失败'" :tone="row.operationResult === 1 ? 'success' : 'danger'" />
              </template>
            </el-table-column>
            <el-table-column label="时间" min-width="180">
              <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
            </el-table-column>
            <el-table-column label="上下文" min-width="260" show-overflow-tooltip>
              <template #default="{ row }">{{ row.extraContextJson || '--' }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-drawer>

    <el-dialog v-model="actionVisible" :title="actionDialogTitle" width="620px" destroy-on-close>
      <el-form label-position="top">
        <template v-if="actionMode === 'grant'">
          <el-form-item label="用户 ID">
            <el-input v-model.number="form.userId" />
          </el-form-item>
          <el-form-item label="资格类型">
            <el-input v-model="form.grantType" placeholder="invite_eligibility" />
          </el-form-item>
          <el-form-item label="资格码">
            <el-input v-model="form.grantCode" placeholder="例如 invite_manual_001" />
          </el-form-item>
          <el-form-item label="生效时间">
            <el-date-picker v-model="form.effectiveTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="过期时间">
            <el-date-picker v-model="form.expireTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="来源类型">
            <el-input v-model="form.sourceType" placeholder="manual" />
          </el-form-item>
          <el-form-item label="来源单据 ID">
            <el-input v-model.number="form.sourceRefId" />
          </el-form-item>
        </template>

        <template v-else>
          <el-form-item label="资格 ID">
            <el-input :model-value="form.grantId" disabled />
          </el-form-item>
          <el-form-item label="资格码">
            <el-input :model-value="currentRow?.grantCode || '--'" disabled />
          </el-form-item>
          <el-form-item v-if="actionMode === 'extend'" label="新的过期时间">
            <el-date-picker v-model="form.expireTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
        </template>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAction">确认</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  extendReferralEligibility,
  fetchReferralEligibilityDetail,
  fetchReferralEligibilityList,
  grantReferralEligibility,
  revokeReferralEligibility,
} from '@/api/referral'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { entitlementStatusMap } from '@/constants/status'
import type {
  ReferralEligibilityDetail,
  ReferralEligibilityItem,
  ReferralEligibilityQuery,
} from '@/types/referral'
import { formatCurrency, formatDateTime, maskPhone } from '@/utils/format'

type ActionMode = 'grant' | 'extend' | 'revoke'

const fallbackStatusTag = { label: '未知', tone: 'info' as const }

const loading = ref(false)
const detailLoading = ref(false)
const submitting = ref(false)
const rows = ref<ReferralEligibilityItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const actionVisible = ref(false)
const detail = ref<ReferralEligibilityDetail | null>(null)
const currentDetailId = ref<number | null>(null)
const currentRow = ref<ReferralEligibilityItem | null>(null)
const actionMode = ref<ActionMode>('grant')

const filters = reactive<ReferralEligibilityQuery>({
  pageNo: 1,
  pageSize: 20,
  userId: undefined,
  phone: '',
  grantType: '',
  grantCode: '',
  status: undefined,
  sourceType: '',
  effectiveFrom: undefined,
  effectiveTo: undefined,
  expireFrom: undefined,
  expireTo: undefined,
})

const form = reactive({
  grantId: undefined as number | undefined,
  userId: undefined as number | undefined,
  grantType: 'invite_eligibility',
  grantCode: '',
  effectiveTime: '',
  expireTime: '',
  sourceType: 'manual',
  sourceRefId: undefined as number | undefined,
  remark: '',
})

const actionDialogTitle = computed(() => {
  if (actionMode.value === 'extend') {
    return '延期邀请资格'
  }
  if (actionMode.value === 'revoke') {
    return '撤销邀请资格'
  }
  return '手工发放邀请资格'
})

const grantBlocks = computed(() => {
  const info = detail.value?.grantInfo
  if (!info) {
    return []
  }
  return [
    { label: '资格 ID', value: info.grantId ?? '--' },
    { label: '用户 ID', value: info.userId ?? '--' },
    { label: '用户名', value: info.userName || '--' },
    { label: '昵称', value: info.nickname || '--' },
    { label: '手机号', value: maskPhone(info.phone) },
    { label: '实名状态', value: formatRealAuthStatus(info.realAuthStatus) },
    { label: '有效邀请数', value: info.validInviteCount ?? 0 },
    { label: '资格类型', value: info.grantType || '--' },
    { label: '资格码', value: info.grantCode || '--' },
    { label: '状态', value: (entitlementStatusMap[info.status || 0] || fallbackStatusTag).label },
    { label: '生效时间', value: formatDateTime(info.effectiveTime) },
    { label: '过期时间', value: formatDateTime(info.expireTime) },
    { label: '备注', value: info.remark || '--' },
    { label: '创建人', value: info.createUserName || info.createUserId || '--' },
    { label: '创建时间', value: formatDateTime(info.createTime) },
    { label: '最后更新时间', value: formatDateTime(info.lastUpdate) },
  ]
})

const sourceBlocks = computed(() => {
  const source = detail.value?.sourceInfo
  return [
    { label: '来源类型', value: source?.sourceType || '--' },
    { label: '来源单据 ID', value: source?.sourceRefId ?? '--' },
    { label: '来源标题', value: source?.sourceTitle || '--' },
    { label: '来源状态', value: source?.sourceStatus || '--' },
    { label: '关联业务类型', value: source?.relatedBizType || '--' },
    { label: '关联业务 ID', value: source?.relatedBizId ?? '--' },
  ]
})

const policyBlocks = computed(() => {
  const policy = detail.value?.relatedPolicy
  return [
    { label: '策略 ID', value: policy?.policyId ?? '--' },
    { label: '策略名称', value: policy?.policyName || '--' },
    { label: '启用状态', value: policy?.enabled == null ? '--' : policy.enabled === 1 ? '启用中' : '已停用' },
    { label: '自动发放', value: policy?.autoGrantEnabled == null ? '--' : policy.autoGrantEnabled === 1 ? '开启' : '关闭' },
    { label: '更新人', value: policy?.updateUserName || '--' },
    { label: '更新时间', value: formatDateTime(policy?.lastUpdate) },
  ]
})

const orderBlocks = computed(() => {
  const order = detail.value?.relatedOrder
  return [
    { label: '支付单 ID', value: order?.paymentOrderId ?? '--' },
    { label: '订单号', value: order?.orderNo || '--' },
    { label: '业务类型', value: order?.bizType || '--' },
    { label: '业务 ID', value: order?.bizRefId ?? '--' },
    { label: '金额', value: formatCurrency(order?.amount) },
    { label: '支付状态', value: order?.payStatus ?? '--' },
    { label: '支付渠道', value: order?.payChannel || '--' },
    { label: '支付时间', value: formatDateTime(order?.paidAt) },
  ]
})

function formatRealAuthStatus(status?: number | null) {
  if (status === 2) {
    return '已实名'
  }
  if (status === 1) {
    return '审核中'
  }
  if (status === 3) {
    return '已拒绝'
  }
  return '未实名'
}

function isActive(status?: number | null) {
  return status === 1
}

function resetActionForm() {
  form.grantId = undefined
  form.userId = undefined
  form.grantType = 'invite_eligibility'
  form.grantCode = ''
  form.effectiveTime = ''
  form.expireTime = ''
  form.sourceType = 'manual'
  form.sourceRefId = undefined
  form.remark = ''
}

async function loadList() {
  loading.value = true
  try {
    const result = await fetchReferralEligibilityList(filters)
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
    detail.value = await fetchReferralEligibilityDetail(id)
  } finally {
    detailLoading.value = false
  }
}

function openAction(mode: ActionMode, row?: ReferralEligibilityItem) {
  actionMode.value = mode
  actionVisible.value = true
  currentRow.value = row || null
  resetActionForm()
  if (!row) {
    return
  }
  form.grantId = row.grantId
  form.userId = row.userId == null ? undefined : row.userId
  form.grantType = row.grantType || 'invite_eligibility'
  form.grantCode = row.grantCode || ''
  form.expireTime = row.expireTime || ''
}

async function submitAction() {
  submitting.value = true
  try {
    if (actionMode.value === 'grant') {
      if (!form.userId || !form.grantType || !form.grantCode || !form.sourceType) {
        ElMessage.warning('请填写完整的资格发放信息')
        return
      }
      await grantReferralEligibility({
        userId: form.userId,
        grantType: form.grantType,
        grantCode: form.grantCode,
        effectiveTime: form.effectiveTime || undefined,
        expireTime: form.expireTime || undefined,
        sourceType: form.sourceType,
        sourceRefId: form.sourceRefId,
        remark: form.remark || undefined,
      })
      ElMessage.success('资格发放已提交')
    } else if (actionMode.value === 'extend') {
      if (!form.grantId || !form.expireTime) {
        ElMessage.warning('请填写新的过期时间')
        return
      }
      await extendReferralEligibility({
        grantId: form.grantId,
        expireTime: form.expireTime,
        remark: form.remark || undefined,
      })
      ElMessage.success('资格延期已提交')
    } else {
      if (!form.grantId) {
        ElMessage.warning('未找到可撤销的资格记录')
        return
      }
      await revokeReferralEligibility({
        grantId: form.grantId,
        remark: form.remark || undefined,
      })
      ElMessage.success('资格撤销已提交')
    }

    actionVisible.value = false
    await loadList()
    if (currentDetailId.value) {
      await openDetail(currentDetailId.value)
    }
  } finally {
    submitting.value = false
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.userId = undefined
  filters.phone = ''
  filters.grantType = ''
  filters.grantCode = ''
  filters.status = undefined
  filters.sourceType = ''
  filters.effectiveFrom = undefined
  filters.effectiveTo = undefined
  filters.expireFrom = undefined
  filters.expireTo = undefined
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

.table-actions {
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

@media (max-width: 960px) {
  .detail-split,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
