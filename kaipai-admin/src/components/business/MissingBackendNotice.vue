<template>
  <el-card class="missing-backend-notice" shadow="never">
    <strong>{{ title }}</strong>
    <p>{{ description }}</p>
    <code v-if="endpointHint">{{ endpointHint }}</code>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  endpointHint?: string
}>()
</script>

<style scoped lang="scss">
.missing-backend-notice {
  border: 1px dashed rgba(196, 77, 52, 0.34);
  background: rgba(255, 248, 241, 0.88);

  strong {
    display: block;
    margin-bottom: 8px;
    color: var(--kp-accent-deep);
  }

  p {
    margin: 0 0 10px;
    color: var(--kp-text-secondary);
    line-height: 1.7;
  }

  code {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(47, 36, 27, 0.06);
  }
}
</style>
