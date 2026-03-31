<template>
  <div class="not-found">
    <div class="not-found__panel">
      <p>404</p>
      <h1>页面不存在</h1>
      <el-button type="primary" @click="router.push('/dashboard')">返回工作台</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped lang="scss">
.not-found {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.not-found__panel {
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
    margin: 10px 0 24px;
  }
}
</style>
