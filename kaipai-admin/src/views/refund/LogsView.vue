<template>
  <PageContainer
    title="退款日志"
    description="当前页面以 `/admin/refund/logs` 为准，支持按退款单、操作人和动作筛选。"
  >
    <FilterPanel description="查询字段与后端 `RefundOperateLogQueryDTO` 保持一致。">
      <el-form :model="filters" inline>
        <el-form-item label="退款单 ID">
          <el-input v-model.number="filters.refundOrderId" placeholder="退款单 ID" clearable />
        </el-form-item>
        <el-form-item label="退款单号">
          <el-input v-model="filters.refundNo" placeholder="退款单号" clearable />
        </el-form-item>
        <el-form-item label="操作人 ID">
          <el-input v-model.number="filters.operatorId" placeholder="操作人 ID" clearable />
        </el-form-item>
        <el-form-item label="动作">
          <el-select v-model="filters.actionType" clearable style="width: 160px">
            <el-option label="approve" value="approve" />
            <el-option label="reject" value="reject" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadLogs">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="logId" label="日志 ID" min-width="110" />
        <el-table-column prop="refundOrderId" label="退款单 ID" min-width="120" />
        <el-table-column prop="operatorId" label="操作人 ID" min-width="120" />
        <el-table-column label="动作" min-width="120">
          <template #default="{ row }">{{ getActionLabel(row.actionType) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="260" show-overflow-tooltip />
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="filters.pageNo"
          v-model:page-size="filters.pageSize"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[20, 50, 100]"
          :total="total"
          @current-change="loadLogs"
          @size-change="loadLogs"
        />
      </div>
    </el-card>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { fetchRefundOperateLogs } from '@/api/refund'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import type { RefundOperateLogItem, RefundOperateLogQuery } from '@/types/refund'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const rows = ref<RefundOperateLogItem[]>([])
const total = ref(0)

const filters = reactive<RefundOperateLogQuery>({
  pageNo: 1,
  pageSize: 20,
  refundOrderId: undefined,
  refundNo: '',
  operatorId: undefined,
  actionType: '',
  dateFrom: '',
  dateTo: '',
})

function getActionLabel(actionType?: string | null) {
  if (actionType === 'approve') return '审核通过'
  if (actionType === 'reject') return '审核拒绝'
  return actionType || '--'
}

async function loadLogs() {
  loading.value = true
  try {
    const result = await fetchRefundOperateLogs(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.refundOrderId = undefined
  filters.refundNo = ''
  filters.operatorId = undefined
  filters.actionType = ''
  loadLogs()
}

onMounted(loadLogs)
</script>

<style scoped lang="scss">
.table-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
