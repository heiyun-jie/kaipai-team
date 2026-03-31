<template>
  <section class="page-container">
    <header class="page-container__header">
      <div>
        <p v-if="eyebrow" class="page-container__eyebrow">{{ eyebrow }}</p>
        <h1>{{ title }}</h1>
        <p v-if="description" class="page-container__description">{{ description }}</p>
      </div>
      <div v-if="$slots.extra" class="page-container__extra">
        <slot name="extra" />
      </div>
    </header>
    <div class="page-container__body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  eyebrow?: string
  description?: string
}>()
</script>

<style scoped lang="scss">
.page-container {
  display: grid;
  gap: 18px;
}

.page-container__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.page-container__eyebrow {
  margin: 0 0 8px;
  color: var(--kp-accent);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.page-container__description {
  margin: 8px 0 0;
  color: var(--kp-text-secondary);
}

.page-container__body {
  display: grid;
  gap: 16px;
}
</style>
