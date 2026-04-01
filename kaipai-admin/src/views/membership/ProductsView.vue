<template>
  <PageContainer title="会员产品" description="维护会员产品方案，统一管理定价、时长与权益配置。">
    <template #actions>
      <PermissionButton action="action.membership.product.create" type="primary" @click="dialogVisible = true">
        新建产品
      </PermissionButton>
    </template>

    <FilterPanel description="按会员层级和状态筛选产品，便于日常维护与检查。">
      <el-form :model="filters" inline>
        <el-form-item label="会员层级">
          <el-select v-model="filters.membershipTier" clearable style="width: 160px">
            <el-option v-for="option in membershipTierOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="草稿" :value="0" />
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="2" />
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
        <el-table-column prop="productCode" label="产品编码" min-width="140" />
        <el-table-column prop="productName" label="产品名称" min-width="180" />
        <el-table-column label="会员层级" min-width="120">
          <template #default="{ row }">{{ getTierLabel(row.membershipTier) }}</template>
        </el-table-column>
        <el-table-column prop="durationDays" label="时长(天)" min-width="100" />
        <el-table-column prop="listPrice" label="原价" min-width="100" />
        <el-table-column prop="salePrice" label="售价" min-width="100" />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag :label="row.status === 1 ? '启用' : row.status === 2 ? '停用' : '草稿'" :tone="row.status === 1 ? 'success' : row.status === 2 ? 'danger' : 'info'" />
          </template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.updateTime) }}</template>
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

    <el-dialog v-model="dialogVisible" title="新建会员产品" width="680px" destroy-on-close>
      <el-form label-position="top" :model="form">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="产品编码"><el-input v-model="form.productCode" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="产品名称"><el-input v-model="form.productName" /></el-form-item></el-col>
          <el-col :span="12">
            <el-form-item label="会员层级">
              <el-select v-model="form.membershipTier" style="width: 100%">
                <el-option v-for="option in membershipTierOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="时长(天)"><el-input-number v-model="form.durationDays" :min="1" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="原价"><el-input-number v-model="form.listPrice" :min="0" :precision="2" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="售价"><el-input-number v-model="form.salePrice" :min="0" :precision="2" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="权益 JSON"><el-input v-model="form.benefitConfigJson" type="textarea" :rows="5" placeholder='{"cards":["share.poster"]}' /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">创建产品</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { membershipTierOptions } from '@/constants/status'
import { createMembershipProduct, fetchMembershipProducts } from '@/api/membership'
import { formatDateTime } from '@/utils/format'
import type { MembershipProductCreatePayload, MembershipProductQuery, MembershipProduct } from '@/types/membership'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const rows = ref<MembershipProduct[]>([])
const total = ref(0)

const filters = reactive<MembershipProductQuery>({
  pageNo: 1,
  pageSize: 20,
  membershipTier: undefined,
  status: undefined,
})

const form = reactive<MembershipProductCreatePayload>({
  productCode: '',
  productName: '',
  membershipTier: 1,
  durationDays: 30,
  listPrice: 0,
  salePrice: 0,
  benefitConfigJson: '',
  sortNo: 0,
})

function getTierLabel(value: number) {
  return membershipTierOptions.find((item) => item.value === value)?.label || `Tier ${value}`
}

async function loadList() {
  loading.value = true
  try {
    const result = await fetchMembershipProducts(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!form.productCode || !form.productName) {
    ElMessage.warning('请补齐产品编码和产品名称')
    return
  }
  submitting.value = true
  try {
    await createMembershipProduct(form)
    ElMessage.success('产品已创建')
    dialogVisible.value = false
    resetForm()
    loadList()
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  form.productCode = ''
  form.productName = ''
  form.membershipTier = 1
  form.durationDays = 30
  form.listPrice = 0
  form.salePrice = 0
  form.benefitConfigJson = ''
  form.sortNo = 0
}

function resetFilters() {
  filters.membershipTier = undefined
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
