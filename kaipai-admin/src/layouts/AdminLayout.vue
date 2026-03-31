<template>
  <div class="admin-layout">
    <AdminSidebar />
    <div class="admin-layout__main">
      <AdminTopbar />
      <main class="admin-layout__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AdminSidebar from '@/components/layout/AdminSidebar.vue'
import AdminTopbar from '@/components/layout/AdminTopbar.vue'
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-layout__main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.admin-layout__content {
  flex: 1;
  padding: 0 32px 32px;
}

@media (max-width: 760px) {
  .admin-layout {
    flex-direction: column;
  }

  .admin-layout__content {
    padding: 0 16px 16px;
  }
}
</style>
