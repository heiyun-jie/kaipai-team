# 00-143 当前阶段模板页面配置运行时对齐（Current Phase Template Page Config Runtime Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-142 current-phase-admin-template-visual-configurator-deepening、00-27 mini-program-frontend-architecture、00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `00-142` 已让后台模板编辑器生成 `artifactPresetJson.pageConfig` 后，继续把该页面配置透出到运行时 DTO，并让小程序公开页 / 分享页真实消费配置，不再停留在“后台可配但前台不映射”的半闭环状态。

## 1. 背景

截至 `2026-04-24`：

- 后台 `TemplatesView.vue` 已支持生成：
  - `baseThemeJson`
  - `artifactPresetJson`
  - `artifactPresetJson.pageConfig`
- `pageConfig` 当前包含：
  - `layoutPreset`
  - `surface`
  - `density`
  - `heroStyle`
  - `sections`
  - `actions`
- 当前小程序端 `SceneTemplate` 仍只承接：
  - `coverImage`
  - `heroEyebrow`
  - `themeColors`
  - `layoutVariant`
  - `contentFocus`
- 当前后端 `ActorSceneTemplateRespDTO` 也还没有 `pageConfig` 字段。

当前判断：

- 只完成后台配置器还不够，当前链路没有形成“配置 -> 返回 DTO -> 前端映射”的真实闭环。
- 另外，后台配置器当前把 `layoutPreset` 写回 `layoutVariant`，而小程序前端现有运行时布局合同仍只认 `compact / spacious / magazine`；直接把 `portfolio / casting` 暴露给现有页面会产生未定义样式承接。
- 因此本轮必须同时处理：
  1. 后端把 `pageConfig` 透出给前端
  2. 前端消费 `pageConfig`
  3. `layoutVariant` 做兼容映射，不让现有运行时掉到未知布局值

依据：

- `kaipai-admin/src/views/content/TemplatesView.vue`
- `kaipaile-server/.../ActorSceneTemplateRespDTO.java`
- `kaipaile-server/.../CardSceneTemplateServiceImpl.java`
- `kaipai-frontend/src/types/level.ts`
- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- `kaipai-frontend/src/pages/actor-profile/detail.vue`

置信度：

- 高

不确定边界：

- 本轮不做完整页面搭建器，也不做拖拽模块排序。
- 本轮优先让公开页 / 分享页看到 `pageConfig` 的真实差异，不扩展到所有小程序页面。

## 2. 范围

### 2.1 本轮必须处理

- 后端 `ActorSceneTemplateRespDTO` 补齐 `pageConfig` 合同。
- 后端模板装配逻辑从 `artifactPresetJson` 解析 `pageConfig`。
- 后端对 `layoutVariant` 做兼容归一，不把 `portfolio / casting` 直接裸传给仍只认旧布局值的前端运行时。
- 前端 `SceneTemplate` 补齐 `pageConfig` 类型。
- 小程序端新增 `pageConfig` 解析 / 归一工具。
- 小程序端至少在以下页面消费 `pageConfig`：
  - `pkg-card/actor-card/index`
  - `pages/actor-profile/detail`
- 映射至少覆盖：
  - 背景质感
  - 视觉密度
  - Hero 风格
  - 页面模块显隐
  - 布局预设兼容承接
- 通过：
  - `kaipaile-server` 编译验证
  - `kaipai-frontend` `npm run type-check`
  - `kaipai-frontend` `npm run build:mp-weixin`
- 按 `mp-ui-change-verification` 要求检查：
  - `src`
  - `dist/build/mp-weixin`
  - `dist/dev/mp-weixin`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不改后台模板编辑器 UI 结构。
- 不改拖拽排序、模块顺序编排。
- 不改 `ThemeTokensView.vue / ShareArtifactsView.vue` 的底层治理模式。
- 不做新的数据库字段迁移。
- 不扩展到所有小程序页面，只先闭环公开页 / 分享页主链。

## 3. 需求

### 3.1 DTO 与合同要求

- **R1** 后端 `ActorSceneTemplateRespDTO` 必须补齐 `pageConfig` 返回字段。
- **R2** 后端必须从 `artifactPresetJson.pageConfig` 解析 DTO，不得要求前端自行解析原始 JSON 文本。
- **R3** `layoutVariant` 必须继续对现有前端布局合同兼容。

### 3.2 小程序运行时要求

- **R4** 小程序 `SceneTemplate` 必须能读取 `pageConfig`。
- **R5** `pkg-card/actor-card/index` 必须对 `pageConfig` 产生可见运行时差异。
- **R6** `pages/actor-profile/detail` 必须对 `pageConfig.sections` 产生真实模块显隐差异。
- **R7** 前端不得因为 `portfolio / casting` 等新预设导致未知布局 class 漏出为无承接状态。

### 3.3 验证要求

- **R8** 本轮必须通过后端编译验证。
- **R9** 本轮必须通过 `kaipai-frontend` `npm run type-check`。
- **R10** 本轮必须通过 `kaipai-frontend` `npm run build:mp-weixin`。
- **R11** 必须检查 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 已出现目标类 / 结构 / 值。

## 4. 验收标准

- [ ] 后端 DTO 已补齐 `pageConfig`
- [ ] 后端已从 `artifactPresetJson` 解析 `pageConfig`
- [ ] `layoutVariant` 兼容映射已生效
- [ ] 前端 `SceneTemplate` 已补齐 `pageConfig` 类型
- [ ] 分享页已消费 `pageConfig`
- [ ] 公开页已消费 `pageConfig.sections`
- [ ] `type-check / build:mp-weixin / 后端编译` 通过
- [ ] 已核查 `src / dist/build / dist/dev`
- [ ] README / mapping / CURRENT_CONTEXT / execution 已回填
