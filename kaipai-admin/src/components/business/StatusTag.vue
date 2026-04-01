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
  gap: 7px;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.03em;
  border: 1px solid transparent;
  white-space: nowrap;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.status-tag::before {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.82;
}

.status-tag--info {
  background: rgba(47, 36, 27, 0.1);
  color: var(--kp-text-secondary);
  border-color: rgba(47, 36, 27, 0.08);
}

.status-tag--warning {
  background: rgba(196, 122, 40, 0.16);
  color: var(--kp-warning);
  border-color: rgba(196, 122, 40, 0.24);
}

.status-tag--success {
  background: rgba(47, 125, 87, 0.16);
  color: var(--kp-success);
  border-color: rgba(47, 125, 87, 0.24);
}

.status-tag--danger {
  background: rgba(181, 65, 49, 0.16);
  color: var(--kp-danger);
  border-color: rgba(181, 65, 49, 0.22);
}
</style>
