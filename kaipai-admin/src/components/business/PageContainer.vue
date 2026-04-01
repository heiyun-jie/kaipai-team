<template>
  <section class="page-container">
    <header class="page-container__header">
      <div class="page-container__copy">
        <p class="page-container__eyebrow">{{ eyebrow }}</p>
        <h1>{{ title }}</h1>
        <p v-if="description" class="page-container__description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="page-container__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="page-container__content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    eyebrow?: string
    description?: string
  }>(),
  {
    eyebrow: 'PLATFORM ADMIN',
    description: '',
  },
)
</script>

<style scoped lang="scss">
.page-container {
  display: grid;
  gap: 24px;
  width: min(100%, var(--kp-layout-max));
  margin: 0 auto;
}

.page-container__header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  padding: 26px 30px;
  border: 1px solid rgba(196, 77, 52, 0.12);
  border-radius: 30px;
  background:
    radial-gradient(circle at top right, rgba(196, 77, 52, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(255, 251, 246, 0.98), rgba(249, 241, 232, 0.9));
  box-shadow: var(--kp-shadow);

  h1 {
    margin: 6px 0 8px;
    font-size: clamp(32px, 3vw, 38px);
    line-height: 1.1;
  }
}

.page-container__copy {
  display: grid;
  gap: 2px;
  max-width: 820px;
}

.page-container__eyebrow {
  margin: 0;
  letter-spacing: 0.24em;
  font-size: 12px;
  font-weight: 700;
  color: var(--kp-accent-deep);
}

.page-container__description {
  margin: 0;
  max-width: 720px;
  color: var(--kp-text-secondary);
  font-size: 15px;
  line-height: 1.75;
}

.page-container__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-self: stretch;
  align-items: flex-end;
}

.page-container__actions :deep(.el-button) {
  min-height: 42px;
  padding-inline: 18px;
  border-radius: 14px;
  font-weight: 700;
}

.page-container__content {
  display: grid;
  gap: 16px;
}

@media (max-width: 900px) {
  .page-container__header {
    display: grid;
    padding: 22px 20px;
  }

  .page-container__actions {
    justify-content: flex-start;
  }
}
</style>
