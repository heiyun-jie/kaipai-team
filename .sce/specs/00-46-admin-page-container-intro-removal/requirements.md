# 00-46 后台页面介绍模块移除（Admin Page Container Intro Removal）

> 状态：进行中 | 优先级：P1 | 依赖：00-10 admin-console
> 记录目的：移除后台所有菜单页顶部统一介绍模块，避免页面首屏被大面积说明区占据。

## 1. 背景

当前后台页面通过 `PageContainer` 统一渲染顶部介绍模块，包含：

- eyebrow
- 标题
- 描述文案

该模块会在所有后台菜单页顶部形成一块大面积说明区，压缩首屏有效操作空间。用户要求：后台所有菜单页统一移除这块介绍模块。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/components/business/PageContainer.vue`

### 2.2 本轮不处理

- 各页面筛选区和表格结构改造
- 侧边菜单和顶栏改造
- 单页额外补标题或面包屑

## 3. 需求

### 3.1 统一移除

- **R1** 后台所有使用 `PageContainer` 的页面，都不再渲染顶部介绍模块。
- **R2** 原有 `title / eyebrow / description` 不再产生可见介绍卡片。

### 3.2 操作保留

- **R3** 若页面使用了 `PageContainer` 的 `actions` 插槽，页级主操作必须继续可见。
- **R4** `actions` 应改为轻量顶栏，不再包裹在介绍模块中。

### 3.3 兼容约束

- **R5** 本轮不得要求逐页修改已有 `PageContainer` 调用。
- **R6** 本轮不得破坏后台页面现有内容区布局与构建通过性。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 所有后台菜单页顶部介绍模块已统一移除
- [ ] 页级 actions 仍可正常显示
- [ ] `npm run build` 在 `kaipai-admin` 通过
