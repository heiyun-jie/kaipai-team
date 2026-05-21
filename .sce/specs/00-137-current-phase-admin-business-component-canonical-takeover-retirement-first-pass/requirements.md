# 00-137 当前阶段后台业务组件 canonical 接管后旧组件退场第一批（Current Phase Admin Business Component Canonical Takeover Retirement First Pass）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-136 current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement
> 记录目的：在 `00-136` 已完成单个 compat wrapper 退场后，继续核销已被 `components/business/*` 完全接管且当前源码无 consumer 的旧组件入口，并在证据充分时执行第一批退场。

## 1. 背景

截至 `2026-04-23`：

- 当前后台运行页已经普遍使用：
  - `@/components/business/PageContainer.vue`
  - `@/components/business/FilterPanel.vue`
  - `@/components/business/PermissionButton.vue`
  - `@/components/business/StatusTag.vue`
- 当前仓内仍保留若干旧组件入口：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\PageContainer.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\PermissionButton.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\StatusTag.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\layout\PageContainer.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\layout\FilterPanel.vue`

本轮实现前核查已确认：

1. 当前 `kaipai-admin/src` 内未发现任何运行时代码继续 import 上述旧入口
2. 当前 `.sce / docs` 未发现上述旧入口的路径追溯引用
3. 当前所有运行态页面已经统一从 `components/business` 目录消费对应组件
4. `components/layout/FilterPanel.vue` 只是 `components/business/FilterPanel.vue` 的兼容转发壳层

当前判断：

- 这批文件属于已被 business canonical 组件接管后的旧入口
- 当前可以作为第一批小范围退场对象

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-137`
- 核销并删除以下旧组件入口：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\PageContainer.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\PermissionButton.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\StatusTag.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\layout\PageContainer.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\layout\FilterPanel.vue`
- 删除后通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除 `D:\XM\kaipai-team\kaipai-admin\src\components\business\*`
- 不删除 `SearchTableLayout` 两个版本：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\SearchTableLayout.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\components\tables\SearchTableLayout.vue`
- 不修改任何业务页 import
- 不处理 hidden tooling 路由
- 不处理 fallback 权限兼容链

## 3. 需求

### 3.1 删除门禁

- **R1** 本轮只处理已被 `components/business/*` 明确接管的旧组件入口。
- **R2** 删除前必须同时满足：
  - 无源码 import / 动态 import consumer
  - 无 `.sce / docs` 路径追溯引用
  - 当前已有 business canonical 组件继续承担运行职责
- **R3** `SearchTableLayout` 虽然当前也未发现 consumer，但本轮不得处理，因为它不属于本轮“business canonical 接管”证据链。

### 3.2 验证合同

- **R4** 删除前必须记录：
  - 旧入口清单
  - business canonical consumer 证据
  - 搜索证据
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

- [x] 已新增独立 `00-137`，并把问题收口为 business canonical 接管后的旧组件入口第一批退场
- [x] 已记录旧入口无 consumer 证据与 business canonical 接管证据
- [x] 5 个旧组件入口已删除
- [x] `SearchTableLayout` 两个版本未被本轮处理
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
