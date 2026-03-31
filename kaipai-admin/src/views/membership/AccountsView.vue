<template>
  <PageContainer title="会员账户" description="账户页直接对接后台已有开通、延期、关闭接口，所有写动作都要求明确备注。">
    <FilterPanel description="当前后端支持按用户、会员层级和状态筛选。">
      <el-form :model="filters" inline>
        <el-form-item label="用户 ID">
          <el-input v-model.number="filters.userId" clearable placeholder="用户 ID" />
        </el-form-item>
        <el-form-item label="会员层级">
          <el-select v-model="filters.tier" clearable style="width: 160px">
            <el-option v-for="option in membershipTierOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="未开通" :value="0" />
            <el-option label="生效中" :value="1" />
            <el-option label="已过期" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #actions>
        <PermissionButton action="action.membership.account.open" type="primary" @click="openDialog('open')">手工开通</PermissionButton>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="loadList">查询</el-button>
      </template>
    </FilterPanel>

    <el-card class="table-card" shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="userId" label="用户 ID" min-width="100" />
        <el-table-column label="层级" min-width="120">
          <template #default="{ row }">{{ getTierLabel(row.tier) }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="membershipStatusMap[row.status] || membershipStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="生效时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.effectiveTime) }}</template>
        </el-table-column>
        <el-table-column label="过期时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.expireTime) }}</template>
        </el-table-column>
        <el-table-column prop="sourceType" label="来源" min-width="120" />
        <el-table-column label="操作" fixed="right" min-width="240">
          <template #default="{ row }">
            <PermissionButton link type="primary" action="action.membership.account.extend" @click="openDialog('extend', row)">延期</PermissionButton>
            <PermissionButton link type="danger" action="action.membership.account.close" @click="openDialog('close', row)">关闭</PermissionButton>
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
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="580px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="用户 ID">
          <el-input v-model.number="form.userId" :disabled="dialogMode !== 'open'" />
        </el-form-item>
        <template v-if="dialogMode === 'open'">
          <el-form-item label="会员层级">
            <el-select v-model="form.tier" style="width: 100%">
              <el-option v-for="option in membershipTierOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="生效时间">
            <el-date-picker v-model="form.effectiveTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="过期时间">
            <el-date-picker v-model="form.expireTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="来源类型">
            <el-input v-model="form.sourceType" placeholder="manual_grant" />
          </el-form-item>
          <el-form-item label="来源单据 ID">
            <el-input v-model.number="form.sourceRefId" />
          </el-form-item>
        </template>
        <el-form-item v-if="dialogMode === 'extend'" label="新的过期时间">
          <el-date-picker v-model="form.expireTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确认</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { membershipStatusMap, membershipTierOptions } from '@/constants/status'
import {
  closeMembershipAccount,
  extendMembershipAccount,
  fetchMembershipAccounts,
  openMembershipAccount,
} from '@/api/membership'
import { formatDateTime } from '@/utils/format'
import type { MembershipAccount, MembershipAccountQuery } from '@/types/membership'

const loading = ref(false)
const submitting = ref(false)
const rows = ref<MembershipAccount[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const dialogMode = ref<'open' | 'extend' | 'close'>('open')

const filters = reactive<MembershipAccountQuery>({
  pageNo: 1,
  pageSize: 20,
  userId: undefined,
  tier: undefined,
  status: undefined,
})

const form = reactive({
  userId: undefined as number | undefined,
  tier: 1,
  effectiveTime: '',
  expireTime: '',
  sourceType: 'manual_grant',
  sourceRefId: undefined as number | undefined,
  remark: '',
})

const dialogTitle = computed(() => {
  if (dialogMode.value === 'extend') {
    return '会员延期'
  }
  if (dialogMode.value === 'close') {
    return '关闭会员'
  }
  return '手工开通会员'
})

function getTierLabel(value: number) {
  return membershipTierOptions.find((item) => item.value === value)?.label || `Tier ${value}`
}

async function loadList() {
  loading.value = true
  try {
    const result = await fetchMembershipAccounts(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function openDialog(mode: 'open' | 'extend' | 'close', row?: MembershipAccount) {
  dialogMode.value = mode
  dialogVisible.value = true
  form.userId = row?.userId
  form.tier = row?.tier || 1
  form.effectiveTime = row?.effectiveTime || ''
  form.expireTime = row?.expireTime || ''
  form.sourceType = 'manual_grant'
  form.sourceRefId = row?.sourceRefId
  form.remark = ''
}

async function submit() {
  if (!form.userId) {
    ElMessage.warning('请输入用户 ID')
    return
  }

  submitting.value = true
  try {
    if (dialogMode.value === 'open') {
      await openMembershipAccount(form.userId, {
        tier: form.tier,
        effectiveTime: form.effectiveTime,
        expireTime: form.expireTime,
        sourceType: form.sourceType,
        sourceRefId: form.sourceRefId,
        remark: form.remark,
      })
    } else if (dialogMode.value === 'extend') {
      await extendMembershipAccount(form.userId, {
        expireTime: form.expireTime,
        remark: form.remark,
      })
    } else {
      await closeMembershipAccount(form.userId, {
        remark: form.remark,
      })
    }
    ElMessage.success('会员账户操作已提交')
    dialogVisible.value = false
    loadList()
  } finally {
    submitting.value = false
  }
}

function resetFilters() {
  filters.userId = undefined
  filters.tier = undefined
  filters.status = undefined
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

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
