<template>
  <PageContainer :title="title" eyebrow="Verify Review" :description="description">
    <section class="verify-overview">
      <article v-for="card in overviewCards" :key="card.label" class="verify-overview__card">
        <div class="verify-overview__head">
          <p>{{ card.label }}</p>
          <StatusTag v-if="card.tone" :label="card.badge" :tone="card.tone" />
          <span v-else class="verify-overview__badge">{{ card.badge }}</span>
        </div>
        <strong>{{ card.value }}</strong>
        <span>{{ card.hint }}</span>
      </article>
    </section>

    <FilterPanel
      title="审核筛选"
      description="优先处理待审核申请；如需复盘，可切换状态快速回看已完成结果。"
    >
      <el-form :model="filters" inline class="verify-filter-form">
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部状态" style="width: 200px">
            <el-option label="待审核" :value="1" />
            <el-option label="已通过" :value="2" />
            <el-option label="已拒绝" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <div class="verify-table__header">
        <div>
          <p class="verify-table__eyebrow">{{ mode === 'pending' ? 'PENDING QUEUE' : 'HISTORY REVIEW' }}</p>
          <h3>{{ tableTitle }}</h3>
        </div>
        <span class="verify-table__hint">{{ tableHint }}</span>
      </div>
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="verificationId" label="申请单号" min-width="120" />
        <el-table-column prop="userId" label="用户 ID" min-width="100" />
        <el-table-column label="用户信息" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.userName }}</strong>
              <span>{{ row.phone || '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="realName" label="真实姓名" min-width="120" />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="verifyStatusMap[row.status] || verifyStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="提交时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.submitTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.verificationId)">查看详情</el-button>
            <PermissionButton
              v-if="mode === 'pending' && row.status === 1"
              link
              type="success"
              action="action.verify.approve"
              @click="openAudit('approve', row)"
            >
              审核通过
            </PermissionButton>
            <PermissionButton
              v-if="mode === 'pending' && row.status === 1"
              link
              type="danger"
              action="action.verify.reject"
              @click="openAudit('reject', row)"
            >
              审核拒绝
            </PermissionButton>
          </template>
        </el-table-column>
        <template #empty>
          <div class="verify-empty">
            <strong>{{ emptyTitle }}</strong>
            <p>{{ emptyDescription }}</p>
          </div>
        </template>
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="filters.pageNo"
          v-model:page-size="filters.pageSize"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="认证申请详情" size="520px">
      <div v-if="detail" class="verify-detail">
        <section class="verify-detail__hero">
          <div>
            <p>审核状态</p>
            <strong>{{ (verifyStatusMap[detail.status] || verifyStatusMap[0]).label }}</strong>
          </div>
          <StatusTag v-bind="verifyStatusMap[detail.status] || verifyStatusMap[0]" />
        </section>
        <div class="detail-grid">
        <div class="detail-block">
          <span>申请单号</span>
          <strong>{{ detail.verificationId }}</strong>
        </div>
        <div class="detail-block">
          <span>用户</span>
          <strong>{{ detail.userName }} / {{ detail.userId }}</strong>
        </div>
        <div class="detail-block">
          <span>手机号</span>
          <strong>{{ detail.phone || '--' }}</strong>
        </div>
        <div class="detail-block">
          <span>真实姓名</span>
          <strong>{{ detail.realName }}</strong>
        </div>
        <div class="detail-block">
          <span>身份证</span>
          <strong>{{ maskText(detail.idCardNoCipher) }}</strong>
        </div>
        <div class="detail-block">
          <span>演员认证结果</span>
          <strong>{{ detail.actorCertified ? '已回写' : '未回写' }}</strong>
        </div>
        <div class="detail-block">
          <span>提交时间</span>
          <strong>{{ formatDateTime(detail.submitTime) }}</strong>
        </div>
        <div class="detail-block">
          <span>审核时间</span>
          <strong>{{ formatDateTime(detail.reviewedAt) }}</strong>
        </div>
        <div class="detail-block detail-block--wide">
          <span>拒绝原因</span>
          <strong>{{ detail.rejectReason || '--' }}</strong>
        </div>
        </div>
      </div>
    </el-drawer>

    <AuditConfirmDialog
      v-model="auditVisible"
      :title="auditMode === 'approve' ? '确认审核通过' : '确认审核拒绝'"
      :confirm-text="auditMode === 'approve' ? '确认通过' : '确认拒绝'"
      :reason-label="auditMode === 'approve' ? '审核备注' : '拒绝原因'"
      :placeholder="auditMode === 'approve' ? '请输入审核备注' : '请输入拒绝原因'"
      :meta="auditMeta"
      @submit="submitAudit"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { approveVerify, fetchVerifyDetail, fetchVerifyList, rejectVerify } from '@/api/verify'
import { verifyStatusMap } from '@/constants/status'
import { formatDateTime, maskText } from '@/utils/format'
import type { VerifyDetail, VerifyListItem, VerifyQuery } from '@/types/verify'

const props = defineProps<{
  mode: 'pending' | 'history'
}>()

const title = computed(() => (props.mode === 'pending' ? '实名认证待审核' : '实名认证历史'))
const description = computed(() =>
  props.mode === 'pending'
    ? '集中处理待审核实名认证申请，支持查看资料并完成通过或拒绝。'
    : '按状态回看历史审核记录，便于复核处理结果和追踪进度。'
)

const loading = ref(false)
const rows = ref<VerifyListItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<VerifyDetail | null>(null)
const auditVisible = ref(false)
const auditMode = ref<'approve' | 'reject'>('approve')
const currentRow = ref<VerifyListItem | null>(null)

const filters = reactive<VerifyQuery>({
  userId: undefined,
  status: props.mode === 'pending' ? 1 : undefined,
  pageNo: 1,
  pageSize: 20,
})

const auditMeta = computed(() => [
  { label: '申请单号', value: currentRow.value?.verificationId },
  { label: '用户', value: currentRow.value?.userName },
  { label: '目标动作', value: auditMode.value === 'approve' ? '审核通过' : '审核拒绝' },
])

const currentStatusMeta = computed(() => {
  if (filters.status == null) {
    return {
      label: '全部状态',
      tone: 'info' as const,
    }
  }
  return verifyStatusMap[filters.status] || { label: `状态 ${filters.status}`, tone: 'info' as const }
})

const overviewCards = computed(() => [
  {
    label: '当前模式',
    badge: props.mode === 'pending' ? '待办' : '历史',
    tone: props.mode === 'pending' ? ('warning' as const) : ('info' as const),
    value: props.mode === 'pending' ? '优先处理待审核申请' : '回看历史审核结果',
    hint: props.mode === 'pending' ? '本页聚焦仍需决策的实名申请。' : '用于复盘审核结果和追踪处理记录。',
  },
  {
    label: '筛选状态',
    badge: currentStatusMeta.value.label,
    tone: currentStatusMeta.value.tone,
    value: filters.userId ? `用户 ${filters.userId}` : '当前未限定用户',
    hint: filters.userId ? '已按指定用户过滤申请记录。' : '可继续按用户 ID 缩小审核范围。',
  },
  {
    label: '列表规模',
    badge: '清单',
    tone: null,
    value: `${total.value} 条`,
    hint: props.mode === 'pending' ? '当前查询条件下待处理申请总数。' : '当前查询条件下历史记录总数。',
  },
])

const tableTitle = computed(() => (props.mode === 'pending' ? '待审核申请清单' : '历史审核记录'))
const tableHint = computed(() =>
  props.mode === 'pending' ? '支持直接查看资料并完成审核决策。' : '用于复盘通过、拒绝和已处理记录。',
)
const emptyTitle = computed(() => (props.mode === 'pending' ? '当前没有待审核申请' : '当前条件下没有历史记录'))
const emptyDescription = computed(() =>
  props.mode === 'pending'
    ? '可以调整筛选条件，或稍后刷新列表继续查看新进入队列的申请。'
    : '可以切换状态或清空用户条件，回看其他审核结果。',
)

async function loadList() {
  loading.value = true
  try {
    const result = await fetchVerifyList(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchVerifyDetail(id)
  detailVisible.value = true
}

function openAudit(mode: 'approve' | 'reject', row: VerifyListItem) {
  auditMode.value = mode
  currentRow.value = row
  auditVisible.value = true
}

async function submitAudit(remark: string) {
  if (!currentRow.value) {
    return
  }
  if (!remark) {
    ElMessage.warning(auditMode.value === 'approve' ? '请输入审核备注' : '请输入拒绝原因')
    return
  }

  if (auditMode.value === 'approve') {
    await approveVerify(currentRow.value.verificationId, { remark })
  } else {
    await rejectVerify(currentRow.value.verificationId, { remark })
  }

  ElMessage.success('审核操作已提交')
  auditVisible.value = false
  loadList()
}

function resetFilters() {
  filters.userId = undefined
  filters.status = props.mode === 'pending' ? 1 : undefined
  filters.pageNo = 1
  loadList()
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.verify-overview {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.verify-overview__card {
  display: grid;
  gap: 12px;
  min-height: 172px;
  padding: 22px 22px 20px;
  border: 1px solid rgba(196, 77, 52, 0.12);
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(196, 77, 52, 0.1), transparent 28%),
    linear-gradient(180deg, rgba(255, 252, 247, 0.96), rgba(247, 240, 231, 0.92));
  box-shadow: 0 14px 28px rgba(63, 42, 20, 0.07);
}

.verify-overview__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;

  p {
    margin: 0;
    color: var(--kp-text-secondary);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
}

.verify-overview__badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: var(--kp-accent-deep);
  font-size: 12px;
  font-weight: 700;
}

.verify-overview__card strong {
  font-size: 24px;
  line-height: 1.35;
}

.verify-overview__card span {
  color: var(--kp-text-secondary);
  line-height: 1.75;
}

.verify-filter-form {
  align-items: center;
}

.verify-filter-form :deep(.el-input),
.verify-filter-form :deep(.el-select) {
  width: 200px;
}

.verify-table__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.verify-table__eyebrow {
  margin: 0 0 8px;
  color: var(--kp-accent-deep);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.verify-table__header h3 {
  margin: 0;
  font-size: 20px;
}

.verify-table__hint {
  max-width: 280px;
  color: var(--kp-text-secondary);
  line-height: 1.7;
  text-align: right;
}

.table-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.verify-empty {
  display: grid;
  gap: 8px;
  padding: 32px 16px 36px;
  text-align: center;

  strong {
    font-size: 20px;
  }

  p {
    max-width: 420px;
    margin: 0 auto;
    color: var(--kp-text-secondary);
    line-height: 1.75;
  }
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

.detail-grid {
  display: grid;
  gap: 14px;
}

.verify-detail {
  display: grid;
  gap: 18px;
}

.verify-detail__hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px 18px 18px 20px;
  border: 1px solid rgba(196, 77, 52, 0.12);
  border-radius: 22px;
  background:
    radial-gradient(circle at top right, rgba(196, 77, 52, 0.1), transparent 26%),
    linear-gradient(180deg, rgba(255, 252, 247, 0.96), rgba(247, 240, 231, 0.92));

  p {
    margin: 0 0 6px;
    color: var(--kp-text-secondary);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  strong {
    font-size: 24px;
    line-height: 1.2;
  }
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
  }
}

.detail-block--wide {
  min-height: 96px;
}

@media (max-width: 1100px) {
  .verify-overview {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .verify-filter-form :deep(.el-input),
  .verify-filter-form :deep(.el-select) {
    width: 100%;
  }

  .verify-table__header,
  .verify-detail__hero {
    display: grid;
  }

  .verify-table__hint {
    max-width: none;
    text-align: left;
  }
}
</style>
