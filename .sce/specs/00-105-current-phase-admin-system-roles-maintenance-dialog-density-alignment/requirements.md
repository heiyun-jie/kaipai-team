# 00-105 当前阶段后台角色治理维护弹窗密度对齐（Current Phase Admin System Roles Maintenance Dialog Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-104 current-phase-admin-system-roles-detail-drawer-density-alignment
> 记录目的：在 `00-104` 完成 `system/roles` 详情抽屉收口后，继续把 `新建角色 / 编辑角色 / 复制角色` 三个维护弹窗的壳层、intro、表单项、权限包与权限树编辑区密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 到 `00-104` 已连续收口 `system/roles` 的首屏、矩阵、角色清单和详情抽屉
- 当前剩余高感知 UI 已收窄到维护弹窗

真实运行态截图已确认：

- 新建角色：`D:\XM\kaipai-team\output\playwright\00-105\roles-create-before.png`
- 编辑角色：`D:\XM\kaipai-team\output\playwright\00-105\roles-edit-before.png`
- 复制角色：`D:\XM\kaipai-team\output\playwright\00-105\roles-copy-before.png`

当前差异：

1. 新建角色弹窗约 `860 × 2008`
2. 编辑角色弹窗约 `860 × 2236`
3. 复制角色弹窗约 `560 × 674`
4. 三个弹窗的 `dialog-intro` 都约 `117px`
5. 创建 / 编辑弹窗的权限编排区过高：
   - 新建 `权限编排` form item 约 `1316px`
   - 编辑 `权限编排` form item 约 `1544px`
6. 权限包卡片约 `326 / 332px`
7. 状态确认弹窗已确认也偏厚，但应单独切片，不与本轮混合

### 当前量化

- 新建角色弹窗：`860 × 2008`
  - header：`67px`
  - body：`1832px`
  - footer：`75px`
  - intro：`117px`
  - 5 个表单项：`78 / 78 / 78 / 105 / 1316`
  - 权限包卡片：`326 / 326 / 332 / 332`
- 编辑角色弹窗：`860 × 2236`
  - header：`67px`
  - body：`2060px`
  - footer：`75px`
  - intro：`117px`
  - 5 个表单项：`78 / 78 / 78 / 105 / 1544`
  - 权限包卡片：`326 / 326 / 332 / 332`
- 复制角色弹窗：`560 × 674`
  - header：`67px`
  - body：`498px`
  - footer：`75px`
  - intro：`117px`
  - 3 个表单项：`78 / 78 / 105`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-105`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 中：
  - `新建角色`
  - `编辑角色`
  - `复制角色`
- 处理内容仅限：
  - dialog shell
  - `dialog-intro`
  - 表单项节奏
  - 权限包卡片
  - 权限树编辑区
  - dialog body 滚动策略
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改首屏与三张主卡
- 不改角色清单表格
- 不改详情抽屉
- 不改启用 / 禁用确认弹窗
- 不改角色模型、权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 的维护弹窗，不扩到状态确认弹窗和其它页面。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 维护弹窗密度合同

- **R4** 创建 / 编辑弹窗必须不再维持当前超过 2000px 的整体高度观感，应改为有限高度 dialog + body 内滚动。
- **R5** dialog header、footer、close button 与 `dialog-intro` 必须明显收紧。
- **R6** 通用表单项高度必须下降。
- **R7** 权限包卡片与权限树编辑区必须更紧，避免其继续主导整体高度。
- **R8** 权限包 tag 可在维护弹窗内使用紧凑文案，但必须保留完整权限语义可追溯。
- **R9** 复制角色弹窗必须同步收紧，但无需承接权限树滚动策略。

### 3.3 治理要求

- **R10** 本轮必须保持创建 / 编辑 / 复制动作语义、表单字段与接口调用不变。
- **R11** 本轮必须通过独立 `00-105` 承接，不继续混入 `00-104`。
- **R12** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R13** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-105` Spec，并明确它只处理 `system/roles` 维护弹窗密度
- [ ] 已完成新建 / 编辑 / 复制三个弹窗的 shell、intro、表单项、权限包与权限树区域收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
