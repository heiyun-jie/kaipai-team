<template>
  <PageContainer title="场景模板" description="围绕模板列表、草稿编辑、发布和回滚建立第一轮配置闭环。">
    <template #actions>
      <PermissionButton action="action.content.template.create" type="primary" @click="openCreate">新建模板</PermissionButton>
    </template>

    <FilterPanel description="按场景、状态和层级筛选模板，便于日常配置与版本维护。">
      <el-form :model="filters" inline>
        <el-form-item label="场景">
          <el-input v-model="filters.sceneKey" clearable placeholder="sceneKey" />
        </el-form-item>
        <el-form-item label="层级">
          <el-input v-model="filters.tier" clearable placeholder="tier" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option label="草稿" :value="0" />
            <el-option label="已发布" :value="1" />
            <el-option label="已停用" :value="2" />
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
        <el-table-column prop="templateCode" label="模板编码" min-width="140" />
        <el-table-column prop="templateName" label="模板名称" min-width="180" />
        <el-table-column prop="sceneKey" label="场景" min-width="120" />
        <el-table-column prop="tier" label="层级" min-width="120" />
        <el-table-column prop="requiredLevel" label="等级门槛" min-width="100" />
        <el-table-column label="会员要求" min-width="110">
          <template #default="{ row }">{{ row.membershipRequired ? '会员' : '不限' }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <StatusTag v-bind="templateStatusMap[row.status] || templateStatusMap[0]" />
          </template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="180">
          <template #default="{ row }">{{ formatDateTime(row.updateTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="260">
          <template #default="{ row }">
            <div class="table-actions">
              <PermissionButton link type="primary" action="action.content.template.edit" @click="openEdit(row)">基础编辑</PermissionButton>
              <PermissionButton link type="success" action="action.content.template.publish" @click="openPublish(row)">发布</PermissionButton>
              <PermissionButton link type="danger" action="action.content.template.rollback" @click="openRollback(row)">回滚</PermissionButton>
            </div>
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

    <el-dialog v-model="editorVisible" :title="editorMode === 'create' ? '新建模板' : '基础编辑'" width="720px" destroy-on-close>
      <el-form label-position="top" :model="editorForm">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="模板编码"><el-input v-model="editorForm.templateCode" :disabled="editorMode === 'edit'" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="模板名称"><el-input v-model="editorForm.templateName" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="场景"><el-input v-model="editorForm.sceneKey" :disabled="editorMode === 'edit'" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="层级"><el-input v-model="editorForm.tier" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="布局变体"><el-input v-model="editorForm.layoutVariant" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="等级门槛"><el-input-number v-model="editorForm.requiredLevel" :min="0" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-select v-model="editorForm.status" style="width: 100%"><el-option label="草稿" :value="0" /><el-option label="已发布" :value="1" /><el-option label="已停用" :value="2" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="排序"><el-input-number v-model="editorForm.sortNo" :min="0" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="说明"><el-input v-model="editorForm.description" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="主题 JSON"><el-input v-model="editorForm.baseThemeJson" type="textarea" :rows="5" placeholder='{"colors":{"primary":"#c44d34"}}' /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="分享产物 JSON"><el-input v-model="editorForm.artifactPresetJson" type="textarea" :rows="5" placeholder='{"poster":{"title":"..."}}' /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEditor">{{ editorMode === 'create' ? '创建模板' : '保存修改' }}</el-button>
      </template>
    </el-dialog>

    <AuditConfirmDialog
      v-model="publishVisible"
      title="发布模板"
      confirm-text="确认发布"
      reason-label="发布说明"
      placeholder="请输入版本说明"
      :meta="publishMeta"
      @submit="submitPublish"
    />

    <AuditConfirmDialog
      v-model="rollbackVisible"
      title="回滚模板"
      confirm-text="确认回滚"
      reason-label="回滚说明"
      placeholder="请输入回滚原因"
      :meta="rollbackMeta"
      @submit="submitRollback"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import { createTemplate, fetchTemplates, publishTemplate, rollbackTemplate, updateTemplate } from '@/api/content'
import { templateStatusMap } from '@/constants/status'
import { formatDateTime } from '@/utils/format'
import type { CreateTemplatePayload, TemplateItem, TemplateQuery, UpdateTemplatePayload } from '@/types/content'

