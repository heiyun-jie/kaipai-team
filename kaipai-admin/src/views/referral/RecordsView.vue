<template>
  <PageContainer
    title="邀请记录"
    eyebrow="Referral Records"
    description="查看邀请注册、状态变化与风险标记，确认邀请记录和前台展示口径是否一致。"
  >
    <FilterPanel description="按邀请码、邀请人、被邀请人和状态筛选邀请记录，优先验证真实链路样本。">
      <el-form :model="filters" inline>
        <el-form-item label="邀请码">
          <el-input v-model="filters.inviteCode" placeholder="邀请码" clearable />
        </el-form-item>
        <el-form-item label="邀请人 ID">
          <el-input v-model.number="filters.inviterUserId" placeholder="邀请人 ID" clearable />
        </el-form-item>
        <el-form-item label="被邀请人 ID">
          <el-input v-model.number="filters.inviteeUserId" placeholder="被邀请人 ID" clearable />
        </el-form-item>
        <el-form-item label="邀请状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="待生效" :value="0" />
            <el-option label="有效" :value="1" />
            <el-option label="已作废" :value="2" />
            <el-option label="复核中" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险状态">
          <el-select v-model="filters.riskFlag" clearable style="width: 160px">
            <el-option label="无风险" :value="0" />
            <el-option label="命中风险" :value="1" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="referralId" label="邀请记录 ID" min-width="130" />
        <el-table-column prop="inviteCode" label="邀请码" min-width="120" />
        <el-table-column label="邀请人" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.inviterName || '--' }}</strong>
              <span>{{ row.inviterUserId ?? '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="被邀请人" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.inviteeName || '--' }}</strong>
              <span>{{ row.inviteeUserId ?? '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="邀请状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="referralStatusMap[row.status || 0] || referralStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="风险状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="referralRiskFlagMap[row.riskFlag || 0] || referralRiskFlagMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="注册时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.registeredAt) }}</template>
        </el-table-column>
        <el-table-column label="生效时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.validatedAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.referralId, row)">查看详情</el-button>
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

    <el-drawer v-model="detailVisible" title="邀请记录详情" size="860px" destroy-on-close>
      <div v-loading="detailLoading" class="detail-layout">
        <el-card class="detail-card" shadow="never">
          <template #header><h3>记录概览</h3></template>
          <div class="detail-grid">
            <div v-for="item in recordBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>

        <div class="detail-split">
          <el-card class="detail-card" shadow="never">
            <template #header><h3>邀请人</h3></template>
            <div class="detail-grid">
              <div v-for="item in inviterBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="detail-card" shadow="never">
            <template #header><h3>被邀请人</h3></template>
            <div class="detail-grid">
              <div v-for="item in inviteeBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </div>

        <el-card class="detail-card" shadow="never">
          <template #header><h3>风控与资格摘要</h3></template>
          <div class="detail-grid">
            <div v-for="item in riskBlocks" :key="item.label" class="detail-block">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </el-card>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchReferralRecordDetail, fetchReferralRecords } from '@/api/referral'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { referralRiskFlagMap, referralStatusMap } from '@/constants/status'
import type { ReferralRecordDetail, ReferralRecordItem, ReferralRecordQuery } from '@/types/referral'
import { formatDateTime, maskPhone, maskText } from '@/utils/format'

const loading = ref(false)
const detailLoading = ref(false)
const rows = ref<ReferralRecordItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<ReferralRecordDetail | null>(null)

const filters = reactive<ReferralRecordQuery>({
  pageNo: 1,
  pageSize: 20,
  inviteCode: '',
  inviterUserId: undefined,
  inviteeUserId: undefined,
  status: undefined,
  riskFlag: undefined,
  registeredAtFrom: undefined,
  registeredAtTo: undefined,
  validatedAtFrom: undefined,
  validatedAtTo: undefined,
})

const recordBlocks = computed(() => {
  const record = detail.value?.recordInfo
  if (!record) {
    return []
  }
  return [
    { label: '邀请记录 ID', value: record.referralId ?? '--' },
    { label: '邀请码', value: record.inviteCode || '--' },
    { label: '邀请码 ID', value: record.inviteCodeId ?? '--' },
    { label: '邀请状态', value: (referralStatusMap[record.status || 0] || referralStatusMap[0]).label },
    { label: '风险状态', value: (referralRiskFlagMap[record.riskFlag || 0] || referralRiskFlagMap[0]).label },
    { label: '风险原因', value: record.riskReason || '--' },
    { label: '设备指纹', value: maskText(record.registerDeviceFingerprint) },
    { label: '注册时间', value: formatDateTime(record.registeredAt) },
    { label: '生效时间', value: formatDateTime(record.validatedAt) },
  ]
})

const inviterBlocks = computed(() => buildUserBlocks(detail.value?.inviterInfo))
const inviteeBlocks = computed(() => buildUserBlocks(detail.value?.inviteeInfo))

const riskBlocks = computed(() => {
  const risk = detail.value?.riskInfo
  if (!risk) {
    return []
  }
  return [
    { label: '当前状态', value: (referralStatusMap[risk.status || 0] || referralStatusMap[0]).label },
    { label: '风险标记', value: (referralRiskFlagMap[risk.riskFlag || 0] || referralRiskFlagMap[0]).label },
    { label: '风险原因', value: risk.riskReason || '--' },
    { label: '设备命中数', value: risk.sameDeviceHitCount ?? 0 },
    { label: '关联资格码', value: risk.relatedGrantCodes?.length ? risk.relatedGrantCodes.join(', ') : '--' },
    { label: '设备指纹', value: maskText(risk.registerDeviceFingerprint) },
  ]
})

function buildUserBlocks(user?: ReferralRecordDetail['inviterInfo']) {
  return [
    { label: '用户 ID', value: user?.userId ?? '--' },
    { label: '用户名', value: user?.userName || '--' },
    { label: '昵称', value: user?.nickname || '--' },
    { label: '手机号', value: maskPhone(user?.phone) },
    { label: '实名状态', value: formatRealAuthStatus(user?.realAuthStatus) },
    { label: '有效邀请数', value: user?.validInviteCount ?? 0 },
  ]
}

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

async function loadList() {
  loading.value = true
  try {
    const result = await fetchReferralRecords(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number, row?: ReferralRecordItem) {
  detailVisible.value = true
  detailLoading.value = true
  detail.value = null
  try {
    detail.value = await fetchReferralRecordDetail(id)
    if (!detail.value?.recordInfo && row) {
      detail.value = {
        recordInfo: {
          referralId: row.referralId,
          inviteCode: row.inviteCode,
          status: row.status,
          riskFlag: row.riskFlag,
          registeredAt: row.registeredAt,
          validatedAt: row.validatedAt,
        },
      }
    }
  } finally {
    detailLoading.value = false
  }
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.inviteCode = ''
  filters.inviterUserId = undefined
  filters.inviteeUserId = undefined
  filters.status = undefined
  filters.riskFlag = undefined
  filters.registeredAtFrom = undefined
  filters.registeredAtTo = undefined
  filters.validatedAtFrom = undefined
  filters.validatedAtTo = undefined
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
