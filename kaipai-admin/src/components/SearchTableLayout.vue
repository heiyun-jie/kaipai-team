<template>
  <div class="search-table-layout">
    <div v-if="$slots.filters" class="search-table-layout__filters">
      <slot name="filters" />
      <div v-if="$slots.actions" class="search-table-layout__actions">
        <slot name="actions" />
      </div>
    </div>
    <el-card class="search-table-layout__card" shadow="never" v-loading="loading">
      <slot />
      <div class="search-table-layout__pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :current-page="pageNo"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="emit('update:pageNo', $event)"
          @size-change="emit('update:pageSize', $event)"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading?: boolean
  total: number
  pageNo: number
  pageSize: number
}>()

const emit = defineEmits<{
  'update:pageNo': [value: number]
  'update:pageSize': [value: number]
}>()
</script>

<style scoped lang="scss">
.search-table-layout {
  display: grid;
  gap: 16px;
}

.search-table-layout__filters {
  display: grid;
  gap: 12px;
}

.search-table-layout__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.search-table-layout__card {
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
}

.search-table-layout__pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
