# 00-88 当前阶段后台系统设置首屏对齐（Current Phase Admin System Settings First Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `operate/actions` 双轮收口完成后，继续把 `system/settings` 的首屏结构与列表密度收口为更接近 reference 的设置列表页表达。

## 1. 背景

截至 `2026-04-22`：

- `system/settings` 已完成正式页回接
- 但尚未进入独立 page-level 精修线

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-88\settings-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-88\settings-before.png`

当前差异：

1. 当前页顶部额外存在一排 `3` 张 overview 卡，而 reference 首屏没有这层摘要
2. 当前三组设置卡都是满宽大卡，首屏纵向占高偏大
3. 当前设置项行高约 `101-102px`，明显高于 reference 的紧凑设置列表表达
4. 当前标题、提示和副文案都偏重，削弱了“设置条目列表”第一语义

同时当前已明确：

- 当前页不能伪造 reference 中的域名、客服邮箱等值
- 当前页只能继续认现有真实事实源与显式“待补事实源”

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-88`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue` 首屏：
  - overview 摘要层
  - `平台信息`
  - `内容审核`
  - `权限管理`
- 用真实浏览器复核 `http://127.0.0.1:5100/system/settings`

### 2.2 本轮不处理

- 不改系统设置背后的真实接口
- 不新增可写配置能力
- 不扩到 `system/admin-users`、`system/roles` 等子页
- 不改其他正式页

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `SettingsView.vue` 首屏结构与设置列表密度。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 对缺失事实源的字段继续明确标记为待补，不得伪造 reference 值。

### 3.2 首屏结构合同

- **R4** 顶部 overview 摘要层不得继续主导首屏；若无必要，应降级或移除。
- **R5** 首屏主语义应回到 `平台信息 / 内容审核 / 权限管理` 三组设置列表。
- **R6** 设置分组卡宽度、标题和说明密度需更接近 reference 的左对齐紧凑列表结构。

### 3.3 列表密度合同

- **R7** 设置项行高、字号和副文案层级需明显收紧，避免当前大卡式占高。
- **R8** 条目值和可跳转语义在收紧后仍需保持清晰、可读和可点击。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-88` 承接，不继续混入 `00-87`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-88` Spec，并明确它只处理 `system/settings` 首屏
- [ ] 已完成 overview 降级 / 移除和三组设置列表的首屏收口
- [ ] 已通过真实浏览器复核 `system/settings`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
