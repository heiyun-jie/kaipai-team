<template>
  <el-card class="filter-panel" shadow="never">
    <div class="filter-panel__header">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      <div class="filter-panel__actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="filter-panel__body">
      <slot />
    </div>
  </el-card>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    description?: string
  }>(),
  {
    title: '筛选条件',
    description: '',
  },
)
</script>

<style scoped lang="scss">
.filter-panel {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
  backdrop-filter: blur(14px);
}

.filter-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    font-size: 15px;
  }

  p {
    margin: 6px 0 0;
    color: var(--kp-text-secondary);
    font-size: 13px;
  }
}

.filter-panel__body {
  display: grid;
  gap: 16px;
}

.filter-panel__actions {
  display: flex;
  gap: 10px;
}
</style>
