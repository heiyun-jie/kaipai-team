<template>
  <PageContainer
    title="操作日志"
    description="回看后台操作记录，便于追踪关键动作、结果与责任人。"
  >
    <FilterPanel description="按操作人、模块、结果和目标信息筛选后台操作记录。">
      <el-form :model="filters" inline>
        <el-form-item label="后台账号 ID">
          <el-input v-model.number="filters.adminUserId" placeholder="后台账号 ID" clearable />
        </el-form-item>
        <el-form-item label="模块">
          <el-input v-model="filters.moduleCode" placeholder="模块编码" clearable />
        </el-form-item>
        <el-form-item label="操作码">
          <el-input v-model="filters.operationCode" placeholder="操作码" clearable />
        </el-form-item>
        <el-form-item label="目标类型">
          <el-input v-model="filters.targetType" placeholder="目标类型" clearable />
        </el-form-item>
        <el-form-item label="请求 ID">
          <el-input v-model="filters.requestId" placeholder="请求 ID" clearable />
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="filters.result" clearable style="width: 140px">
            <el-option label="成功" :value="1" />
            <el-option label="失败" :value="0" />
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
        <el-table-column prop="operationLogId" label="日志 ID" min-width="110" />
        <el-table-column label="操作人" min-width="150">
          <template #default="{ row }">{{ row.adminUserName || row.adminUserId || '--' }}</template>
        </el-table-column>
        <el-table-column prop="moduleCode" label="模块" min-width="120" />
        <el-table-column prop="operationCode" label="操作码" min-width="160" />
        <el-table-column label="目标" min-width="180">
          <template #default="{ row }">{{ row.targetType || '--' }} / {{ row.targetId ?? '--' }}</template>
        </el-table-column>
        <el-table-column prop="requestId" label="请求 ID" min-width="180" show-overflow-tooltip />
        <el-table-column label="结果" min-width="100">
          <template #default="{ row }">
            <StatusTag :label="row.operationResult === 1 ? '成功' : '失败'" :tone="row.operationResult === 1 ? 'success' : 'danger'" />
          </template>
        </el-table-column>
        <el-table-column prop="clientIp" label="客户端 IP" min-width="140" />
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.operationLogId)">查看详情</el-button>
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
          @current-change="loadLogs"
          @size-change="loadLogs"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="操作日志详情" size="860px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-grid">
          <div v-for="item in detailBlocks" :key="item.label" class="detail-block">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>变更前快照</h3></template>
          <pre class="json-block">{{ detail.beforeSnapshotJson || '--' }}</pre>
        </el-card>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>变更后快照</h3></template>
          <pre class="json-block">{{ detail.afterSnapshotJson || '--' }}</pre>
        </el-card>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>补充信息</h3></template>
          <pre class="json-block">{{ detail.extraContextJson || '--' }}</pre>
        </el-card>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchAdminOperationLogDetail, fetchAdminOperationLogs } from '@/api/system'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import type { AdminOperationLogDetail, AdminOperationLogItem, AdminOperationLogQuery } from '@/types/system'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const rows = ref<AdminOperationLogItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<AdminOperationLogDetail | null>(null)

const filters = reactive<AdminOperationLogQuery>({
  pageNo: 1,
  pageSize: 20,
  adminUserId: undefined,
  moduleCode: '',
  operationCode: '',
  targetType: '',
  requestId: '',
  result: undefined,
  dateFrom: '',
  dateTo: '',
})

const detailBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '日志 ID', value: detail.value.operationLogId },
    { label: '操作人', value: detail.value.adminUserName || detail.value.adminUserId || '--' },
    { label: '模块', value: detail.value.moduleCode || '--' },
    { label: '操作码', value: detail.value.operationCode || '--' },
    { label: '目标', value: `${detail.value.targetType || '--'} / ${detail.value.targetId ?? '--'}` },
    { label: '请求 ID', value: detail.value.requestId || '--' },
    { label: '客户端 IP', value: detail.value.clientIp || '--' },
    { label: '访问设备信息', value: detail.value.userAgent || '--' },
    { label: '结果', value: detail.value.operationResult === 1 ? '成功' : '失败' },
    { label: '失败原因', value: detail.value.failReason || '--' },
    { label: '确认时间', value: formatDateTime(detail.value.confirmedAt) },
    { label: '创建时间', value: formatDateTime(detail.value.createTime) },
  ]
})

async function loadLogs() {
  loading.value = true
  try {
    const result = await fetchAdminOperationLogs(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchAdminOperationLogDetail(id)
  detailVisible.value = true
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.adminUserId = undefined
  filters.moduleCode = ''
  filters.operationCode = ''
  filters.targetType = ''
  filters.requestId = ''
  filters.result = undefined
  filters.dateFrom = ''
  filters.dateTo = ''
  loadLogs()
}

onMounted(loadLogs)
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
