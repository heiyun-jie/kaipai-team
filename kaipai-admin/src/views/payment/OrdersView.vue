<template>
  <PageContainer
    title="支付订单"
    description="当前页面以 `/admin/payment/orders` 聚合详情为准，展示订单、产品、支付流水与退款摘要。"
  >
    <FilterPanel description="按后端当前开放字段筛选支付订单。">
      <el-form :model="filters" inline>
        <el-form-item label="订单号">
          <el-input v-model="filters.orderNo" placeholder="支付订单号" clearable />
        </el-form-item>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="filters.phone" placeholder="手机号" clearable />
        </el-form-item>
        <el-form-item label="支付状态">
          <el-select v-model="filters.payStatus" clearable style="width: 160px">
            <el-option label="待支付" :value="0" />
            <el-option label="已支付" :value="1" />
            <el-option label="已关闭" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付渠道">
          <el-input v-model="filters.payChannel" placeholder="payChannel" clearable />
        </el-form-item>
        <el-form-item label="产品 ID">
          <el-input v-model.number="filters.productId" placeholder="产品 ID" clearable />
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
        <el-form-item label="支付时间">
          <el-date-picker
            v-model="paidAtRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="支付开始"
            end-placeholder="支付结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            @change="handlePaidAtRangeChange"
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
        <el-table-column prop="paymentOrderId" label="订单 ID" min-width="110" />
        <el-table-column prop="orderNo" label="订单号" min-width="180" />
        <el-table-column prop="userId" label="用户 ID" min-width="100" />
        <el-table-column prop="phone" label="手机号" min-width="140" />
        <el-table-column label="产品" min-width="220">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.productName || '--' }}</strong>
              <span>{{ row.productCode || '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="bizType" label="业务类型" min-width="160" />
        <el-table-column label="金额" min-width="120">
          <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="支付状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="paymentOrderStatusMap[row.payStatus ?? -1] || fallbackOrderStatus(row.payStatus)" />
          </template>
        </el-table-column>
        <el-table-column prop="payChannel" label="渠道" min-width="120" />
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="支付时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.paidAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.paymentOrderId)">查看详情</el-button>
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

    <el-drawer v-model="detailVisible" title="支付订单详情" size="920px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>订单信息</h3></template>
            <div class="detail-grid">
              <div v-for="item in orderBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>产品信息</h3></template>
            <div class="detail-grid">
              <div v-for="item in productBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>支付摘要</h3></template>
            <div class="detail-grid">
              <div v-for="item in paymentBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
          <el-card class="detail-card" shadow="never">
            <template #header><h3>退款摘要</h3></template>
            <div class="detail-grid">
              <div v-for="item in refundBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>关联流水</h3></template>
          <el-table :data="detail.paymentInfo?.transactions || []" empty-text="暂无支付流水">
            <el-table-column prop="transactionId" label="流水 ID" min-width="110" />
            <el-table-column prop="channelTradeNo" label="渠道流水号" min-width="180" />
            <el-table-column prop="channel" label="渠道" min-width="120" />
            <el-table-column prop="tradeType" label="交易类型" min-width="120" />
            <el-table-column label="金额" min-width="120">
              <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="状态" min-width="100">
              <template #default="{ row }">
                <StatusTag v-bind="paymentTransactionStatusMap[row.status ?? -1] || fallbackTransactionStatus(row.status)" />
              </template>
            </el-table-column>
            <el-table-column label="回调时间" min-width="180">
              <template #default="{ row }">{{ formatDateTime(row.callbackTime) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchPaymentOrderDetail, fetchPaymentOrders } from '@/api/payment'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { paymentOrderStatusMap, paymentTransactionStatusMap, refundAuditStatusMap, refundStatusMap } from '@/constants/status'
import type { PaymentOrderDetail, PaymentOrderListItem, PaymentOrderQuery } from '@/types/payment'
import { formatCurrency, formatDateTime } from '@/utils/format'

const loading = ref(false)
const rows = ref<PaymentOrderListItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<PaymentOrderDetail | null>(null)

const filters = reactive<PaymentOrderQuery>({
  pageNo: 1,
  pageSize: 20,
  orderNo: '',
  userId: undefined,
  phone: '',
  payStatus: undefined,
  payChannel: '',
  bizType: '',
  productId: undefined,
  createdAtFrom: '',
  createdAtTo: '',
  paidAtFrom: '',
  paidAtTo: '',
})

const createdAtRange = ref<string[]>([])
const paidAtRange = ref<string[]>([])

const orderBlocks = computed(() => {
  const order = detail.value?.orderInfo
  if (!order) return []
  return [
    { label: '订单 ID', value: order.paymentOrderId ?? '--' },
    { label: '订单号', value: order.orderNo || '--' },
    { label: '用户 ID', value: order.userId ?? '--' },
    { label: '手机号', value: order.phone || '--' },
    { label: '业务类型', value: order.bizType || '--' },
    { label: '业务引用 ID', value: order.bizRefId ?? '--' },
    { label: '金额', value: formatCurrency(order.amount) },
    { label: '币种', value: order.currencyCode || '--' },
    { label: '支付状态', value: (paymentOrderStatusMap[order.payStatus ?? -1] || fallbackOrderStatus(order.payStatus)).label },
    { label: '支付渠道', value: order.payChannel || '--' },
    { label: '创建时间', value: formatDateTime(order.createTime) },
    { label: '支付时间', value: formatDateTime(order.paidAt) },
  ]
})

const productBlocks = computed(() => {
  const product = detail.value?.productInfo
  if (!product) return []
  return [
    { label: '产品 ID', value: product.productId ?? '--' },
    { label: '产品编码', value: product.productCode || '--' },
    { label: '产品名称', value: product.productName || '--' },
    { label: '会员层级', value: product.membershipTier ?? '--' },
    { label: '时长(天)', value: product.durationDays ?? '--' },
  ]
})

const paymentBlocks = computed(() => {
  const payment = detail.value?.paymentInfo
  return [
    { label: '流水数量', value: payment?.transactionCount ?? 0 },
  ]
})

const refundBlocks = computed(() => {
  const refund = detail.value?.refundSummary
  return [
    { label: '退款单数量', value: refund?.totalRefundCount ?? 0 },
    { label: '累计退款金额', value: formatCurrency(refund?.totalRefundAmount) },
    { label: '最新退款单 ID', value: refund?.latestRefundOrderId ?? '--' },
    { label: '最新退款单号', value: refund?.latestRefundNo || '--' },
    { label: '最新审核状态', value: refund?.latestAuditStatus == null ? '--' : (refundAuditStatusMap[refund.latestAuditStatus] || { label: `状态 ${refund.latestAuditStatus}` }).label },
    { label: '最新退款状态', value: refund?.latestRefundStatus == null ? '--' : (refundStatusMap[refund.latestRefundStatus] || { label: `状态 ${refund.latestRefundStatus}` }).label },
  ]
})

function fallbackOrderStatus(status?: number | null) {
  return { label: `状态 ${status ?? '--'}`, tone: 'info' as const }
}

function fallbackTransactionStatus(status?: number | null) {
  return { label: `状态 ${status ?? '--'}`, tone: 'info' as const }
}

function handleCreatedAtRangeChange(value: string[] | null) {
  filters.createdAtFrom = value?.[0] || ''
  filters.createdAtTo = value?.[1] || ''
}

function handlePaidAtRangeChange(value: string[] | null) {
  filters.paidAtFrom = value?.[0] || ''
  filters.paidAtTo = value?.[1] || ''
}

async function loadOrders() {
  loading.value = true
  try {
    const result = await fetchPaymentOrders(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchPaymentOrderDetail(id)
  detailVisible.value = true
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.orderNo = ''
  filters.userId = undefined
  filters.phone = ''
  filters.payStatus = undefined
  filters.payChannel = ''
  filters.bizType = ''
  filters.productId = undefined
  filters.createdAtFrom = ''
  filters.createdAtTo = ''
  filters.paidAtFrom = ''
  filters.paidAtTo = ''
  createdAtRange.value = []
  paidAtRange.value = []
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
