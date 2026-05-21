# 00-143 设计说明

## 1. 设计目标

`00-143` 只处理一个闭环缺口：让后台风格模板编辑器新增的 `pageConfig` 真正进入小程序运行时。

## 2. 已核实事实

### 2.1 后台已能生成 pageConfig

`TemplatesView.vue` 已将以下配置写入 `artifactPresetJson.pageConfig`：

- `layoutPreset`
- `surface`
- `density`
- `heroStyle`
- `sections`
- `actions`

### 2.2 后端 DTO 尚未透出

当前 `ActorSceneTemplateRespDTO` 仍没有 `pageConfig` 字段，`CardSceneTemplateServiceImpl.applyArtifactOverride(...)` 也只解析：

- `coverImage`
- `heroEyebrow`
- `requiredInviteCount`
- `contentFocus`

### 2.3 前端存在布局合同错位

当前后台编辑器用 `layoutPreset` 派生写回 `layoutVariant`，但小程序前端当前布局合同只认：

- `compact`
- `spacious`
- `magazine`

而后台新增预设是：

- `magazine`
- `portfolio`
- `casting`

因此不能把新预设直接当旧布局值裸传。

## 3. 设计策略

### 3.1 后端透出 pageConfig

在 `ActorSceneTemplateRespDTO` 中新增嵌套对象：

- `PageConfig`
- `Sections`
- `Actions`

在 `CardSceneTemplateServiceImpl` 中：

- 继续保留当前 `coverImage / heroEyebrow / contentFocus` 解析
- 新增 `pageConfig` 解析
- 若缺失 `pageConfig`，则按当前默认模板生成一套默认值

### 3.2 layoutVariant 兼容归一

在后端组装 DTO 时，对模板持久化字段 `layoutVariant` 做兼容归一：

- `magazine` -> `magazine`
- `portfolio` -> `spacious`
- `casting` -> `compact`
- 旧值 `compact / spacious / magazine` 保持原样

这样前端现有 `card-page--layout-* / actor-detail-page--layout-*` 仍有承接。

### 3.3 前端 pageConfig 消费

前端补一个独立 helper：

- 归一 `pageConfig`
- 提供缺省值
- 提供 `layoutPreset -> runtimeLayoutVariant` 映射

运行时映射策略：

- `pkg-card/actor-card/index`
  - 根据 `surface / density / heroStyle / layoutPreset` 附加样式 class
  - 让分享页预览外壳、节奏和 Hero 结构产生真实差异
- `pages/actor-profile/detail`
  - 根据 `sections.profile / stats / timeline / contactCta` 控制可见模块
  - 根据 `surface / density / heroStyle / layoutPreset` 附加样式 class

## 4. 风险与边界

### 4.1 已确认

- 本轮不修改后台配置器形态。
- 本轮不做模块拖拽排序。
- 本轮优先保证公开页 / 分享页主链可见差异。

### 4.2 待验证

- `build:mp-weixin` 后 `dist/dev` 与 `dist/build` 是否都能看到目标类名和值。

验证方法：

- `npm run build:mp-weixin`
- 检查生成的 WXML / WXSS / JS
- 必要时再做运行态截图验证
