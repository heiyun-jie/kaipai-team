# 00-142 当前阶段后台风格模板可视化配置深化（Current Phase Admin Template Visual Configurator Deepening）

> 状态：已完成 | 优先级：最高 | 依赖：00-140 current-phase-admin-shell-ia-and-template-config-alignment、00-141 current-phase-admin-organization-page-runtime-retirement
> 记录目的：在 `00-140` 已完成第一批主题色 / 分享产物可视化配置后，继续按用户指定的 B 步骤，把风格模板编辑深化为更接近小程序页面配置的可视化配置器，并继续生成既有后端 JSON 字段。

## 1. 背景

截至 `2026-04-23`：

- `00-140` 已把 `TemplatesView.vue` 的模板编辑弹窗从直接编辑 `主题 JSON / 分享产物 JSON` 改为：
  - 主题色配置
  - 小程序卡片预览
  - 分享产物表单配置
  - 保存时生成 `baseThemeJson / artifactPresetJson`
- 用户进一步明确：
  - 风格模板应该是配置的，不是用 JSON。
  - 应该模拟小程序页面去配置，然后生成相关 JSON 保存后端。
  - 前端拿 JSON 去映射。

当前判断：

- `00-140` 已完成“不是直接写 JSON”的第一步，但配置模型仍偏颜色表单和产物表单，不足以表达“小程序页面配置”。
- 本轮应继续深化 `TemplatesView.vue`，增加页面结构、模块显隐、行动区、视觉密度等可配置项，并在预览区以小程序页面方式呈现。
- 后端合同继续保持不变，仍写入 `baseThemeJson / artifactPresetJson`。

依据：

- `00-140` 执行记录
- 当前 `TemplatesView.vue` 中 `themeConfig / artifactConfig / buildThemeJson / buildArtifactJson`
- 用户最新目标描述

置信度：

- 中高

不确定边界：

- 小程序前台当前 JSON 映射消费字段可能仍有历史字段，本轮要保留未知 root 字段，避免误删后端已有配置。
- 本轮不实现完整拖拽页面搭建器，只做可验证、可保存、可回放的结构化页面配置深化。

## 2. 范围

### 2.1 本轮必须处理

- 在 `TemplatesView.vue` 的模板编辑弹窗中新增更接近小程序页面的配置能力：
  - 页面布局预设
  - 背景质感 / 视觉密度
  - Hero 区展示方式
  - 小程序页面模块显隐
  - 主要行动区配置
  - 分享卡 / 海报产物配置延续
- 预览区从单张卡片深化为“小程序页面模拟预览”，实时反映配置。
- 保存时继续生成：
  - `baseThemeJson`
  - `artifactPresetJson`
- 生成 JSON 时必须保留原始 JSON root 中未建模字段。
- 通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不改后端模板 DTO / Controller / 数据库字段。
- 不改小程序前台 JSON 映射逻辑。
- 不把 hidden tooling 的 `ThemeTokensView.vue / ShareArtifactsView.vue` 改成同款配置器。
- 不实现拖拽排序与完整页面搭建器。

## 3. 需求

### 3.1 配置交互要求

- **R1** 模板编辑主交互不得回退为直接编辑 JSON textarea。
- **R2** 配置器必须包含小程序页面结构配置，而不只是颜色和产物开关。
- **R3** 配置器必须提供实时小程序页面预览。
- **R4** 预览必须反映主题色、布局、模块显隐和行动区配置。

### 3.2 JSON 生成要求

- **R5** 保存前必须继续生成 `baseThemeJson`。
- **R6** 保存前必须继续生成 `artifactPresetJson`。
- **R7** 生成 JSON 时必须尽量保留原 JSON root 未建模字段。
- **R8** 不得改变 `createTemplate / updateTemplate` 后端调用合同。

### 3.3 验证要求

- **R9** 本轮必须通过 `npm run type-check`。
- **R10** 本轮必须通过 `npm run build`。
- **R11** 执行记录必须写明配置项、JSON 生成策略和验证结果。

## 4. 验收标准

- [x] 模板编辑仍不暴露 JSON textarea 作为主交互
- [x] 已新增小程序页面结构配置
- [x] 已新增更完整的小程序页面模拟预览
- [x] 预览能体现主题、布局、模块和行动区变化
- [x] 保存前生成 `baseThemeJson / artifactPresetJson`
- [x] 未改变后端保存合同
- [x] `type-check / build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
