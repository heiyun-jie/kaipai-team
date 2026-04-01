<template>
  <PageContainer
    title="工作台"
    description="集中查看今日待办、风险项与近期处理记录，方便运营快速切换工作。"
  >
    <section class="dashboard-hero">
      <div class="dashboard-hero__copy">
        <p class="dashboard-hero__eyebrow">TODAY FOCUS</p>
        <h2>{{ heroTitle }}</h2>
        <p class="dashboard-hero__description">{{ heroDescription }}</p>
        <div class="dashboard-hero__meta">
          <span>优先聚焦实名认证、邀请异常和退款三类待办</span>
          <span>最近事项支持继续回看和接续处理</span>
        </div>
      </div>
      <div class="dashboard-hero__actions">
        <StatusTag v-bind="heroStatus" />
        <el-button type="primary" :loading="loading" class="dashboard-hero__refresh" @click="loadOverview">
          刷新工作台
        </el-button>
      </div>
    </section>

    <section class="dashboard-grid">
      <el-card v-for="card in cards" :key="card.label" class="dashboard-card" shadow="never">
        <div class="dashboard-card__head">
          <p>{{ card.label }}</p>
          <span class="dashboard-card__badge" :class="`dashboard-card__badge--${card.tone}`">{{ card.badge }}</span>
        </div>
        <strong>{{ card.value }}</strong>
        <span class="dashboard-card__hint">{{ card.hint }}</span>
      </el-card>
    </section>

    <section class="dashboard-grid dashboard-grid--modules">
      <el-card
        v-for="module in modules"
        :key="module.title"
        class="dashboard-module"
        :class="{ 'dashboard-module--emphasis': module.emphasis }"
        shadow="never"
      >
        <div class="dashboard-module__head">
          <div>
            <p>{{ module.eyebrow }}</p>
            <h3>{{ module.title }}</h3>
          </div>
          <StatusTag :label="module.status" :tone="module.tone" />
        </div>
        <p class="dashboard-module__copy">{{ module.copy }}</p>
        <div class="dashboard-module__footer">
          <div class="dashboard-module__summary">
            <span>{{ module.summaryLabel }}</span>
            <strong>{{ module.summaryValue }}</strong>
          </div>
          <el-button
            :type="module.emphasis ? 'primary' : undefined"
            :plain="!module.emphasis"
            class="dashboard-module__action"
            :disabled="!module.route"
            @click="module.route && router.push(module.route)"
          >
            {{ module.action }}
          </el-button>
        </div>
      </el-card>
    </section>

    <el-card class="recent-card" shadow="never">
      <template #header>
        <div class="recent-card__header">
          <div>
            <h3>最近事项</h3>
            <p>展示最近 10 条待处理或刚更新的运营事项，便于回看和继续跟进。</p>
          </div>
        </div>
      </template>

      <el-table v-if="overview.recentItems.length" :data="overview.recentItems" v-loading="loading">
        <el-table-column label="业务线" min-width="120">
          <template #default="{ row }">
            <StatusTag :label="dashboardBizLineMap[row.bizLine] || row.bizLine" :tone="getBizTone(row.bizLine)" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="事项标题" min-width="180" />
        <el-table-column label="引用编号" min-width="150">
          <template #default="{ row }">{{ row.referenceNo || '--' }}</template>
        </el-table-column>
        <el-table-column label="用户 ID" min-width="100">
          <template #default="{ row }">{{ row.userId ?? '--' }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="120">
          <template #default="{ row }">
            <StatusTag v-bind="getRecentStatus(row)" />
          </template>
        </el-table-column>
        <el-table-column label="发生时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.occurredAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="!getRecentRoute(row)" @click="openRecentItem(row)">
              查看页面
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="当前没有最近事项" />
    </el-card>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { fetchDashboardOverview } from '@/api/dashboard'
import { dashboardBizLineMap, referralStatusMap, verifyStatusMap } from '@/constants/status'
import type { DashboardOverview, DashboardRecentItem } from '@/types/dashboard'
import { formatDateTime } from '@/utils/format'

type StatusTone = 'info' | 'warning' | 'success' | 'danger'

const router = useRouter()
const loading = ref(false)
const overview = reactive<DashboardOverview>({
  verifyPendingCount: null,
  referralRiskPendingCount: null,
  refundPendingCount: null,
  todayPaymentOrderCount: null,
  recentItems: [],
})

const pendingTaskCount = computed(
  () =>
    Number(overview.verifyPendingCount || 0) +
    Number(overview.referralRiskPendingCount || 0) +
    Number(overview.refundPendingCount || 0),
)

const heroTitle = computed(() =>
  pendingTaskCount.value ? `当前有 ${pendingTaskCount.value} 项待优先处理` : '当前待办已清空，可转入日常巡检',
)

const heroDescription = computed(() =>
  pendingTaskCount.value
    ? '先处理有积压的审核与退款事项，再进入会员、模板等日常配置工作。'
    : '核心待办已处理完成，当前更适合做巡检、复核与配置维护。',
)

