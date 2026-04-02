<template>
  <PageContainer
    title="招募角色"
    eyebrow="Recruit Roles"
    description="查看真实 `recruit_post` 与项目扩展字段的组装结果，确认角色、项目和剧组的映射没有继续停留在 mock。"
  >
    <FilterPanel description="按角色、剧组、项目和状态筛选，优先核对写侧创建后的真实落库结果。">
      <el-form :model="filters" inline>
        <el-form-item label="角色 ID">
          <el-input v-model.number="filters.roleId" placeholder="角色 ID" clearable />
        </el-form-item>
        <el-form-item label="剧组用户 ID">
          <el-input v-model.number="filters.crewUserId" placeholder="剧组用户 ID" clearable />
        </el-form-item>
        <el-form-item label="项目 ID">
          <el-input v-model.number="filters.projectId" placeholder="项目 ID" clearable />
        </el-form-item>
        <el-form-item label="角色状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="招募中" value="recruiting" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已结束" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="角色 / 项目 / 剧组" clearable />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="roleId" label="角色 ID" min-width="120" />
        <el-table-column label="角色" min-width="260">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.roleName || '--' }}</strong>
              <span>{{ row.requirement || '未补角色要求' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="项目 / 剧组" min-width="240">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.projectTitle || '--' }}</strong>
              <span>{{ row.companyName || '--' }} / 用户 {{ row.crewUserId ?? '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="recruitRoleStatusMap[row.status || 'paused'] || recruitRoleStatusMap.paused" />
          </template>
        </el-table-column>
        <el-table-column label="条件" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.gender || '不限' }} / {{ formatAgeRange(row) }}</strong>
              <span>{{ row.fee || '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="applyCount" label="投递数" min-width="90" />
        <el-table-column prop="deadline" label="截止时间" min-width="120" />
        <el-table-column prop="publishTime" label="发布时间" min-width="180" />
        <el-table-column label="操作" fixed="right" min-width="320">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="openDetail(row)">查看详情</el-button>
              <PermissionButton
                v-if="row.status !== 'recruiting'"
                link
                type="success"
                action="action.recruit.role.status"
                :fallback-permissions="roleActionFallbacks"
                hide-if-denied
                @click="openRoleStatus(row, 'recruiting')"
              >
                恢复招募
              </PermissionButton>
              <PermissionButton
                v-if="row.status !== 'paused'"
                link
                type="warning"
                action="action.recruit.role.status"
                :fallback-permissions="roleActionFallbacks"
                hide-if-denied
                @click="openRoleStatus(row, 'paused')"
              >
                暂停
              </PermissionButton>
              <PermissionButton
                v-if="row.status !== 'closed'"
                link
                type="danger"
                action="action.recruit.role.status"
                :fallback-permissions="roleActionFallbacks"
                hide-if-denied
                @click="openRoleStatus(row, 'closed')"
              >
                结束
              </PermissionButton>
            </div>
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

    <el-drawer v-model="detailVisible" title="角色详情" size="760px">
      <div v-if="detail" class="detail-layout">
        <div class="detail-actions">
          <PermissionButton
            v-if="detail.status !== 'recruiting'"
            type="success"
            action="action.recruit.role.status"
            :fallback-permissions="roleActionFallbacks"
            hide-if-denied
            @click="openRoleStatus(detail, 'recruiting')"
          >
            恢复招募
          </PermissionButton>
          <PermissionButton
            v-if="detail.status !== 'paused'"
            type="warning"
            action="action.recruit.role.status"
            :fallback-permissions="roleActionFallbacks"
            hide-if-denied
            @click="openRoleStatus(detail, 'paused')"
          >
            暂停
          </PermissionButton>
          <PermissionButton
            v-if="detail.status !== 'closed'"
            type="danger"
            action="action.recruit.role.status"
            :fallback-permissions="roleActionFallbacks"
            hide-if-denied
            @click="openRoleStatus(detail, 'closed')"
          >
            结束
          </PermissionButton>
        </div>
        <div class="detail-grid">
          <div v-for="item in detailBlocks" :key="item.label" class="detail-block">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </div>
    </el-drawer>

    <AuditConfirmDialog
      v-model="roleStatusVisible"
      :title="roleStatusTitle"
      :summary="roleStatusSummary"
      :confirm-text="roleStatusConfirmText"
      reason-label="处置备注"
      placeholder="请输入状态校准备注，可留空"
      action-code="action.recruit.role.status"
      :loading="roleStatusLoading"
      :meta="roleStatusMeta"
      @submit="submitRoleStatus"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchAdminRecruitRoles, updateAdminRecruitRoleStatus } from '@/api/recruit'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { recruitRoleStatusMap } from '@/constants/status'
import type { AdminRecruitRoleItem, AdminRecruitRoleQuery } from '@/types/recruit'

const roleActionFallbacks = ['page.system.admin-users']

const loading = ref(false)
const rows = ref<AdminRecruitRoleItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<AdminRecruitRoleItem | null>(null)
const roleStatusVisible = ref(false)
const roleStatusLoading = ref(false)
const currentRole = ref<AdminRecruitRoleItem | null>(null)
const roleStatusTarget = ref<'recruiting' | 'paused' | 'closed'>('paused')

const filters = reactive<AdminRecruitRoleQuery>({
  pageNo: 1,
  pageSize: 20,
  roleId: undefined,
  crewUserId: undefined,
  projectId: undefined,
  status: '',
  keyword: '',
})

const detailBlocks = computed(() => {
  if (!detail.value) {
    return []
  }
  return [
    { label: '角色 ID', value: detail.value.roleId ?? '--' },
    { label: '剧组用户 ID', value: detail.value.crewUserId ?? '--' },
    { label: '项目 ID', value: detail.value.projectId ?? '--' },
    { label: '项目名称', value: detail.value.projectTitle || '--' },
    { label: '剧组名称', value: detail.value.companyName || '--' },
    { label: '角色名称', value: detail.value.roleName || '--' },
    { label: '状态', value: (recruitRoleStatusMap[detail.value.status || 'paused'] || recruitRoleStatusMap.paused).label },
    { label: '性别要求', value: detail.value.gender || '--' },
    { label: '年龄范围', value: formatAgeRange(detail.value) },
    { label: '报酬', value: detail.value.fee || '--' },
    { label: '拍摄地', value: detail.value.location || '--' },
    { label: '联系人', value: detail.value.contactName || '--' },
    { label: '联系电话', value: detail.value.contactPhone || '--' },
    { label: '截止时间', value: detail.value.deadline || '--' },
    { label: '投递数', value: detail.value.applyCount ?? 0 },
    { label: '标签', value: detail.value.tags?.length ? detail.value.tags.join('、') : '--' },
    { label: '角色要求', value: detail.value.requirement || '--' },
    { label: '发布时间', value: detail.value.publishTime || '--' },
  ]
})

const roleStatusMeta = computed(() => [
  { label: '角色 ID', value: currentRole.value?.roleId },
  { label: '角色名称', value: currentRole.value?.roleName || '--' },
  { label: '项目', value: currentRole.value?.projectTitle || '--' },
  {
    label: '当前状态',
    value: (recruitRoleStatusMap[currentRole.value?.status || 'paused'] || recruitRoleStatusMap.paused).label,
  },
  {
    label: '目标状态',
    value: (recruitRoleStatusMap[roleStatusTarget.value] || recruitRoleStatusMap.paused).label,
  },
])

const roleStatusTitle = computed(() => {
  if (roleStatusTarget.value === 'recruiting') {
    return '确认恢复角色招募'
  }
  if (roleStatusTarget.value === 'closed') {
    return '确认结束角色招募'
  }
  return '确认暂停角色招募'
})

const roleStatusConfirmText = computed(() => {
  if (roleStatusTarget.value === 'recruiting') {
    return '确认恢复'
  }
  if (roleStatusTarget.value === 'closed') {
    return '确认结束'
  }
  return '确认暂停'
})

const roleStatusSummary = computed(() => {
  if (roleStatusTarget.value === 'recruiting') {
    return '恢复招募前会校验关联项目是否仍处于进行中，项目已结束的角色不能直接恢复。'
  }
  if (roleStatusTarget.value === 'closed') {
    return '结束后演员端将不再展示该角色，已存在的投递记录仍保留给后台继续查看。'
  }
  return '暂停后演员端会立即隐藏该角色，但不会删除已有投递记录。'
})

async function loadList() {
  loading.value = true
  try {
    const params = {
      ...filters,
      status: filters.status || undefined,
    }
    const result = await fetchAdminRecruitRoles(params)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function openDetail(row: AdminRecruitRoleItem) {
  detail.value = row
  detailVisible.value = true
}

function openRoleStatus(row: AdminRecruitRoleItem, status: 'recruiting' | 'paused' | 'closed') {
  currentRole.value = row
  roleStatusTarget.value = status
  roleStatusVisible.value = true
}

async function submitRoleStatus(reason: string) {
  if (!currentRole.value) {
    return
  }
  roleStatusLoading.value = true
  try {
    await updateAdminRecruitRoleStatus(currentRole.value.roleId, {
      status: roleStatusTarget.value,
      reason,
    })
    ElMessage.success(`角色状态已更新为${(recruitRoleStatusMap[roleStatusTarget.value] || recruitRoleStatusMap.paused).label}`)
    applyRoleStatusLocally(currentRole.value.roleId, roleStatusTarget.value)
    roleStatusVisible.value = false
    await loadList()
  } finally {
    roleStatusLoading.value = false
  }
}

function applyRoleStatusLocally(roleId: number, status: 'recruiting' | 'paused' | 'closed') {
  rows.value = rows.value.map((item) => (item.roleId === roleId ? { ...item, status } : item))
  if (detail.value?.roleId === roleId) {
    detail.value = {
      ...detail.value,
      status,
    }
  }
}

function formatAgeRange(row: Pick<AdminRecruitRoleItem, 'minAge' | 'maxAge'>) {
  if (row.minAge && row.maxAge) {
    return `${row.minAge}-${row.maxAge}`
  }
  if (row.minAge) {
    return `${row.minAge}+`
  }
  if (row.maxAge) {
    return `<=${row.maxAge}`
  }
  return '不限'
}

function resetFilters() {
  filters.pageNo = 1
  filters.pageSize = 20
  filters.roleId = undefined
  filters.crewUserId = undefined
  filters.projectId = undefined
  filters.status = ''
  filters.keyword = ''
  loadList()
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.table-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.stack-cell {
  display: grid;
  gap: 4px;

  strong {
    font-size: 13px;
  }

  span {
    color: var(--kp-text-secondary);
    font-size: 12px;
    line-height: 1.5;
  }
}

.table-actions,
.detail-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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
    word-break: break-word;
  }
}

@media (max-width: 820px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
