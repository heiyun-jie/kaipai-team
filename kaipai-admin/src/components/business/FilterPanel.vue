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
  border-radius: 26px;
  background:
    linear-gradient(180deg, rgba(255, 252, 247, 0.95), rgba(250, 245, 237, 0.88)),
    rgba(255, 251, 245, 0.9);
  backdrop-filter: blur(14px);
  box-shadow: 0 16px 34px rgba(63, 42, 20, 0.08);
}

:deep(.filter-panel .el-card__body) {
  padding: 24px 24px 22px;
}

.filter-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(80, 63, 47, 0.08);

  h3 {
    margin: 0;
    font-size: 16px;
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

.filter-panel :deep(.el-form--inline) {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 16px;
  align-items: center;
}

.filter-panel :deep(.el-form--inline .el-form-item) {
  display: inline-flex;
  margin: 0;
  align-items: center;
  gap: 12px;
}

.filter-panel :deep(.el-form-item__label) {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  min-height: 44px;
  padding: 0;
  color: var(--kp-text-secondary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1;
}

.filter-panel :deep(.el-form-item__content) {
  display: inline-flex;
  align-items: center;
  min-width: 180px;
  line-height: 1;
}

.filter-panel :deep(.el-input__wrapper),
.filter-panel :deep(.el-select__wrapper),
.filter-panel :deep(.el-textarea__inner),
.filter-panel :deep(.el-date-editor.el-input__wrapper) {
  min-height: 44px;
  align-items: center;
}

.filter-panel :deep(.el-input__inner),
.filter-panel :deep(.el-select__selected-item),
.filter-panel :deep(.el-select__placeholder),
.filter-panel :deep(.el-input__suffix),
.filter-panel :deep(.el-select__caret),
.filter-panel :deep(.el-input__prefix) {
  display: inline-flex;
  align-items: center;
  min-height: 100%;
}

.filter-panel__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: flex-end;
}

.filter-panel__actions :deep(.el-button) {
  min-height: 40px;
  padding-inline: 16px;
  border-radius: 14px;
  font-weight: 700;
}

@media (max-width: 900px) {
  .filter-panel__header {
    display: grid;
  }

  .filter-panel :deep(.el-form--inline .el-form-item) {
    width: 100%;
  }

  .filter-panel :deep(.el-form--inline .el-form-item__content) {
    width: 100%;
    min-width: 0;
  }

  .filter-panel__actions {
    justify-content: flex-start;
  }
}
</style>