const heroStatus = computed(() => ({
  label: pendingTaskCount.value ? '优先处理中' : '运行平稳',
  tone: (pendingTaskCount.value ? 'warning' : 'success') as StatusTone,
}))

const cards = computed(() => [
  {
    label: '待审核实名认证',
    value: formatMetric(overview.verifyPendingCount),
    hint: '当前处于待审核状态的实名申请',
    badge: '审核',
    tone: 'warning' as const,
  },
  {
    label: '异常邀请待处理',
    value: formatMetric(overview.referralRiskPendingCount),
    hint: '命中风险且仍在复核中的邀请记录',
    badge: '风控',
    tone: 'danger' as const,
  },
  {
    label: '待处理退款',
    value: formatMetric(overview.refundPendingCount),
    hint: '等待复核或处理结果确认的退款申请',
    badge: '退款',
    tone: 'warning' as const,
  },
  {
    label: '今日支付订单',
    value: formatMetric(overview.todayPaymentOrderCount),
    hint: '按今日业务数据统计的支付订单数量',
    badge: '观察',
    tone: 'success' as const,
  },
])

const modules = computed(() => [
  {
    eyebrow: 'VERIFY',
    title: '实名认证审核',
    status: overview.verifyPendingCount ? '待处理' : '运行中',
    tone: overview.verifyPendingCount ? ('warning' as const) : ('success' as const),
    copy: '查看申请资料、核对实名信息，并完成通过或拒绝处理。',
    summaryLabel: '待处理事项',
    summaryValue: formatPendingSummary(overview.verifyPendingCount, '当前无积压'),
    action: '进入实名审核',
    route: '/verify/pending',
    emphasis: Boolean(overview.verifyPendingCount),
  },
  {
    eyebrow: 'REFERRAL',
    title: '异常邀请审核',
    status: overview.referralRiskPendingCount ? '待处理' : '运行中',
    tone: overview.referralRiskPendingCount ? ('warning' as const) : ('success' as const),
    copy: '跟进异常邀请记录，完成复核、作废或处理结果确认。',
    summaryLabel: '待处理事项',
    summaryValue: formatPendingSummary(overview.referralRiskPendingCount, '当前无积压'),
    action: '进入异常邀请',
    route: '/referral/risk',
    emphasis: Boolean(overview.referralRiskPendingCount),
  },
  {
    eyebrow: 'MEMBERSHIP',
    title: '会员产品与账户',
    status: '可配置',
    tone: 'success' as const,
    copy: '维护会员产品方案，并处理会员开通、延期和关闭等日常操作。',
    summaryLabel: '当前覆盖',
    summaryValue: '产品 / 账户',
    action: '进入会员中心',
    route: '/membership/products',
    emphasis: false,
  },
  {
    eyebrow: 'CONTENT',
    title: '模板配置',
    status: '可配置',
    tone: 'success' as const,
    copy: '管理模板内容，支持新建、编辑、发布和回滚当前版本。',
    summaryLabel: '当前覆盖',
    summaryValue: '模板 / 版本',
    action: '进入模板配置',
    route: '/content/templates',
    emphasis: false,
  },
])

function formatMetric(value?: number | null) {
  return value ?? '--'
}

function formatPendingSummary(value?: number | null, emptyLabel = '当前稳定') {
  return value ? `${value} 项待跟进` : emptyLabel
}

function getBizTone(bizLine?: string) {
  switch (bizLine) {
    case 'verify':
      return 'warning' as const
    case 'referral':
      return 'danger' as const
    case 'refund':
      return 'warning' as const
    case 'payment':
      return 'success' as const
    default:
      return 'info' as const
  }
}

function getRecentStatus(item: DashboardRecentItem) {
  if (item.bizLine === 'verify') {
    return verifyStatusMap[item.status || 0] || verifyStatusMap[0]
  }
  if (item.bizLine === 'referral') {
    return referralStatusMap[item.status || 0] || referralStatusMap[0]
  }
  if (item.bizLine === 'refund') {
    return {
      label: item.status === 0 ? '待审核' : `状态 ${item.status ?? '--'}`,
      tone: (item.status === 0 ? 'warning' : 'info') as StatusTone,
    }
  }
  if (item.bizLine === 'payment') {
    return {
      label: item.status === 1 ? '已支付' : `状态 ${item.status ?? '--'}`,
      tone: (item.status === 1 ? 'success' : 'info') as StatusTone,
    }
  }
  return { label: `状态 ${item.status ?? '--'}`, tone: 'info' as StatusTone }
}

function getRecentRoute(item: DashboardRecentItem) {
  if (item.bizLine === 'verify') {
    return '/verify/pending'
  }
  if (item.bizLine === 'referral') {
    return '/referral/risk'
  }
  return ''
}

function openRecentItem(item: DashboardRecentItem) {
  const route = getRecentRoute(item)
  if (route) {
    router.push(route)
  }
}

