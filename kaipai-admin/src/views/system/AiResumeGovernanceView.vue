<template>
  <PageContainer
    title="AI 简历治理"
    eyebrow="AI Resume Governance"
    description="围绕 AI 润色概览、额度消耗和历史补丁建立第一版真实治理页，当前临时复用操作日志页面权限。"
  >
    <section class="overview-grid">
      <article v-for="card in overviewCards" :key="card.label" class="overview-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <p>{{ card.description }}</p>
      </article>
    </section>

    <section class="board-grid">
      <el-card class="surface-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <h3>Quota Top Users</h3>
              <p>按本月 AI 次数消耗排序，优先确认高频用户是否与等级权益一致。</p>
            </div>
          </div>
        </template>
        <el-table :data="overview.topQuotaUsers" v-loading="overviewLoading" empty-text="暂无额度消耗数据">
          <el-table-column prop="userId" label="用户 ID" min-width="110" />
          <el-table-column label="用户" min-width="180">
            <template #default="{ row }">
              <div class="stack-cell">
                <strong>{{ row.userName || '--' }}</strong>
                <span>{{ maskPhone(row.phone) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="实名" min-width="110">
            <template #default="{ row }">
              <StatusTag v-bind="getRealAuthTag(row.realAuthStatus)" />
            </template>
          </el-table-column>
          <el-table-column label="等级 / 会员" min-width="150">
            <template #default="{ row }">{{ formatLevel(row.level, row.membershipTier) }}</template>
          </el-table-column>
          <el-table-column label="本月已用 / 总配额" min-width="160">
            <template #default="{ row }">{{ row.usedCount ?? 0 }} / {{ row.totalQuota ?? '--' }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="surface-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <h3>Recent Histories</h3>
              <p>概览接口返回的最近润色样本，帮助先看最新流量和状态分布。</p>
            </div>
          </div>
        </template>
        <div v-if="overview.recentHistories.length" class="recent-list">
          <button
            v-for="item in overview.recentHistories"
            :key="item.historyId"
            type="button"
            class="recent-item"
            @click="openDetail(item.historyId)"
          >
            <div class="recent-item__head">
              <strong>{{ item.userName || `用户 ${item.userId ?? '--'}` }}</strong>
              <StatusTag v-bind="getHistoryStatusTag(item.status)" />
            </div>
            <p>{{ item.historyId }}</p>
            <span>请求 {{ item.requestId || '--' }} · Patch {{ item.patchCount ?? 0 }} · {{ formatDateTime(item.createdAt) }}</span>
          </button>
        </div>
        <el-empty v-else description="暂无历史样本" />
      </el-card>
    </section>

    <section class="notice-grid">
      <el-card class="surface-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <h3>Failure Samples</h3>
              <p>回看最近 AI 润色失败样本，优先定位不可解析响应、超时和上下文异常。</p>
            </div>
          </div>
        </template>
        <el-table :data="failures" v-loading="failureLoading" empty-text="暂无失败样本">
          <el-table-column label="时间" min-width="160">
            <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
          </el-table-column>
          <el-table-column label="用户" min-width="180">
            <template #default="{ row }">
              <div class="stack-cell">
                <strong>{{ row.userName || '--' }}</strong>
                <span>{{ row.userId ?? '--' }} · {{ maskPhone(row.phone) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="类型" min-width="120">
            <template #default="{ row }">
              <StatusTag v-bind="getFailureStatusTag(row.failureType)" />
            </template>
          </el-table-column>
          <el-table-column prop="errorCode" label="错误码" min-width="100" />
          <el-table-column prop="errorMessage" label="错误信息" min-width="220" show-overflow-tooltip />
          <el-table-column prop="instruction" label="用户指令" min-width="260" show-overflow-tooltip />
        </el-table>
      </el-card>

      <el-card class="surface-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <h3>Sensitive Hits</h3>
              <p>单独拉出命中敏感内容的失败样本，便于排查规则、文案和人工复核需求。</p>
            </div>
          </div>
        </template>
        <el-table :data="sensitiveHits" v-loading="failureLoading" empty-text="暂无敏感命中样本">
          <el-table-column label="时间" min-width="160">
            <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
          </el-table-column>
          <el-table-column label="用户" min-width="180">
            <template #default="{ row }">
              <div class="stack-cell">
                <strong>{{ row.userName || '--' }}</strong>
                <span>{{ row.userId ?? '--' }} · {{ maskPhone(row.phone) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="命中词" min-width="120">
            <template #default="{ row }">{{ row.hitKeyword || '--' }}</template>
          </el-table-column>
          <el-table-column prop="errorMessage" label="结果" min-width="180" show-overflow-tooltip />
          <el-table-column prop="instruction" label="用户指令" min-width="260" show-overflow-tooltip />
        </el-table>
      </el-card>
    </section>

    <FilterPanel description="按用户、状态、关键词和请求 ID 回看 AI 润色历史，详情抽屉可检查 patch 和前后快照。">
      <el-form :model="filters" inline>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="已创建" value="created" />
            <el-option label="已应用" value="applied" />
            <el-option label="已回滚" value="rolled_back" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="historyId / draftId / 指令 / 回复" clearable />
        </el-form-item>
        <el-form-item label="请求 ID">
          <el-input v-model="filters.requestId" placeholder="requestId" clearable />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadHistories">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="surface-card" shadow="never">
      <el-table :data="rows" v-loading="tableLoading" empty-text="暂无 AI 润色历史">
        <el-table-column prop="historyId" label="历史 ID" min-width="180" show-overflow-tooltip />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.userName || '--' }}</strong>
              <span>{{ row.userId ?? '--' }} · {{ maskPhone(row.phone) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="实名" min-width="100">
          <template #default="{ row }">
            <StatusTag v-bind="getRealAuthTag(row.realAuthStatus)" />
          </template>
        </el-table-column>
        <el-table-column label="等级 / 会员" min-width="150">
          <template #default="{ row }">{{ formatLevel(row.level, row.membershipTier) }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="getHistoryStatusTag(row.status)" />
          </template>
        </el-table-column>
        <el-table-column label="Patch" min-width="80">
          <template #default="{ row }">{{ row.patchCount ?? 0 }}</template>
        </el-table-column>
        <el-table-column prop="requestId" label="请求 ID" min-width="180" show-overflow-tooltip />
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.historyId)">查看详情</el-button>
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
          @current-change="loadHistories"
          @size-change="loadHistories"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="AI 简历历史详情" size="980px" destroy-on-close>
      <div v-loading="detailLoading" class="detail-layout">
        <template v-if="detail">
          <el-card class="surface-card" shadow="never">
            <template #header><h3>治理概览</h3></template>
            <div class="detail-grid">
              <div v-for="item in detailBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <div class="detail-split">
            <el-card class="surface-card" shadow="never">
              <template #header><h3>用户指令</h3></template>
              <pre class="text-block">{{ detail.instruction || '--' }}</pre>
            </el-card>

            <el-card class="surface-card" shadow="never">
              <template #header><h3>模型回复</h3></template>
              <pre class="text-block">{{ detail.reply || '--' }}</pre>
            </el-card>
          </div>

          <div class="detail-split">
            <el-card class="surface-card" shadow="never">
              <template #header><h3>Patch 列表</h3></template>
              <el-table :data="detail.patches || []" empty-text="暂无 patch" class="inner-table">
                <el-table-column prop="fieldKey" label="字段" min-width="120" />
                <el-table-column prop="label" label="标签" min-width="120" />
                <el-table-column prop="beforeValue" label="变更前" min-width="180" show-overflow-tooltip />
                <el-table-column prop="afterValue" label="变更后" min-width="180" show-overflow-tooltip />
                <el-table-column prop="reason" label="原因" min-width="180" show-overflow-tooltip />
              </el-table>
            </el-card>

            <el-card class="surface-card" shadow="never">
              <template #header><h3>快照对比</h3></template>
              <div class="snapshot-stack">
                <div>
                  <h4>Before Snapshot</h4>
                  <el-table :data="detail.beforeSnapshot || []" empty-text="暂无前快照" class="inner-table">
                    <el-table-column prop="fieldKey" label="字段" min-width="140" />
                    <el-table-column prop="value" label="值" min-width="220" show-overflow-tooltip />
                  </el-table>
                </div>
                <div>
                  <h4>After Snapshot</h4>
                  <el-table :data="detail.afterSnapshot || []" empty-text="暂无后快照" class="inner-table">
                    <el-table-column prop="fieldKey" label="字段" min-width="140" />
                    <el-table-column prop="value" label="值" min-width="220" show-overflow-tooltip />
                  </el-table>
                </div>
              </div>
            </el-card>
          </div>
        </template>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  fetchAdminAiResumeFailures,
  fetchAdminAiResumeHistories,
  fetchAdminAiResumeHistoryDetail,
  fetchAdminAiResumeOverview,
  fetchAdminAiResumeSensitiveHits,
} from '@/api/ai'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import type {
  AdminAiResumeFailureItem,
  AdminAiResumeHistoryItem,
  AdminAiResumeHistoryQuery,
  AdminAiResumeOverview,
} from '@/types/ai'
import { formatDateTime, maskPhone } from '@/utils/format'

const overviewLoading = ref(false)
const tableLoading = ref(false)
const detailLoading = ref(false)
const failureLoading = ref(false)
const total = ref(0)
const rows = ref<AdminAiResumeHistoryItem[]>([])
const detailVisible = ref(false)
const detail = ref<AdminAiResumeHistoryItem | null>(null)
const failures = ref<AdminAiResumeFailureItem[]>([])
const sensitiveHits = ref<AdminAiResumeFailureItem[]>([])

const overview = reactive<AdminAiResumeOverview>({
  totalHistoryCount: 0,
  appliedHistoryCount: 0,
  rolledBackHistoryCount: 0,
  historyUserCount: 0,
  currentMonthHistoryCount: 0,
  currentMonthQuotaUserCount: 0,
  currentMonthQuotaUsageTotal: 0,
  topQuotaUsers: [],
  recentHistories: [],
})

const filters = reactive<AdminAiResumeHistoryQuery>({
  pageNo: 1,
  pageSize: 20,
  userId: undefined,
  status: '',
  keyword: '',
  requestId: '',
})

const overviewCards = computed(() => [
  {
    label: '历史总量',
    value: String(overview.totalHistoryCount || 0),
    description: `覆盖用户 ${overview.historyUserCount || 0} 人`,
  },
  {
    label: '已应用',
    value: String(overview.appliedHistoryCount || 0),
    description: '已确认写回档案的 AI 润色历史',
  },
  {
    label: '已回滚',
    value: String(overview.rolledBackHistoryCount || 0),
    description: '已回滚样本，适合回看 patch 质量',
  },
  {
    label: '本月调用',
    value: String(overview.currentMonthHistoryCount || 0),
    description: `本月额度用户 ${overview.currentMonthQuotaUserCount || 0} 人`,
  },
  {
    label: '本月额度消耗',
    value: String(overview.currentMonthQuotaUsageTotal || 0),
    description: '用于快速识别治理重点用户',
  },
])

const detailBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '历史 ID', value: detail.value.historyId || '--' },
    { label: '用户', value: `${detail.value.userName || '--'} / ${detail.value.userId ?? '--'}` },
    { label: '手机号', value: maskPhone(detail.value.phone) },
    { label: '实名状态', value: getRealAuthTag(detail.value.realAuthStatus).label },
    { label: '等级 / 会员', value: formatLevel(detail.value.level, detail.value.membershipTier) },
    { label: '状态', value: getHistoryStatusTag(detail.value.status).label },
    { label: 'Patch 数', value: detail.value.patchCount ?? 0 },
    { label: '草稿 ID', value: detail.value.draftId || '--' },
    { label: '请求 ID', value: detail.value.requestId || '--' },
    { label: '会话 ID', value: detail.value.conversationId || '--' },
    { label: '创建时间', value: formatDateTime(detail.value.createdAt) },
    { label: '应用时间', value: formatDateTime(detail.value.appliedAt) },
    { label: '回滚时间', value: formatDateTime(detail.value.rolledBackAt) },
  ]
})

