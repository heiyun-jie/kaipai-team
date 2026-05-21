# 00-94 当前阶段后台系统设置分组行细节对齐（Current Phase Admin System Settings Grouped Row Detail Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-88 current-phase-admin-system-settings-first-screen-alignment
> 记录目的：在 `00-88` 完成 `system/settings` 首屏收口后，继续把 `系统设置` 页的 grouped rows / 子入口细节收口为更接近 reference 的分组行表达。

## 1. 背景

截至 `2026-04-22`：

- `SettingsView.vue` 已完成首屏结构收口
- 但整页对比后仍保留明显的 grouped-row 细节差异

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-94\settings-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-94\settings-current.png`

当前差异：

1. reference 是更干净的 grouped rows 表达
2. 当前运行态每组卡的 header hint 仍偏重
3. 当前行级副文案、占高和尾部动作感仍比 reference 更厚
4. 当前部分 value 文案过长，例如“未纳入后台正式事实源”，影响 grouped row 的紧凑感

同时当前已明确：

- 不能伪造 reference 中的 `juming.app / help@juming.app / 3 人 / 12 人 / 8 人`
- 隐藏治理工具入口在依赖未核实前不能删除
- 本轮只能重组现有真实入口与现有事实源

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-94`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue`：
  - grouped cards 的 header 密度
  - grouped rows 的行高、层级与尾部 affordance
  - 子入口细节文案收口
- 用真实浏览器复核 `http://127.0.0.1:5100/system/settings`

### 2.2 本轮不处理

- 不改真实接口
- 不改路由职责
- 不删除隐藏治理工具页
- 不伪造 reference 中无事实源支撑的域名、邮箱和岗位人数

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `SettingsView.vue` 的 grouped-row 细节，不重开首屏结构问题。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮继续遵守系统设置页事实边界：不伪造 reference 中无事实源支撑的配置值。

### 3.2 grouped-row 合同

- **R4** grouped cards 的 header hint 必须明显收紧，不再占据过多垂直空间。
- **R5** grouped rows 必须更接近 reference 的紧凑行表达，行高与副文案占高继续下降。
- **R6** 每个子入口行都应具有更接近 reference 的右侧 affordance，不再只像纯文本列表。

### 3.3 子入口文案合同

- **R7** 占位 value 文案必须收口为更短、更稳定的事实边界表达。
- **R8** 隐藏工具入口与正式入口的副文案必须保留真实边界，但用更轻量的行级 copy 表达。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-94` 承接，不继续混入 `00-88`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-94` Spec，并明确它只处理 `system/settings` grouped rows / 子入口细节
- [ ] 已完成 grouped cards header、row 高度、右侧 affordance 与子入口文案收口
- [ ] 已通过真实浏览器复核 `system/settings`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
