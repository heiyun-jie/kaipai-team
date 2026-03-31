<template>
  <PageContainer :title="title" description="菜单、路由和权限入口已建立，本页等对应业务域接口或字段矩阵稳定后再继续实现。">
    <el-card class="placeholder-card" shadow="never">
      <h3>页面壳层已就位</h3>
      <p>当前路由：{{ route.path }}</p>
      <p>当前页面权限：{{ String(route.meta.pagePermission || '--') }}</p>
    </el-card>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PageContainer from '@/components/business/PageContainer.vue'

const route = useRoute()
const title = computed(() => String(route.meta.title || '页面开发中'))
</script>

<style scoped lang="scss">
.placeholder-card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}
</style>
