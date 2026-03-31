<template>
  <BusinessFilterPanel v-bind="$props">
    <template v-if="$slots.actions" #actions>
      <slot name="actions" />
    </template>
    <slot />
  </BusinessFilterPanel>
</template>

<script setup lang="ts">
import BusinessFilterPanel from '@/components/business/FilterPanel.vue'
</script>
