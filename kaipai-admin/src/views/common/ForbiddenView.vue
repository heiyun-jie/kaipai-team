<template>
  <div class="forbidden-page">
    <div class="forbidden-card">
      <p>403</p>
      <h1>当前账号没有访问权限</h1>
      <span>请确认是否分配了对应 `page.*` 权限。</span>
      <el-button type="primary" @click="router.push('/dashboard/index')">返回工作台</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<style scoped lang="scss">
.forbidden-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.forbidden-card {
  display: grid;
  gap: 12px;
  padding: 40px;
  border-radius: 28px;
  border: 1px solid var(--kp-border);
  background: var(--kp-surface);
  text-align: center;

  p {
    margin: 0;
    color: var(--kp-accent);
    font-size: 14px;
    letter-spacing: 0.3em;
  }

  h1 {
    margin: 0;
  }

  span {
    color: var(--kp-text-secondary);
  }
}
</style>
