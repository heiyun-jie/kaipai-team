# 00-47 后台 PageContainer 死参清理（Admin Page Container Intro Prop Cleanup）

> 状态：已完成 | 优先级：P1 | 依赖：00-46 admin-page-container-intro-removal
> 记录目的：在统一移除后台菜单页介绍模块后，清理仍残留在各页面调用点上的 `title / eyebrow / description` 死参，避免无效属性继续泄漏到 DOM。

## 1. 背景

`00-46` 已将 `PageContainer` 顶部介绍模块从共享组件中移除，后台页面不再显示统一介绍区。

但当前多个页面仍继续向 `PageContainer` 传入：

- `title`
- `eyebrow`
- `description`

这些字段已经不再被共享组件消费；在 Vue 默认 attribute 透传下，它们会变成根节点上的无效 DOM 属性，其中 `title` 还可能生成浏览器 tooltip，属于残留实现噪音。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/components/business/PageContainer.vue`
- 所有仍向 `PageContainer` 传递 `title / eyebrow / description` 的后台视图
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`

### 2.2 本轮不处理

- `FilterPanel`、`el-dialog`、`el-drawer` 等其他组件的 `title / description` 合法属性
- 后台页面正文文案、筛选区或卡片结构重构
- 新增替代性的页头组件或面包屑体系

## 3. 需求

### 3.1 死参清除

- **R1** 所有后台页面对 `PageContainer` 的 `title / eyebrow / description` 传参必须清理干净。
- **R2** 不得误删页面内其他组件的合法 `title / description` 属性。

### 3.2 结构兼容

- **R3** 清理死参后，页面原有内容、`actions` 插槽、筛选区和表格结构必须保持不变。
- **R4** 若某页面此前仅为 `PageContainer` 准备标题相关脚本变量、`computed` 或路由取值，本轮必须同步移除未使用代码。

### 3.3 治理回填

- **R5** 必须新增独立 Spec 记录本轮“死参清理”工作，而不是继续挤入 `00-46`。
- **R6** 必须完成代码映射、任务记录和执行验证闭环。

## 4. 验收标准

- [x] 已新增独立 `00-47` Spec 并登记索引与代码映射
- [x] `kaipai-admin` 中所有 `PageContainer` 调用点不再传 `title / eyebrow / description`
- [x] 未误删其他组件合法属性，页面结构保持稳定
- [x] `npm run build` 在 `kaipai-admin` 通过