function getRealAuthTag(status?: number | null) {
  if (status === 2) {
    return { label: '已实名', tone: 'success' as const }
  }
  if (status === 1) {
    return { label: '审核中', tone: 'warning' as const }
  }
  if (status === 3) {
    return { label: '已拒绝', tone: 'danger' as const }
  }
  return { label: '未实名', tone: 'info' as const }
}

function getHistoryStatusTag(status?: string | null) {
  if (status === 'applied') {
    return { label: '已应用', tone: 'success' as const }
  }
  if (status === 'rolled_back') {
    return { label: '已回滚', tone: 'warning' as const }
  }
  if (status === 'failed') {
    return { label: '失败', tone: 'danger' as const }
  }
  return { label: status || '已创建', tone: 'info' as const }
}

function getFailureStatusTag(type?: string | null) {
  if (type === 'content_blocked') {
    return { label: '敏感命中', tone: 'danger' as const }
  }
  if (type === 'response_unparsable') {
    return { label: '不可解析', tone: 'warning' as const }
  }
  if (type === 'model_timeout') {
    return { label: '超时', tone: 'warning' as const }
  }
  if (type === 'context_invalid') {
    return { label: '上下文无效', tone: 'info' as const }
  }
  return { label: '失败', tone: 'danger' as const }
}

