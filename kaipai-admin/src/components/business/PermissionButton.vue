<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import { usePermissionStore } from '@/stores/permission'

const props = withDefaults(
  defineProps<{
    action?: string
    actionCode?: string
    mode?: 'hide' | 'disable'
    hideIfDenied?: boolean
  }>(),
  {
    mode: 'disable',
    hideIfDenied: false,
  },
)

const attrs = useAttrs()
const permissionStore = usePermissionStore()
const action = computed(() => props.action || props.actionCode)
const renderMode = computed(() => (props.hideIfDenied ? 'hide' : props.mode))
const allowed = computed(() => (action.value ? permissionStore.hasAction(action.value) : true))
const shouldRender = computed(() => allowed.value || renderMode.value !== 'hide')
</script>

<template>
  <el-button v-if="shouldRender" v-bind="attrs" :disabled="!allowed || Boolean(attrs.disabled)">
    <slot />
  </el-button>
</template>

