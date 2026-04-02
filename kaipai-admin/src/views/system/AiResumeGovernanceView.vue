<template>
  <PageContainer
    title="AI 简历治理"
    eyebrow="AI Resume Governance"
    description="围绕 AI 润色概览、额度消耗、失败样本和人工处置建立第一版真实治理页，当前已补独立 AI 权限，并保留操作日志权限兼容兜底。"
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

    <FilterPanel description="按用户、处理状态、失败类型、关键词和请求 ID 筛选失败样本与敏感命中，优先定位仍待处理的异常。">
      <el-form :model="failureFilters" inline>
        <el-form-item label="用户 ID">
          <el-input v-model.number="failureFilters.userId" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="failureFilters.handlingStatus" clearable style="width: 160px">
            <el-option label="待处理" value="pending" />
            <el-option label="已复核" value="reviewed" />
            <el-option label="建议重试" value="retry_advised" />
          </el-select>
        </el-form-item>
        <el-form-item label="失败类型">
          <el-select v-model="failureFilters.failureType" clearable style="width: 180px">
            <el-option label="敏感命中" value="content_blocked" />
            <el-option label="不可解析" value="response_unparsable" />
            <el-option label="超时" value="model_timeout" />
            <el-option label="上下文无效" value="context_invalid" />
            <el-option label="其他失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="failureFilters.keyword" placeholder="failureId / 指令 / 错误 / 命中词" clearable />
        </el-form-item>
        <el-form-item label="请求 ID">
          <el-input v-model="failureFilters.requestId" placeholder="requestId" clearable />
        </el-form-item>
      </el-form>
      <template #actions>
        <el-button @click="resetFailureFilters">重置</el-button>
        <el-button type="primary" @click="loadFailures">查询</el-button>
      </template>
    </FilterPanel>

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
          <el-table-column label="处理状态" min-width="120">
            <template #default="{ row }">
              <StatusTag v-bind="getFailureHandlingTag(row.handlingStatus)" />
            </template>
          </el-table-column>
          <el-table-column prop="errorCode" label="错误码" min-width="100" />
          <el-table-column prop="errorMessage" label="错误信息" min-width="220" show-overflow-tooltip />
          <el-table-column prop="instruction" label="用户指令" min-width="260" show-overflow-tooltip />
          <el-table-column label="处理信息" min-width="200">
            <template #default="{ row }">
              <div class="stack-cell">
                <strong>{{ row.handledByAdminName || '--' }}</strong>
                <span>{{ row.handledAt ? formatDateTime(row.handledAt) : '待处理' }}</span>
                <span>{{ row.handlingNotes?.length || 0 }} 条处置记录</span>
                <span>{{ row.handlingNote || '--' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" min-width="240">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link @click="openFailureDetail(row)">处置记录</el-button>
                <PermissionButton
                  link
                  action="action.system.ai-resume.review"
                  :fallback-permissions="aiGovernanceFallbackPermissions"
                  @click="openFailureAction('review', row)"
                >
                  人工复核
                </PermissionButton>
                <PermissionButton
                  link
                  type="warning"
                  action="action.system.ai-resume.resolve"
                  :fallback-permissions="aiGovernanceFallbackPermissions"
                  @click="openFailureAction('suggestRetry', row)"
                >
                  建议重试
                </PermissionButton>
              </div>
            </template>
          </el-table-column>
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
          <el-table-column label="处理状态" min-width="120">
            <template #default="{ row }">
              <StatusTag v-bind="getFailureHandlingTag(row.handlingStatus)" />
            </template>
          </el-table-column>
          <el-table-column prop="errorMessage" label="结果" min-width="180" show-overflow-tooltip />
          <el-table-column prop="instruction" label="用户指令" min-width="260" show-overflow-tooltip />
          <el-table-column label="操作" fixed="right" min-width="240">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link @click="openFailureDetail(row)">处置记录</el-button>
                <PermissionButton
                  link
                  action="action.system.ai-resume.review"
                  :fallback-permissions="aiGovernanceFallbackPermissions"
                  @click="openFailureAction('review', row)"
                >
                  人工复核
                </PermissionButton>
                <PermissionButton
                  link
                  type="warning"
                  action="action.system.ai-resume.resolve"
                  :fallback-permissions="aiGovernanceFallbackPermissions"
                  @click="openFailureAction('suggestRetry', row)"
                >
                  建议重试
                </PermissionButton>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </section>

    <section>
      <el-card class="surface-card" shadow="never">
        <template #header>
          <div class="card-head">
            <div>
              <h3>Governance Audit</h3>
              <p>回看 AI 失败样本的人工复核与建议重试动作，确认处理人、结果与上下文。</p>
            </div>
          </div>
        </template>
        <el-form :model="auditFilters" inline class="audit-filter-form">
          <el-form-item label="操作人 ID">
            <el-input v-model.number="auditFilters.adminUserId" placeholder="后台账号 ID" clearable />
          </el-form-item>
          <el-form-item label="动作">
            <el-select v-model="auditFilters.operationCode" clearable style="width: 160px">
              <el-option label="人工复核" value="ai_resume_review" />
              <el-option label="建议重试" value="ai_resume_suggest_retry" />
            </el-select>
          </el-form-item>
          <el-form-item label="结果">
            <el-select v-model="auditFilters.result" clearable style="width: 140px">
              <el-option label="成功" :value="1" />
              <el-option label="失败" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item label="请求 ID">
            <el-input v-model="auditFilters.requestId" placeholder="requestId" clearable />
          </el-form-item>
          <el-form-item label="条数">
            <el-select v-model="auditFilters.pageSize" style="width: 120px">
              <el-option label="10 条" :value="10" />
              <el-option label="20 条" :value="20" />
              <el-option label="50 条" :value="50" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetAuditFilters">重置</el-button>
            <el-button type="primary" @click="loadAuditLogs">查询</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="auditRows" v-loading="auditLoading" empty-text="暂无治理动作日志">
          <el-table-column prop="operationLogId" label="日志 ID" min-width="110" />
          <el-table-column label="操作人" min-width="150">
            <template #default="{ row }">{{ row.adminUserName || row.adminUserId || '--' }}</template>
          </el-table-column>
          <el-table-column label="动作" min-width="160">
            <template #default="{ row }">{{ getGovernanceOperationLabel(row.operationCode) }}</template>
          </el-table-column>
          <el-table-column prop="requestId" label="请求 ID" min-width="180" show-overflow-tooltip />
          <el-table-column label="结果" min-width="100">
            <template #default="{ row }">
              <StatusTag :label="row.operationResult === 1 ? '成功' : '失败'" :tone="row.operationResult === 1 ? 'success' : 'danger'" />
            </template>
          </el-table-column>
          <el-table-column label="时间" min-width="180">
            <template #default="{ row }">{{ formatDateTime(row.createTime) }}</template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" min-width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="openAuditDetail(row.operationLogId)">查看详情</el-button>
            </template>
          </el-table-column>
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

    <el-drawer v-model="auditDetailVisible" title="AI 治理动作详情" size="860px" destroy-on-close>
      <div v-loading="auditDetailLoading" class="detail-layout">
        <template v-if="auditDetail">
          <el-card class="surface-card" shadow="never">
            <template #header><h3>动作概览</h3></template>
            <div class="detail-grid">
              <div v-for="item in auditDetailBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="surface-card" shadow="never">
            <template #header><h3>补充上下文</h3></template>
            <pre class="text-block">{{ auditDetail.extraContextJson || '--' }}</pre>
          </el-card>

          <div class="detail-split">
            <el-card class="surface-card" shadow="never">
              <template #header><h3>变更前</h3></template>
              <pre class="text-block">{{ auditDetail.beforeSnapshotJson || '--' }}</pre>
            </el-card>

            <el-card class="surface-card" shadow="never">
              <template #header><h3>变更后</h3></template>
              <pre class="text-block">{{ auditDetail.afterSnapshotJson || '--' }}</pre>
            </el-card>
          </div>
        </template>
      </div>
    </el-drawer>

    <el-drawer v-model="failureDetailVisible" title="AI 失败样本处置记录" size="760px" destroy-on-close>
      <div class="detail-layout">
        <template v-if="failureDetail">
          <el-card class="surface-card" shadow="never">
            <template #header><h3>样本概览</h3></template>
            <div class="detail-grid">
              <div v-for="item in failureDetailBlocks" :key="item.label" class="detail-block">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="surface-card" shadow="never">
            <template #header><h3>失败上下文</h3></template>
            <div class="detail-grid">
              <div class="detail-block">
                <span>错误信息</span>
                <strong>{{ failureDetail.errorMessage || '--' }}</strong>
              </div>
              <div class="detail-block">
                <span>命中词</span>
                <strong>{{ failureDetail.hitKeyword || '--' }}</strong>
              </div>
              <div class="detail-block detail-block--full">
                <span>用户指令</span>
                <strong>{{ failureDetail.instruction || '--' }}</strong>
              </div>
            </div>
          </el-card>

          <el-card class="surface-card" shadow="never">
            <template #header><h3>处置时间线</h3></template>
            <div v-if="failureDetail.handlingNotes?.length" class="timeline-list">
              <article v-for="(note, index) in failureDetail.handlingNotes" :key="`${note.handledAt || 'note'}-${index}`" class="timeline-item">
                <div class="timeline-item__head">
                  <strong>{{ note.handledByAdminName || note.handledByAdminId || '--' }}</strong>
                  <StatusTag v-bind="getFailureHandlingTag(note.handlingStatus)" />
                </div>
                <p>{{ note.handlingNote || '--' }}</p>
                <span>{{ formatDateTime(note.handledAt) }}</span>
              </article>
            </div>
            <el-empty v-else description="暂无处置记录" />
          </el-card>
        </template>
      </div>
    </el-drawer>

    <AuditConfirmDialog
      v-model="actionVisible"
      :title="actionDialogTitle"
      :confirm-text="actionConfirmText"
      :placeholder="actionPlaceholder"
      :reason-required="true"
      reason-label="处理备注"
      :meta="actionMeta"
      :loading="actionSubmitting"
      @submit="submitFailureAction"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  fetchAdminAiResumeFailures,
  fetchAdminAiResumeHistories,
  fetchAdminAiResumeHistoryDetail,
  fetchAdminAiResumeOverview,
  fetchAdminAiResumeSensitiveHits,
  reviewAdminAiResumeFailure,
  suggestRetryAdminAiResumeFailure,
} from '@/api/ai'
import { fetchAdminOperationLogDetail, fetchAdminOperationLogs } from '@/api/system'
import FilterPanel from '@/components/business/FilterPanel.vue'
import PermissionButton from '@/components/business/PermissionButton.vue'
import PageContainer from '@/components/business/PageContainer.vue'
import StatusTag from '@/components/business/StatusTag.vue'
import AuditConfirmDialog from '@/components/dialogs/AuditConfirmDialog.vue'
import { PERMISSIONS } from '@/constants/permission'
import type {
  AdminAiResumeFailureItem,
  AdminAiResumeFailureQuery,
  AdminAiResumeHistoryItem,
  AdminAiResumeHistoryQuery,
  AdminAiResumeOverview,
} from '@/types/ai'
import type { AdminOperationLogDetail, AdminOperationLogItem, AdminOperationLogQuery } from '@/types/system'
import { formatDateTime, maskPhone } from '@/utils/format'

type FailureActionMode = 'review' | 'suggestRetry'

const overviewLoading = ref(false)
const tableLoading = ref(false)
const detailLoading = ref(false)
const failureLoading = ref(false)
const auditLoading = ref(false)
const auditDetailLoading = ref(false)
const actionVisible = ref(false)
const actionSubmitting = ref(false)
const total = ref(0)
const rows = ref<AdminAiResumeHistoryItem[]>([])
const detailVisible = ref(false)
const detail = ref<AdminAiResumeHistoryItem | null>(null)
const auditRows = ref<AdminOperationLogItem[]>([])
const auditDetailVisible = ref(false)
const auditDetail = ref<AdminOperationLogDetail | null>(null)
const failures = ref<AdminAiResumeFailureItem[]>([])
const sensitiveHits = ref<AdminAiResumeFailureItem[]>([])
const failureDetailVisible = ref(false)
const failureDetail = ref<AdminAiResumeFailureItem | null>(null)
const currentFailure = ref<AdminAiResumeFailureItem | null>(null)
const actionMode = ref<FailureActionMode>('review')
const aiGovernanceFallbackPermissions = [PERMISSIONS.page.systemOperationLogs]

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

const failureFilters = reactive<AdminAiResumeFailureQuery>({
  userId: undefined,
  handlingStatus: '',
  failureType: '',
  keyword: '',
  requestId: '',
  limit: 20,
})

const auditFilters = reactive<AdminOperationLogQuery>({
  pageNo: 1,
  pageSize: 10,
  adminUserId: undefined,
  moduleCode: 'system',
  operationCode: '',
  targetType: 'ai_resume_failure',
  requestId: '',
  result: undefined,
  dateFrom: '',
  dateTo: '',
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

const actionDialogTitle = computed(() => (actionMode.value === 'review' ? '人工复核失败样本' : '标记建议重试'))
const actionConfirmText = computed(() => (actionMode.value === 'review' ? '确认复核' : '确认标记'))
const actionPlaceholder = computed(() =>
  actionMode.value === 'review' ? '请输入复核结论、人工判断或补充备注' : '请输入建议重试原因、观察结论或后续动作',
)
const actionMeta = computed(() => [
  { label: '失败样本', value: currentFailure.value?.failureId || '--' },
  { label: '用户', value: currentFailure.value?.userName || `用户 ${currentFailure.value?.userId ?? '--'}` },
  { label: '错误码', value: currentFailure.value?.errorCode ?? '--' },
  { label: '当前状态', value: getFailureHandlingTag(currentFailure.value?.handlingStatus).label },
])
const auditDetailBlocks = computed(() => {
  if (!auditDetail.value) {
    return []
  }
  return [
    { label: '日志 ID', value: auditDetail.value.operationLogId },
    { label: '操作人', value: auditDetail.value.adminUserName || auditDetail.value.adminUserId || '--' },
    { label: '动作', value: getGovernanceOperationLabel(auditDetail.value.operationCode) },
    { label: '请求 ID', value: auditDetail.value.requestId || '--' },
    { label: '结果', value: auditDetail.value.operationResult === 1 ? '成功' : '失败' },
    { label: '失败原因', value: auditDetail.value.failReason || '--' },
    { label: '确认时间', value: formatDateTime(auditDetail.value.confirmedAt) },
    { label: '创建时间', value: formatDateTime(auditDetail.value.createTime) },
  ]
})
const failureDetailBlocks = computed(() => {
  if (!failureDetail.value) {
    return []
  }
  return [
    { label: '失败样本', value: failureDetail.value.failureId || '--' },
    { label: '用户', value: `${failureDetail.value.userName || '--'} / ${failureDetail.value.userId ?? '--'}` },
    { label: '手机号', value: maskPhone(failureDetail.value.phone) },
    { label: '失败类型', value: getFailureStatusTag(failureDetail.value.failureType).label },
    { label: '处理状态', value: getFailureHandlingTag(failureDetail.value.handlingStatus).label },
    { label: '请求 ID', value: failureDetail.value.requestId || '--' },
    { label: '会话 ID', value: failureDetail.value.conversationId || '--' },
    { label: '错误码', value: failureDetail.value.errorCode ?? '--' },
    { label: '创建时间', value: formatDateTime(failureDetail.value.createdAt) },
    { label: '最近处理', value: formatDateTime(failureDetail.value.handledAt) },
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

function getFailureHandlingTag(status?: string | null) {
  if (status === 'reviewed') {
    return { label: '已复核', tone: 'success' as const }
  }
  if (status === 'retry_advised') {
    return { label: '建议重试', tone: 'warning' as const }
  }
  return { label: '待处理', tone: 'info' as const }
}

function getGovernanceOperationLabel(operationCode?: string | null) {
  if (operationCode === 'ai_resume_review') {
    return '人工复核'
  }
  if (operationCode === 'ai_resume_suggest_retry') {
    return '建议重试'
  }
  return operationCode || '--'
}

function formatLevel(level?: number | null, membershipTier?: string | null) {
  const levelText = level == null ? 'L--' : `L${level}`
  return membershipTier ? `${levelText} / ${membershipTier}` : levelText
}

function buildFailureQuery(): AdminAiResumeFailureQuery {
  return {
    userId: failureFilters.userId,
    handlingStatus: failureFilters.handlingStatus || undefined,
    failureType: failureFilters.failureType || undefined,
    keyword: failureFilters.keyword || undefined,
    requestId: failureFilters.requestId || undefined,
    limit: failureFilters.limit || 20,
  }
}

function syncFailureDetail() {
  if (!failureDetail.value?.failureId) {
    return
  }
  const next = [...failures.value, ...sensitiveHits.value].find((item) => item.failureId === failureDetail.value?.failureId)
  if (next) {
    failureDetail.value = next
  }
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
    const query = buildFailureQuery()
    const [failureData, sensitiveData] = await Promise.all([
      fetchAdminAiResumeFailures(query),
      fetchAdminAiResumeSensitiveHits(query),
    ])
    failures.value = failureData || []
    sensitiveHits.value = sensitiveData || []
    syncFailureDetail()
  } finally {
    failureLoading.value = false
  }
}

async function loadAuditLogs() {
  auditLoading.value = true
  try {
    const result = await fetchAdminOperationLogs({
      pageNo: 1,
      pageSize: auditFilters.pageSize || 10,
      adminUserId: auditFilters.adminUserId,
      moduleCode: 'system',
      operationCode: auditFilters.operationCode || '',
      targetType: 'ai_resume_failure',
      requestId: auditFilters.requestId || '',
      result: auditFilters.result,
      dateFrom: '',
      dateTo: '',
    })
    auditRows.value = result.list || []
  } finally {
    auditLoading.value = false
  }
}

function openFailureAction(mode: FailureActionMode, row: AdminAiResumeFailureItem) {
  currentFailure.value = row
  actionMode.value = mode
  actionVisible.value = true
}

function openFailureDetail(row: AdminAiResumeFailureItem) {
  failureDetail.value = row
  failureDetailVisible.value = true
}

async function openAuditDetail(id: number) {
  auditDetailVisible.value = true
  auditDetailLoading.value = true
  auditDetail.value = null
  try {
    auditDetail.value = await fetchAdminOperationLogDetail(id)
  } finally {
    auditDetailLoading.value = false
  }
}

async function submitFailureAction(reason: string) {
  if (!currentFailure.value?.failureId) {
    return
  }
  actionSubmitting.value = true
  try {
    if (actionMode.value === 'review') {
      await reviewAdminAiResumeFailure(currentFailure.value.failureId, { reason })
      ElMessage.success('失败样本已标记为人工复核')
    } else {
      await suggestRetryAdminAiResumeFailure(currentFailure.value.failureId, { reason })
      ElMessage.success('失败样本已标记为建议重试')
    }
    actionVisible.value = false
    await loadFailures()
    await loadAuditLogs()
  } finally {
    actionSubmitting.value = false
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

function resetFailureFilters() {
  failureFilters.userId = undefined
  failureFilters.handlingStatus = ''
  failureFilters.failureType = ''
  failureFilters.keyword = ''
  failureFilters.requestId = ''
  failureFilters.limit = 20
  loadFailures()
}

function resetAuditFilters() {
  auditFilters.pageNo = 1
  auditFilters.pageSize = 10
  auditFilters.adminUserId = undefined
  auditFilters.operationCode = ''
  auditFilters.requestId = ''
  auditFilters.result = undefined
  loadAuditLogs()
}

onMounted(() => {
  loadOverview()
  loadHistories()
  loadFailures()
  loadAuditLogs()
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

.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.audit-filter-form {
  margin-bottom: 16px;
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

.detail-block--full {
  grid-column: 1 / -1;
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

.timeline-list {
  display: grid;
  gap: 12px;
}

.timeline-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid rgba(47, 36, 27, 0.08);
  border-radius: 16px;
  background: rgba(47, 36, 27, 0.03);

  p,
  span {
    margin: 0;
    color: var(--kp-text-secondary);
    word-break: break-word;
  }
}

.timeline-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
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
