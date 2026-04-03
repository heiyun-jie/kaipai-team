# 00-46 设计说明

## 1. 设计原则

- 一处收口，全页生效
- 保留页级主操作，不做逐页迁移
- 去掉介绍模块后，不额外补新视觉壳层

## 2. 设计策略

### 2.1 PageContainer 收口

`PageContainer` 改为：

- 不再渲染 header copy 区
- 不再渲染 eyebrow / title / description 的介绍卡片
- 当存在 `actions` 插槽时，仅渲染一个轻量 actions 行

### 2.2 兼容性

- 继续保留 `title / eyebrow / description` props，避免影响现有调用
- 页面内容区继续沿用现有 `.page-container__content` 结构

## 3. 影响文件

- `kaipai-admin/src/components/business/PageContainer.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