function formatLevel(level?: number | null, membershipTier?: string | null) {
  const levelText = level == null ? 'L--' : `L${level}`
  return membershipTier ? `${levelText} / ${membershipTier}` : levelText
}

async function loadOverview() {
  overviewLoading.value = true
  try {
    const data = await fetchAdminAiResumeOverview()
    overview.totalHistoryCount = data.totalHistoryCount || 0
    overview.appliedHistoryCount = data.appliedHistoryCount || 0
    overview.rolledBackHistoryCount = data.rolledBackHistoryCount || 0
    overview.historyUserCount = data.historyUserCount || 0
    overview.currentMonthHistoryCount = data.currentMonthHistoryCount || 0
    overview.currentMonthQuotaUserCount = data.currentMonthQuotaUserCount || 0
    overview.currentMonthQuotaUsageTotal = data.currentMonthQuotaUsageTotal || 0
    overview.topQuotaUsers = data.topQuotaUsers || []
    overview.recentHistories = data.recentHistories || []
  } finally {
    overviewLoading.value = false
  }
}

async function loadHistories() {
  tableLoading.value = true
  try {
    const result = await fetchAdminAiResumeHistories({
      pageNo: filters.pageNo,
      pageSize: filters.pageSize,
      userId: filters.userId,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined,
      requestId: filters.requestId || undefined,
    })
    rows.value = result.list || []
    total.value = result.total || 0
  } finally {
    tableLoading.value = false
  }
}

