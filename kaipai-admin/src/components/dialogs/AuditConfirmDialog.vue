<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title: string
    summary?: string
    requireReason?: boolean
    confirmText?: string
    loading?: boolean
    placeholder?: string
    actionCode?: string
    targetSummary?: string
    impactHint?: string
    reasonRequired?: boolean
    reasonLabel?: string
    meta?: Array<{ label: string; value?: string | number | null }>
  }>(),
  {
    requireReason: false,
    reasonRequired: false,
    confirmText: '确认提交',
    placeholder: '请输入操作备注',
    reasonLabel: '操作备注',
    meta: () => [],
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [reason: string]
  confirm: [reason: string]
}>()

const state = reactive({
  reason: '',
})

const finalSummary = computed(() => props.summary || props.targetSummary || '')
const finalRequireReason = computed(() => props.requireReason || props.reasonRequired)

watch(
  () => props.modelValue,
  (value) => {
    if (!value) {
      state.reason = ''
    }
  },
)

function close() {
  emit('update:modelValue', false)
}

function submit() {
  if (finalRequireReason.value && !state.reason.trim()) {
    return
  }
  emit('submit', state.reason.trim())
  emit('confirm', state.reason.trim())
}
</script>

<template>
  <el-dialog :model-value="modelValue" :title="title" width="460px" @close="close">
    <div class="dialog-content">
      <p v-if="finalSummary" class="dialog-summary">{{ finalSummary }}</p>
      <ul v-if="meta.length" class="dialog-meta">
        <li v-for="item in meta" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value ?? '--' }}</strong>
        </li>
      </ul>
      <p v-if="impactHint" class="dialog-summary">{{ impactHint }}</p>
      <el-input
        v-model="state.reason"
        type="textarea"
        :rows="4"
        :placeholder="placeholder"
      />
      <span v-if="finalRequireReason" class="dialog-tip">{{ reasonLabel }}为必填。</span>
      <span v-else-if="actionCode" class="dialog-tip">权限码：{{ actionCode }}</span>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit">{{ confirmText }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-summary {
  margin: 0;
  color: var(--kp-ink-soft);
  line-height: 1.6;
}

.dialog-meta {
  display: grid;
  gap: 8px;
  padding: 0;
  margin: 0;
  list-style: none;

  li {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(29, 23, 18, 0.05);
  }

  span {
    color: var(--kp-text-secondary);
  }
}

.dialog-tip {
  color: var(--kp-ink-faint);
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

