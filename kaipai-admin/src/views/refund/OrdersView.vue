<template>
  <PageContainer
    title="退款单"
    description="当前页面以 `/admin/refund/orders` 和退款聚合详情接口为准，支持待审核退款的通过与拒绝。"
  >
    <FilterPanel description="查询字段与后端 `RefundOrderQueryDTO` 保持一致。">
      <el-form :model="filters" inline>
        <el-form-item label="退款单号">
          <el-input v-model="filters.refundNo" placeholder="退款单号" clearable />
        </el-form-item>
        <el-form-item label="支付订单号">
          <el-input v-model="filters.paymentOrderNo" placeholder="支付订单号" clearable />
        </el-form-item>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="filters.auditStatus" clearable style="width: 160px">
            <el-option label="待审核" :value="0" />
            <el-option label="已通过" :value="1" />
            <el-option label="已拒绝" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="退款状态">
          <el-select v-model="filters.refundStatus" clearable style="width: 160px">
            <el-option label="待处理" :value="0" />
            <el-option label="退款中" :value="1" />
            <el-option label="退款成功" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="createdAtRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="创建开始"
            end-placeholder="创建结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            @change="handleCreatedAtRangeChange"
          />
        </el-form-item>
        <el-form-item label="审核时间">
          <el-date-picker
            v-model="auditedAtRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="审核开始"
            end-placeholder="审核结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            @change="handleAuditedAtRangeChange"
          />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadOrders">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="refundOrderId" label="退款单 ID" min-width="110" />
        <el-table-column prop="refundNo" label="退款单号" min-width="170" />
        <el-table-column prop="paymentOrderId" label="支付单 ID" min-width="120" />
        <el-table-column prop="userId" label="用户 ID" min-width="100" />
        <el-table-column label="退款金额" min-width="120">
          <template #default="{ row }">{{ formatCurrency(row.refundAmount) }}</template>
        </el-table-column>
        <el-table-column prop="refundReason" label="退款原因" min-width="220" show-overflow-tooltip />
        <el-table-column label="审核状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="refundAuditStatusMap[row.auditStatus ?? 0] || refundAuditStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="退款状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="refundStatusMap[row.refundStatus ?? 0] || refundStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="审核时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.auditedAt) }}</template>
        </el-table-column>
        <el-table-column label="退款完成时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.refundedAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.refundOrderId)">查看详情</el-button>
            <PermissionButton
              v-if="row.auditStatus === 0"
              link
              type="success"
              action="action.refund.approve"
              @click="openAudit('approve', row)"
            >
              审核通过
            </PermissionButton>
            <PermissionButton
              v-if="row.auditStatus === 0"
              link
              type="danger"
              action="action.refund.reject"
              @click="openAudit('reject', row)"
            >
              审核拒绝
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
          @current-change="loadOrders"
          @size-change="loadOrders"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="退款单详情" size="860px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-actions">
          <PermissionButton
            v-if="detail.auditStatus === 0"
            type="success"
            action="action.refund.approve"
            @click="openAudit('approve', currentRow)"
          >
            审核通过
          </PermissionButton>
          <PermissionButton
            v-if="detail.auditStatus === 0"
            type="danger"
            action="action.refund.reject"
            @click="openAudit('reject', currentRow)"
          >
            审核拒绝
          </PermissionButton>
        </div>

        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>退款信息</h3></template>
            <div class="detail-grid">
              <div v-for="item in refundBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header><h3>支付信息</h3></template>
            <div class="detail-grid">
              <div v-for="item in paymentBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>操作日志</h3></template>
          <el-table :data="detail.operateLogs || []" empty-text="暂无退款日志">
            <el-table-column prop="logId" label="日志 ID" min-width="110" />
            <el-table-column label="动作" min-width="120">
              <template #default="{ row }">{{ getLogActionLabel(row.actionType) }}</template>
            </el-table-column>
            <el-table-column prop="operatorId" label="操作人 ID" min-width="120" />
            <el-table-column prop="remark" label="备注" min-width="220" show-overflow-tooltip />
            <el-table-column label="时间" min-width="180">
              <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-drawer>

    <AuditConfirmDialog
      v-model="auditVisible"
      :title="auditMode === 'approve' ? '确认通过退款审核' : '确认拒绝退款审核'"
      :confirm-text="auditMode === 'approve' ? '确认通过' : '确认拒绝'"
      :reason-required="auditMode === 'reject'"
      :reason-label="auditMode === 'approve' ? '审核备注' : '拒绝原因'"
      :placeholder="auditMode === 'approve' ? '请输入审核备注，可留空' : '请输入拒绝原因'"
      :meta="auditMeta"
      @submit="submitAudit"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { approveRefundOrder, fetchRefundOrderDetail, fetchRefundOrders, rejectRefundOrder } from '@/api/refund'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { refundAuditStatusMap, refundStatusMap } from '@/constants/status'
import type { RefundOrderDetail, RefundOrderItem, RefundOrderQuery } from '@/types/refund'
import { formatCurrency, formatDateTime } from '@/utils/format'

