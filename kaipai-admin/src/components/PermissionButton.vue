<template>
  <el-button v-if="visible" v-bind="$attrs" :disabled="denied || disabled">
    <slot />
  </el-button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePermissionStore } from '@/stores/permission'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  actionCode?: string
  hideIfDenied?: boolean
  disabled?: boolean
}>()

const permissionStore = usePermissionStore()
const denied = computed(() => (props.actionCode ? !permissionStore.hasAction(props.actionCode) : false))
const visible = computed(() => !(props.hideIfDenied && denied.value))
</script>