const loading = ref(false)
const submitting = ref(false)
const rows = ref<TemplateItem[]>([])
const total = ref(0)
const editorVisible = ref(false)
const editorMode = ref<'create' | 'edit'>('create')
const publishVisible = ref(false)
const rollbackVisible = ref(false)
const currentRow = ref<TemplateItem | null>(null)

const filters = reactive<TemplateQuery>({
  pageNo: 1,
  pageSize: 20,
  sceneKey: '',
  status: undefined,
  tier: '',
})

const editorForm = reactive<CreateTemplatePayload & UpdateTemplatePayload>({
  templateCode: '',
  templateName: '',
  sceneKey: '',
  description: '',
  layoutVariant: '',
  tier: '',
  requiredLevel: 0,
  membershipRequired: false,
  baseThemeJson: '',
  artifactPresetJson: '',
  status: 0,
  sortNo: 0,
})

const publishMeta = computed(() => [
  { label: '模板', value: currentRow.value?.templateName },
  { label: '模板编码', value: currentRow.value?.templateCode },
  { label: '当前状态', value: templateStatusMap[currentRow.value?.status || 0]?.label },
])

const rollbackMeta = computed(() => [
  { label: '模板', value: currentRow.value?.templateName },
  { label: '模板编码', value: currentRow.value?.templateCode },
  { label: '回滚来源版本', value: '需手动填写 sourceVersion' },
])

async function loadList() {
  loading.value = true
  try {
    const result = await fetchTemplates(filters)
    rows.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editorMode.value = 'create'
  editorVisible.value = true
  resetEditorForm()
}

function openEdit(row: TemplateItem) {
  editorMode.value = 'edit'
  currentRow.value = row
  editorVisible.value = true
  editorForm.templateCode = row.templateCode
  editorForm.templateName = row.templateName
  editorForm.sceneKey = row.sceneKey
  editorForm.tier = row.tier
  editorForm.requiredLevel = row.requiredLevel
  editorForm.membershipRequired = row.membershipRequired
  editorForm.status = row.status
  editorForm.sortNo = row.sortNo
}

function openPublish(row: TemplateItem) {
  currentRow.value = row
  publishVisible.value = true
}

function openRollback(row: TemplateItem) {
  currentRow.value = row
  rollbackVisible.value = true
}

async function submitEditor() {
  if (!editorForm.templateCode || !editorForm.templateName || !editorForm.sceneKey) {
    ElMessage.warning('请补齐模板编码、模板名称和场景')
    return
  }

  submitting.value = true
  try {
    if (editorMode.value === 'create') {
      await createTemplate(editorForm)
    } else if (currentRow.value) {
      await updateTemplate(currentRow.value.templateId, editorForm)
    }
    ElMessage.success(editorMode.value === 'create' ? '模板已创建' : '模板已更新')
    editorVisible.value = false
    loadList()
  } finally {
    submitting.value = false
  }
}

async function submitPublish(publishNote: string) {
  if (!currentRow.value) {
    return
  }
  await publishTemplate(currentRow.value.templateId, {
    publishVersion: `manual-${Date.now()}`,
    publishNote,
  })
  ElMessage.success('模板发布已提交')
  publishVisible.value = false
  loadList()
}

async function submitRollback(reason: string) {
  if (!currentRow.value) {
    return
  }

  const sourceVersion = await ElMessageBox.prompt('请输入 sourceVersion', '回滚版本', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPlaceholder: '例如 v2026.03.31',
  }).then((result) => result.value)

  await rollbackTemplate(currentRow.value.templateId, {
    sourceVersion,
    publishNote: reason,
  })
  ElMessage.success('模板回滚已提交')
  rollbackVisible.value = false
  loadList()
}

function resetEditorForm() {
  editorForm.templateCode = ''
  editorForm.templateName = ''
  editorForm.sceneKey = ''
  editorForm.description = ''
  editorForm.layoutVariant = ''
  editorForm.tier = ''
  editorForm.requiredLevel = 0
  editorForm.membershipRequired = false
  editorForm.baseThemeJson = ''
  editorForm.artifactPresetJson = ''
  editorForm.status = 0
  editorForm.sortNo = 0
}

function resetFilters() {
  filters.sceneKey = ''
  filters.tier = ''
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
