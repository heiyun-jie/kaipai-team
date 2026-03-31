<template>
  <PageContainer :title="title" :description="description">
    <FilterPanel description="后端当前筛选能力较少，本轮以前后端已存在字段为准。">
      <el-form :model="filters" inline>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="待审核" :value="1" />
            <el-option label="已通过" :value="2" />
            <el-option label="已拒绝" :value="3" />
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
        <el-table-column prop="verificationId" label="申请单号" min-width="120" />
        <el-table-column prop="userId" label="用户 ID" min-width="100" />
        <el-table-column label="用户信息" min-width="180">
          <template #default="{ row }">
            <div class="stack-cell">
              <strong>{{ row.userName }}</strong>
              <span>{{ row.phone || '--' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="realName" label="真实姓名" min-width="120" />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="verifyStatusMap[row.status] || verifyStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="提交时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.submitTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.verificationId)">查看详情</el-button>
            <PermissionButton
              v-if="mode === 'pending' && row.status === 1"
              link
              type="success"
              action="action.verify.approve"
              @click="openAudit('approve', row)"
            >
              审核通过
            </PermissionButton>
            <PermissionButton
              v-if="mode === 'pending' && row.status === 1"
              link
              type="danger"
              action="action.verify.reject"
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
          layout="total, prev, pager, next"
          :total="total"
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="认证申请详情" size="520px">
      <div v-if="detail" class="detail-grid">
        <div class="detail-block">
          <span>申请单号</span>
          <strong>{{ detail.verificationId }}</strong>
        </div>
        <div class="detail-block">
          <span>用户</span>
          <strong>{{ detail.userName }} / {{ detail.userId }}</strong>
        </div>
        <div class="detail-block">
          <span>手机号</span>
          <strong>{{ detail.phone || '--' }}</strong>
        </div>
        <div class="detail-block">
          <span>真实姓名</span>
          <strong>{{ detail.realName }}</strong>
        </div>
        <div class="detail-block">
          <span>身份证</span>
          <strong>{{ maskText(detail.idCardNoCipher) }}</strong>
        </div>
        <div class="detail-block">
          <span>演员认证结果</span>
          <strong>{{ detail.actorCertified ? '已回写' : '未回写' }}</strong>
        </div>
        <div class="detail-block">
          <span>提交时间</span>
          <strong>{{ formatDateTime(detail.submitTime) }}</strong>
        </div>
        <div class="detail-block">
          <span>审核时间</span>
          <strong>{{ formatDateTime(detail.reviewedAt) }}</strong>
        </div>
        <div class="detail-block detail-block--wide">
          <span>拒绝原因</span>
          <strong>{{ detail.rejectReason || '--' }}</strong>
        </div>
      </div>
    </el-drawer>

    <AuditConfirmDialog
      v-model="auditVisible"
      :title="auditMode === 'approve' ? '确认审核通过' : '确认审核拒绝'"
      :confirm-text="auditMode === 'approve' ? '确认通过' : '确认拒绝'"
      :reason-label="auditMode === 'approve' ? '审核备注' : '拒绝原因'"
      :placeholder="auditMode === 'approve' ? '请输入审核备注' : '请输入拒绝原因'"
      :meta="auditMeta"
      @submit="submitAudit"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { approveVerify, fetchVerifyDetail, fetchVerifyList, rejectVerify } from '@/api/verify'
import { verifyStatusMap } from '@/constants/status'
import { formatDateTime, maskText } from '@/utils/format'
import type { VerifyDetail, VerifyListItem, VerifyQuery } from '@/types/verify'

const props = defineProps<{
  mode: 'pending' | 'history'
}>()

const title = computed(() => (props.mode === 'pending' ? '实名认证待审核' : '实名认证历史'))
const description = computed(() =>
  props.mode === 'pending'
    ? '以 `/admin/verify/list` 和 `/admin/verify/{id}` 为准，审核动作独立走通过/拒绝接口。'
    : '当前后端列表接口按单状态查询，本页作为历史检索入口，允许按状态回看。'
)

const loading = ref(false)
const rows = ref<VerifyListItem[]>([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref<VerifyDetail | null>(null)
const auditVisible = ref(false)
const auditMode = ref<'approve' | 'reject'>('approve')
const currentRow = ref<VerifyListItem | null>(null)

const filters = reactive<VerifyQuery>({
  userId: undefined,
  status: props.mode === 'pending' ? 1 : undefined,
  pageNo: 1,
  pageSize: 20,
})

const auditMeta = computed(() => [
  { label: '申请单号', value: currentRow.value?.verificationId },
  { label: '用户', value: currentRow.value?.userName },
  { label: '目标动作', value: auditMode.value === 'approve' ? '审核通过' : '审核拒绝' },
])

async function loadList() {
  loading.value = true
  try {
    const result = await fetchVerifyList(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function openDetail(id: number) {
  detail.value = await fetchVerifyDetail(id)
  detailVisible.value = true
}

function openAudit(mode: 'approve' | 'reject', row: VerifyListItem) {
  auditMode.value = mode
  currentRow.value = row
  auditVisible.value = true
}

async function submitAudit(remark: string) {
  if (!currentRow.value) {
    return
  }
  if (!remark) {
    ElMessage.warning(auditMode.value === 'approve' ? '请输入审核备注' : '请输入拒绝原因')
    return
  }

  if (auditMode.value === 'approve') {
    await approveVerify(currentRow.value.verificationId, { remark })
  } else {
    await rejectVerify(currentRow.value.verificationId, { remark })
  }

  ElMessage.success('审核操作已提交')
  auditVisible.value = false
  loadList()
}

function resetFilters() {
  filters.userId = undefined
  filters.status = props.mode === 'pending' ? 1 : undefined
  filters.pageNo = 1
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

.detail-grid {
  display: grid;
  gap: 14px;
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
  }
}

.detail-block--wide {
  min-height: 96px;
}
</style>
