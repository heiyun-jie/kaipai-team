# 00-138 当前阶段后台 SearchTableLayout 双版本退场（Current Phase Admin SearchTableLayout Dual Version Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-137 current-phase-admin-business-component-canonical-takeover-retirement-first-pass
> 记录目的：在 `00-137` 已完成 business canonical 接管后的旧组件入口第一批退场后，继续核销 `SearchTableLayout` 双版本是否仍承担运行态职责，并在证据充分时执行双文件退场。

## 1. 背景

截至 `2026-04-23`：

- 当前仓内仍保留两份历史列表壳层：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\SearchTableLayout.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\tables\SearchTableLayout.vue`
- 当前实现前核查已确认：
  1. `kaipai-admin/src` 内未命中任何对 `SearchTableLayout` 的运行时 consumer
  2. `package.json` / `vite.config.ts` 未发现自动注册组件机制
  3. `.sce` 中关于 `SearchTableLayout` 的命中主要来自：
     - `00-137` 当前说明
     - `00-11-platform-admin-console/design.md` 的历史设计组件矩阵
  4. `00-11` 中的 `SearchTableLayout` 只是一条设计级组件命名，不指向当前文件路径，也不构成运行时保留门禁

当前判断：

- 这两份文件属于历史列表壳层残留
- 当前更合理的下一手是单独起一条实现型 spec，专门核销并退场这两个版本

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-138`
- 核销并删除以下两个文件：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\SearchTableLayout.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\tables\SearchTableLayout.vue`
- 删除后通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除其它组件
- 不修改任何业务页 import
- 不调整 business canonical 组件
- 不处理 hidden tooling 路由
- 不处理 fallback 权限兼容链

## 3. 需求

### 3.1 删除门禁

- **R1** 本轮只处理 `SearchTableLayout` 双版本，不扩到其它组件或页面。
- **R2** 删除前必须同时满足：
  - 无源码 import / 动态 import consumer
  - 无自动注册组件机制
  - 文档命中只属于历史设计追溯，不构成运行时保留理由
- **R3** 若 `.sce` 命中指向当前文件路径并明确要求保留，则本轮不得删除。

### 3.2 验证合同

- **R4** 删除前必须记录：
  - 双版本文件职责
  - 源码搜索证据
  - 历史设计引用与运行时依赖的区分
- **R5** 删除后必须通过：
  - `npm run type-check`
  - `npm run build`
- **R6** 若删除后出现类型或构建失败，本轮必须回退删除结论，不得扩大清理范围。

### 3.3 回填要求

- **R7** 本轮必须回填 `README.md`、`spec-code-mapping.md`、`CURRENT_CONTEXT.md`。
- **R8** `execution.md` 必须记录：
  - 删除前核查范围
  - 删除前关键证据
  - 删除动作
  - 删除后验证结果

## 4. 验收标准

- [x] 已新增独立 `00-138`，并把问题收口为 `SearchTableLayout` 双版本退场
- [x] 已记录源码零 consumer 证据与历史设计引用边界
- [x] 两个 `SearchTableLayout` 文件已删除
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