async function loadFailures() {
  failureLoading.value = true
  try {
    const [failureData, sensitiveData] = await Promise.all([
      fetchAdminAiResumeFailures(),
      fetchAdminAiResumeSensitiveHits(),
    ])
    failures.value = failureData || []
    sensitiveHits.value = sensitiveData || []
  } finally {
    failureLoading.value = false
  }
}

async function openDetail(historyId: string) {
  detailVisible.value = true
  detailLoading.value = true
  detail.value = null
  try {
    detail.value = await fetchAdminAiResumeHistoryDetail(historyId)
  } finally {
    detailLoading.value = false
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.userId = undefined
  filters.status = ''
  filters.keyword = ''
  filters.requestId = ''
  loadHistories()
}

onMounted(() => {
  loadOverview()
  loadHistories()
  loadFailures()
})
</script>

<style scoped lang="scss">
.overview-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.overview-card,
.surface-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.overview-card {
  display: grid;
  gap: 8px;
  padding: 20px;
  border-radius: 24px;
  box-shadow: var(--kp-shadow);

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
    letter-spacing: 0.08em;
  }

  strong {
    font-size: 30px;
    line-height: 1;
  }

  p {
    margin: 0;
    color: var(--kp-text-secondary);
    line-height: 1.6;
  }
}

.board-grid,
.detail-split,
.notice-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;

  h3,
  p {
    margin: 0;
  }

  p {
    margin-top: 6px;
    color: var(--kp-text-secondary);
    line-height: 1.6;
  }
}

.stack-cell {
  display: grid;
  gap: 2px;

  strong {
    font-size: 13px;
  }

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }
}

.recent-list {
  display: grid;
  gap: 12px;
}

.recent-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid rgba(47, 36, 27, 0.08);
  border-radius: 18px;
  background: rgba(47, 36, 27, 0.03);
  text-align: left;
  cursor: pointer;

  p,
  span {
    margin: 0;
    color: var(--kp-text-secondary);
    word-break: break-all;
  }
}

.recent-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
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

.text-block {
  margin: 0;
  min-height: 180px;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.7;
}

.snapshot-stack {
  display: grid;
  gap: 16px;

  h4 {
    margin: 0 0 12px;
    font-size: 14px;
  }
}

.inner-table {
  width: 100%;
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .board-grid,
  .detail-split,
  .notice-grid,
  .detail-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
