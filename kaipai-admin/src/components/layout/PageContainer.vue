<template>
  <section class="page-container">
    <header class="page-container__header">
      <div>
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
  gap: 20px;
}

.page-container__header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;

  h1 {
    margin: 6px 0 8px;
    font-size: 34px;
    line-height: 1.1;
  }
}

.page-container__eyebrow {
  margin: 0;
  letter-spacing: 0.24em;
  font-size: 12px;
  color: var(--kp-accent);
}

.page-container__description {
  margin: 0;
  max-width: 720px;
  color: var(--kp-text-secondary);
}

.page-container__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.page-container__content {
  display: grid;
  gap: 16px;
}
</style>
