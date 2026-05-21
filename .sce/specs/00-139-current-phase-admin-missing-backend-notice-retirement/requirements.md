# 00-139 当前阶段后台 MissingBackendNotice 退场（Current Phase Admin Missing Backend Notice Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-138 current-phase-admin-search-table-layout-dual-version-retirement
> 记录目的：在 `00-138` 已完成 `SearchTableLayout` 双版本退场后，继续核销 `src/components/business/MissingBackendNotice.vue` 是否仍承担运行态职责，并在证据充分时执行单文件退场。

## 1. 背景

截至 `2026-04-23`：

- 当前仓内仍保留：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\business\MissingBackendNotice.vue`
- 当前实现前核查已确认：
  1. `kaipai-admin/src` 内未命中任何 `MissingBackendNotice` consumer
  2. `.sce / docs` 内未命中任何 `MissingBackendNotice` 或当前文件路径追溯引用
  3. 该组件本身只是一张提示卡：
     - `title`
     - `description`
     - `endpointHint`

当前判断：

- `MissingBackendNotice.vue` 是未被消费的独立提示组件
- 当前更合理的下一手是单独起一条实现型 spec，核销并退场这张单文件组件

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-139`
- 核销并删除：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\business\MissingBackendNotice.vue`
- 删除后通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除其它 business 组件
- 不修改任何页面 import
- 不处理 hidden tooling 路由
- 不处理 fallback 权限兼容链

## 3. 需求

### 3.1 删除门禁

- **R1** 本轮只处理 `MissingBackendNotice.vue`，不扩展到其它组件。
- **R2** 删除前必须同时满足：
  - 无源码 import / 动态 import consumer
  - 无 `.sce / docs` 追溯引用
  - 当前文件不承担 router / menu / fallback 相关职责
- **R3** 若删除后发现其承担过真实降级提示职责，本轮必须回退结论。

### 3.2 验证合同

- **R4** 删除前必须记录：
  - 文件职责
  - 源码搜索证据
  - 文档搜索证据
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

- [x] 已新增独立 `00-139`，并把问题收口为 `MissingBackendNotice.vue` 的单文件退场
- [x] 已记录源码零 consumer 与文档零引用证据
- [x] `MissingBackendNotice.vue` 已删除
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