type AuditMode = 'approve' | 'reject'

const loading = ref(false)
const rows = ref<RefundOrderItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<RefundOrderDetail | null>(null)
const currentRow = ref<RefundOrderItem | null>(null)
const currentDetailId = ref<number | null>(null)
const auditVisible = ref(false)
const auditMode = ref<AuditMode>('approve')

const filters = reactive<RefundOrderQuery>({
  pageNo: 1,
  pageSize: 20,
  refundNo: '',
  paymentOrderNo: '',
  userId: undefined,
  auditStatus: undefined,
  refundStatus: undefined,
  createdAtFrom: '',
  createdAtTo: '',
  auditedAtFrom: '',
  auditedAtTo: '',
})

const createdAtRange = ref<string[]>([])
const auditedAtRange = ref<string[]>([])

const refundBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '退款单 ID', value: detail.value.refundOrderId },
    { label: '退款单号', value: detail.value.refundNo },
    { label: '用户 ID', value: detail.value.userId ?? '--' },
    { label: '退款金额', value: formatCurrency(detail.value.refundAmount) },
    { label: '退款原因', value: detail.value.refundReason || '--' },
    { label: '审核状态', value: (refundAuditStatusMap[detail.value.auditStatus ?? 0] || refundAuditStatusMap[0]).label },
    { label: '退款状态', value: (refundStatusMap[detail.value.refundStatus ?? 0] || refundStatusMap[0]).label },
    { label: '审核备注', value: detail.value.auditRemark || '--' },
    { label: '审核人 ID', value: detail.value.auditorId ?? '--' },
    { label: '审核时间', value: formatDateTime(detail.value.auditedAt) },
    { label: '渠道退款单号', value: detail.value.channelRefundNo || '--' },
    { label: '退款完成时间', value: formatDateTime(detail.value.refundedAt) },
  ]
})

const paymentBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '支付单 ID', value: detail.value.paymentOrderId ?? '--' },
    { label: '支付单号', value: detail.value.paymentOrderNo || '--' },
    { label: '支付金额', value: formatCurrency(detail.value.paymentAmount) },
    { label: '支付状态', value: detail.value.paymentStatus ?? '--' },
    { label: '支付渠道', value: detail.value.payChannel || '--' },
    { label: '支付时间', value: formatDateTime(detail.value.paidAt) },
  ]
})

const auditMeta = computed(() => [
  { label: '退款单 ID', value: currentRow.value?.refundOrderId },
  { label: '退款单号', value: currentRow.value?.refundNo },
  { label: '退款金额', value: formatCurrency(currentRow.value?.refundAmount) },
  { label: '目标动作', value: auditMode.value === 'approve' ? '审核通过' : '审核拒绝' },
])

function handleCreatedAtRangeChange(value: string[] | null) {
  filters.createdAtFrom = value?.[0] || ''
  filters.createdAtTo = value?.[1] || ''
}

function handleAuditedAtRangeChange(value: string[] | null) {
  filters.auditedAtFrom = value?.[0] || ''
  filters.auditedAtTo = value?.[1] || ''
}

async function loadOrders() {
  loading.value = true
  try {
    const result = await fetchRefundOrders(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  currentDetailId.value = id
  currentRow.value = rows.value.find((item) => item.refundOrderId === id) || currentRow.value
  detail.value = await fetchRefundOrderDetail(id)
  detailVisible.value = true
}

function openAudit(mode: AuditMode, row: RefundOrderItem | null) {
  if (!row) {
    return
  }
  currentRow.value = row
  auditMode.value = mode
  auditVisible.value = true
}

async function submitAudit(auditRemark: string) {
  if (!currentRow.value) {
    return
  }
  if (auditMode.value === 'reject' && !auditRemark) {
    ElMessage.warning('请输入拒绝原因')
    return
  }

  if (auditMode.value === 'approve') {
    await approveRefundOrder(currentRow.value.refundOrderId, { auditRemark })
    ElMessage.success('退款审核已通过')
  } else {
    await rejectRefundOrder(currentRow.value.refundOrderId, { auditRemark })
    ElMessage.success('退款审核已拒绝')
  }

  auditVisible.value = false
  await loadOrders()
  if (currentDetailId.value) {
    detail.value = await fetchRefundOrderDetail(currentDetailId.value)
  }
}

function getLogActionLabel(actionType?: string | null) {
  if (actionType === 'approve') {
    return '审核通过'
  }
  if (actionType === 'reject') {
    return '审核拒绝'
  }
  return actionType || '--'
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.refundNo = ''
  filters.paymentOrderNo = ''
  filters.userId = undefined
  filters.auditStatus = undefined
  filters.refundStatus = undefined
  filters.createdAtFrom = ''
  filters.createdAtTo = ''
  filters.auditedAtFrom = ''
  filters.auditedAtTo = ''
  createdAtRange.value = []
  auditedAtRange.value = []
  loadOrders()
}

onMounted(loadOrders)
</script>

<style scoped lang="scss">
.table-card,
.detail-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
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

.detail-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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