async function loadOverview() {
  loading.value = true
  try {
    const data = await fetchDashboardOverview()
    overview.verifyPendingCount = data.verifyPendingCount
    overview.referralRiskPendingCount = data.referralRiskPendingCount
    overview.refundPendingCount = data.refundPendingCount
    overview.todayPaymentOrderCount = data.todayPaymentOrderCount
    overview.recentItems = data.recentItems || []
  } finally {
    loading.value = false
  }
}

onMounted(loadOverview)
</script>

<style scoped lang="scss">
.dashboard-hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
  border: 1px solid rgba(196, 77, 52, 0.12);
  border-radius: 30px;
  background:
    radial-gradient(circle at top right, rgba(196, 77, 52, 0.16), transparent 30%),
    linear-gradient(135deg, rgba(255, 250, 244, 0.96), rgba(250, 243, 234, 0.88));
  box-shadow: var(--kp-shadow);
}

.dashboard-hero__copy {
  display: grid;
  gap: 10px;
  max-width: 760px;
}

.dashboard-hero__eyebrow {
  margin: 0;
  color: var(--kp-accent-deep);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.dashboard-hero__copy h2 {
  margin: 0;
  font-size: clamp(30px, 3vw, 42px);
  line-height: 1.05;
}

.dashboard-hero__description {
  margin: 0;
  color: var(--kp-text-secondary);
  font-size: 15px;
  line-height: 1.8;
}

.dashboard-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 2px;

  span {
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.58);
    color: var(--kp-text-secondary);
    font-size: 12px;
  }
}

.dashboard-hero__actions {
  display: grid;
  align-content: space-between;
  justify-items: end;
  gap: 12px;
}

.dashboard-hero__refresh {
  min-width: 136px;
  min-height: 42px;
  border-radius: 14px;
}

.dashboard-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-grid--modules {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.dashboard-card,
.dashboard-module,
.recent-card {
  border: 1px solid var(--kp-border);
  background: rgba(255, 252, 247, 0.88);
}

:deep(.dashboard-card .el-card__body),
:deep(.dashboard-module .el-card__body) {
  padding: 24px 24px 22px;
}

.dashboard-card {
  border-radius: 26px;
  box-shadow: 0 16px 32px rgba(63, 42, 20, 0.08);
}

.dashboard-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;

  p {
    margin: 0;
    color: var(--kp-text-secondary);
    font-size: 14px;
    font-weight: 600;
  }
}

.dashboard-card__badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.dashboard-card__badge--warning {
  background: rgba(196, 122, 40, 0.14);
  color: var(--kp-warning);
}

.dashboard-card__badge--danger {
  background: rgba(181, 65, 49, 0.14);
  color: var(--kp-danger);
}

.dashboard-card__badge--success {
  background: rgba(47, 125, 87, 0.14);
  color: var(--kp-success);
}

.dashboard-card strong {
  display: block;
  margin: 20px 0 10px;
  font-size: clamp(42px, 4vw, 56px);
  line-height: 0.95;
}

.dashboard-card__hint {
  display: block;
  color: var(--kp-text-secondary);
  line-height: 1.7;
}

.dashboard-module {
  border-radius: 28px;
  box-shadow: 0 14px 28px rgba(63, 42, 20, 0.08);
}

.dashboard-module--emphasis {
  border-color: rgba(196, 122, 40, 0.22);
  background:
    radial-gradient(circle at top right, rgba(196, 122, 40, 0.12), transparent 26%),
    rgba(255, 251, 245, 0.92);
}

.dashboard-module__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;

  p {
    margin: 0 0 8px;
    color: var(--kp-accent);
    font-size: 12px;
    letter-spacing: 0.18em;
  }

  h3 {
    margin: 0;
    font-size: 24px;
  }
}

.dashboard-module__copy {
  min-height: 54px;
  margin: 16px 0 18px;
  color: var(--kp-text-secondary);
  line-height: 1.7;
}

.dashboard-module__footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding-top: 18px;
  border-top: 1px solid rgba(80, 63, 47, 0.08);
}

.dashboard-module__summary {
  display: grid;
  gap: 4px;

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
  }

  strong {
    font-size: 16px;
  }
}

.dashboard-module__action {
  min-width: 148px;
  min-height: 42px;
  border-radius: 14px;
  font-weight: 700;
}

.recent-card__header {
  h3 {
    margin: 0 0 6px;
    font-size: 18px;
  }

  p {
    margin: 0;
    color: var(--kp-text-secondary);
  }
}

@media (max-width: 1100px) {
  .dashboard-grid,
  .dashboard-grid--modules {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-hero {
    display: grid;
  }

  .dashboard-hero__actions {
    justify-items: start;
  }
}

@media (max-width: 760px) {
  .dashboard-grid,
  .dashboard-grid--modules {
    grid-template-columns: 1fr;
  }

  .dashboard-hero {
    padding: 22px 20px;
  }

  .dashboard-module__footer {
    display: grid;
  }

  .dashboard-module__action {
    width: 100%;
  }
}
</style>
