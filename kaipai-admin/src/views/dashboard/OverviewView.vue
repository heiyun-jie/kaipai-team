<template>
  <PageContainer
    title="工作台"
    description="集中查看今日待办、风险项与近期处理记录，方便运营快速切换工作。"
  >
    <template #actions>
      <el-button type="primary" :loading="loading" @click="loadOverview">刷新数据</el-button>
    </template>

    <section class="dashboard-grid">
      <el-card v-for="card in cards" :key="card.label" class="dashboard-card" shadow="never">
        <p>{{ card.label }}</p>
        <strong>{{ card.value }}</strong>
        <span>{{ card.hint }}</span>
      </el-card>
    </section>

    <section class="dashboard-grid dashboard-grid--modules">
      <el-card v-for="module in modules" :key="module.title" class="dashboard-module" shadow="never">
        <div class="dashboard-module__head">
          <div>
            <p>{{ module.eyebrow }}</p>
            <h3>{{ module.title }}</h3>
          </div>
          <StatusTag :label="module.status" :tone="module.tone" />
        </div>
        <p class="dashboard-module__copy">{{ module.copy }}</p>
        <el-button :disabled="!module.route" @click="module.route && router.push(module.route)">{{ module.action }}</el-button>
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

const cards = computed(() => [
  {
    label: '待审核实名认证',
    value: formatMetric(overview.verifyPendingCount),
    hint: '当前处于待审核状态的实名申请',
  },
  {
    label: '异常邀请待处理',
    value: formatMetric(overview.referralRiskPendingCount),
    hint: '命中风险且仍在复核中的邀请记录',
  },
  {
    label: '待处理退款',
    value: formatMetric(overview.refundPendingCount),
    hint: '等待复核或处理结果确认的退款申请',
  },
  {
    label: '今日支付订单',
    value: formatMetric(overview.todayPaymentOrderCount),
    hint: '按今日业务数据统计的支付订单数量',
  },
])

const modules = computed(() => [
  {
    eyebrow: 'VERIFY',
    title: '实名认证审核',
    status: overview.verifyPendingCount ? '待处理' : '运行中',
    tone: overview.verifyPendingCount ? ('warning' as const) : ('success' as const),
    copy: '查看申请资料、核对实名信息，并完成通过或拒绝处理。',
    action: '进入待审核',
    route: '/verify/pending',
  },
  {
    eyebrow: 'REFERRAL',
    title: '异常邀请审核',
    status: overview.referralRiskPendingCount ? '待处理' : '运行中',
    tone: overview.referralRiskPendingCount ? ('warning' as const) : ('success' as const),
    copy: '跟进异常邀请记录，完成复核、作废或处理结果确认。',
    action: '进入风控页',
    route: '/referral/risk',
  },
  {
    eyebrow: 'MEMBERSHIP',
    title: '会员产品与账户',
    status: '可配置',
    tone: 'success' as const,
    copy: '维护会员产品方案，并处理会员开通、延期和关闭等日常操作。',
    action: '进入会员中心',
    route: '/membership/products',
  },
  {
    eyebrow: 'CONTENT',
    title: '模板配置',
    status: '可配置',
    tone: 'success' as const,
    copy: '管理模板内容，支持新建、编辑、发布和回滚当前版本。',
    action: '进入模板配置',
    route: '/content/templates',
  },
])

function formatMetric(value?: number | null) {
  return value ?? '--'
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
.dashboard-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-grid--modules {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.dashboard-card,
.dashboard-module,
.recent-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.dashboard-card {
  p,
  span {
    margin: 0;
    color: var(--kp-text-secondary);
  }

  strong {
    display: block;
    margin: 18px 0 10px;
    font-size: 40px;
    line-height: 1;
  }
}

.dashboard-module__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;

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
}

@media (max-width: 760px) {
  .dashboard-grid,
  .dashboard-grid--modules {
    grid-template-columns: 1fr;
  }
}
</style>
