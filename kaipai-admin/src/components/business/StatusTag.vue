<template>
  <span class="status-tag" :class="`status-tag--${tone}`">{{ label }}</span>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  tone: 'info' | 'warning' | 'success' | 'danger'
}>()
</script>

<style scoped lang="scss">
.status-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid transparent;
}

.status-tag--info {
  background: rgba(47, 36, 27, 0.08);
  color: var(--kp-text-secondary);
}

.status-tag--warning {
  background: rgba(196, 122, 40, 0.14);
  color: var(--kp-warning);
  border-color: rgba(196, 122, 40, 0.2);
}

.status-tag--success {
  background: rgba(47, 125, 87, 0.14);
  color: var(--kp-success);
  border-color: rgba(47, 125, 87, 0.2);
}

.status-tag--danger {
  background: rgba(181, 65, 49, 0.14);
  color: var(--kp-danger);
  border-color: rgba(181, 65, 49, 0.18);
}
</style>
