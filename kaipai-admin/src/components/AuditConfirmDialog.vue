<template>
  <el-dialog :model-value="modelValue" :title="title" width="520px" @close="emit('update:modelValue', false)">
    <div class="audit-dialog">
      <strong>{{ targetSummary }}</strong>
      <p v-if="impactHint">{{ impactHint }}</p>
      <code>{{ actionCode }}</code>
      <el-input
        v-model="remark"
        type="textarea"
        :rows="4"
        :placeholder="reasonRequired ? '请输入原因' : '请输入操作备注'"
      />
    </div>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="emit('confirm', remark.trim())">确认提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: boolean
  title: string
  actionCode: string
  targetSummary: string
  impactHint?: string
  reasonRequired?: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [remark: string]
}>()

const remark = ref('')

watch(
  () => props.modelValue,
  (value) => {
    if (!value) {
      remark.value = ''
    }
  },
)
</script>

<style scoped lang="scss">
.audit-dialog {
  display: grid;
  gap: 12px;
}

p,
code {
  color: var(--kp-text-secondary);
}
</style>
