# 00-142 设计说明

## 1. 设计目标

`00-142` 只处理 B：深化风格模板可视化配置。

目标是让后台编辑者以“小程序页面配置”的方式维护模板，而不是维护 JSON 文本；保存时继续生成现有后端字段，让后续前台按 JSON 映射。

## 2. 已核实事实

当前 `TemplatesView.vue` 已有第一批能力：

- `themeConfig`
  - primary
  - accent
  - background
  - text
  - heroText
- `artifactConfig`
  - coverImage
  - heroEyebrow
  - focus1 / focus2 / focus3
  - shareCard enabled / ratio
  - poster enabled / ratio
- `buildThemeJson()`
- `buildArtifactJson()`
- `syncVisualConfigToJson()`

当前不足：

- 预览仍是单张卡片，不像小程序页面配置器。
- 配置项还没有覆盖页面结构、模块显隐、行动区和视觉密度。
- `artifactPresetJson` 尚未明确承接页面配置节点。

## 3. 设计策略

### 3.1 增加页面配置状态

新增 `pageConfig`：

- `layoutPreset`
- `surface`
- `density`
- `heroStyle`
- `showProfile`
- `showStats`
- `showTimeline`
- `showContactCta`
- `primaryAction`
- `secondaryAction`

这些配置用于模拟小程序页面结构，并写入 `artifactPresetJson.pageConfig`。

### 3.2 深化小程序预览

把现有预览从单卡改为 phone shell：

- 顶部状态栏
- Hero 区
- 内容聚焦 chips
- 可选档案模块
- 可选统计模块
- 可选时间线模块
- 可选行动区

预览只表达配置映射，不伪造真实业务数据。

### 3.3 JSON 生成策略

继续保留原逻辑：

- `baseThemeJson`
  - 保留原 root 未建模字段
  - 写入主题色配置
- `artifactPresetJson`
  - 保留原 root 未建模字段
  - 写入内容聚焦、分享卡、海报配置
  - 新增 / 覆盖 `pageConfig`

### 3.4 后端合同保持不变

继续调用：

- `createTemplate(...)`
- `updateTemplate(...)`

不改 DTO，不做数据库迁移。

## 4. 风险与边界

### 4.1 已确认

- 本轮不是完整拖拽搭建器。
- 本轮不改小程序前台映射逻辑。
- 本轮不删除 hidden tooling 的 JSON 低层治理能力。

### 4.2 待验证

- 现有模板历史 JSON 中是否已经存在 `pageConfig` 或等价字段。

设计处理：

- hydrate 时读取已有 `pageConfig`
- build 时只覆盖本轮建模字段
- 保留 root 中其它未知字段
