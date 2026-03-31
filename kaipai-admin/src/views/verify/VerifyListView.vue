<template>
  <PendingView v-if="mode === 'pending'" />
  <HistoryView v-else />
</template>

<script setup lang="ts">
import HistoryView from './HistoryView.vue'
import PendingView from './PendingView.vue'

defineProps<{
  mode: 'pending' | 'history'
}>()
</script>
