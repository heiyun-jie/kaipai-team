<template>
  <PageContainer
    title="支付流水"
    description="回看支付流水状态与回调结果，便于核对交易处理情况。"
  >
    <FilterPanel description="按支付订单、渠道流水和回调时间筛选交易记录。">
      <el-form :model="filters" inline>
        <el-form-item label="支付订单号">
          <el-input v-model="filters.paymentOrderNo" placeholder="支付订单号" clearable />
        </el-form-item>
        <el-form-item label="渠道流水号">
          <el-input v-model="filters.channelTradeNo" placeholder="渠道流水号" clearable />
        </el-form-item>
        <el-form-item label="渠道">
          <el-input v-model="filters.channel" placeholder="渠道" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="待回调" :value="0" />
            <el-option label="成功" :value="1" />
            <el-option label="失败" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="回调时间">
          <el-date-picker
            v-model="callbackRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="回调开始"
            end-placeholder="回调结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            @change="handleCallbackRangeChange"
          />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadTransactions">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="transactionId" label="流水 ID" min-width="110" />
        <el-table-column prop="paymentOrderNo" label="支付订单号" min-width="180" />
        <el-table-column prop="channelTradeNo" label="渠道流水号" min-width="200" />
        <el-table-column prop="channel" label="渠道" min-width="120" />
        <el-table-column prop="tradeType" label="交易类型" min-width="120" />
        <el-table-column label="金额" min-width="120">
          <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <StatusTag v-bind="paymentTransactionStatusMap[row.status ?? -1] || fallbackStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column label="回调时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.callbackTime) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.transactionId)">查看详情</el-button>
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
          @current-change="loadTransactions"
          @size-change="loadTransactions"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="支付流水详情" size="860px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-grid">
          <div v-for="item in infoBlocks" :key="item.label" class="detail-block">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>回调摘要</h3></template>
          <div class="detail-grid">
            <div v-for="item in callbackBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>回调原文预览</h3></template>
          <pre class="json-block">{{ detail.callbackPayloadSummary?.payloadPreview || '--' }}</pre>
        </el-card>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchPaymentTransactionDetail, fetchPaymentTransactions } from '@/api/payment'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { paymentOrderStatusMap, paymentTransactionStatusMap } from '@/constants/status'
import type { PaymentTransactionDetail, PaymentTransactionListItem, PaymentTransactionQuery } from '@/types/payment'
import { formatCurrency, formatDateTime } from '@/utils/format'

const loading = ref(false)
const rows = ref<PaymentTransactionListItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<PaymentTransactionDetail | null>(null)

const filters = reactive<PaymentTransactionQuery>({
  pageNo: 1,
  pageSize: 20,
  paymentOrderNo: '',
  channelTradeNo: '',
  channel: '',
  status: undefined,
  callbackFrom: '',
  callbackTo: '',
})

const callbackRange = ref<string[]>([])

const infoBlocks = computed(() => {
  const info = detail.value?.transactionInfo
  if (!info) return []
  return [
    { label: '流水 ID', value: info.transactionId ?? '--' },
    { label: '支付订单 ID', value: info.paymentOrderId ?? '--' },
    { label: '支付订单号', value: info.paymentOrderNo || '--' },
    { label: '用户 ID', value: info.userId ?? '--' },
    { label: '业务类型', value: info.bizType || '--' },
    { label: '产品', value: info.productName || info.productCode || '--' },
    { label: '订单金额', value: formatCurrency(info.orderAmount) },
    { label: '流水金额', value: formatCurrency(info.amount) },
    { label: '订单状态', value: (paymentOrderStatusMap[info.payStatus ?? -1] || fallbackStatus(info.payStatus)).label },
    { label: '流水状态', value: (paymentTransactionStatusMap[info.status ?? -1] || fallbackStatus(info.status)).label },
    { label: '支付渠道', value: info.payChannel || info.channel || '--' },
    { label: '交易类型', value: info.tradeType || '--' },
    { label: '渠道流水号', value: info.channelTradeNo || '--' },
    { label: '支付时间', value: formatDateTime(info.paidAt) },
    { label: '回调时间', value: formatDateTime(info.callbackTime) },
    { label: '创建时间', value: formatDateTime(info.createTime) },
  ]
})

const callbackBlocks = computed(() => {
  const callback = detail.value?.callbackPayloadSummary
  return [
    { label: '是否有回调内容', value: callback?.hasPayload ? '是' : '否' },
    { label: '回调内容长度', value: callback?.payloadLength ?? 0 },
    { label: '回调时间', value: formatDateTime(callback?.callbackTime) },
  ]
})

function fallbackStatus(status?: number | null) {
  return { label: `状态 ${status ?? '--'}`, tone: 'info' as const }
}

function handleCallbackRangeChange(value: string[] | null) {
  filters.callbackFrom = value?.[0] || ''
  filters.callbackTo = value?.[1] || ''
}

async function loadTransactions() {
  loading.value = true
  try {
    const result = await fetchPaymentTransactions(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchPaymentTransactionDetail(id)
  detailVisible.value = true
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.paymentOrderNo = ''
  filters.channelTradeNo = ''
  filters.channel = ''
  filters.status = undefined
  filters.callbackFrom = ''
  filters.callbackTo = ''
  callbackRange.value = []
  loadTransactions()
}

onMounted(loadTransactions)
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

.json-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 820px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
