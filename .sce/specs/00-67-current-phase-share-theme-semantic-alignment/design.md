# 00-67 设计说明

## 1. 设计目标

把“编辑页三色配置”从当前的弱语义主题系统，改成用户可理解、公开页可验证、实现上单一事实源的稳定体系。

## 2. 设计原则

- 单一主题事实源
- 三色职责显式化
- 编辑页预览与公开页同构
- 内容配置链与视觉主题链分离

## 3. 目标结构

### 3.1 内容配置链

保持现有链路：

```text
/api/card/personalization.profile.customConfig
  -> buildCardConfigFromPersonalization()
  -> currentCardConfig
  -> getActorSummary()
  -> displayPhotos / displayExperiences / primaryTags
```

该链主要负责：

- `highlightedPhotos`
- `highlightedExperiences`
- `tagOrder`
- `layoutVariant`

### 3.2 主题链

本轮建议优先采用：

```text
/api/card/personalization.theme
  -> pages/actor-profile/detail
  -> pageStyle / headerStyle / section tokens
```

理由：

- 后端已输出完整 `theme`
- 公开页不应再次本地改写同一张卡片主题语义
- 可减少“保存正确、聚合正确、前端又重算错”的再引入问题

## 4. 三色建议语义

### 4.1 backgroundColor

负责：

- 页面底层背景
- hero 外层背景氛围底板

不再被 `primaryColor` 派生色大面积覆盖。

### 4.2 primaryColor

负责：

- hero 主视觉强调区
- 主按钮 / 主要行动入口
- 关键身份信息的主强调元素

### 4.3 accentColor

负责：

- 次级强调元素
- 标签、眉标、统计块、辅助边框或小面积高亮

禁止继续只作为头部渐变终点存在。

## 5. 页面消费建议

### 5.1 公开页

`pages/actor-profile/detail.vue` 调整为：

- `page background` 主用 `background`
- `hero background` 使用 `primary + accent`
- `section chip / eyebrow / small badge` 主用 `accent`
- `surface / surfaceStrong` 仅作为局部卡片层次，不再吞掉背景主语义

### 5.2 编辑页

`pkg-card/actor-card/index.vue` 的预览组件和公开页使用相同 token 规则，避免展示“看起来像这样、实际不是这样”。

## 6. 验证方案

### 6.1 请求验证

- 保存前记录色值
- 保存后对比 `/api/card/config`
- 再对比 `/api/card/personalization`

### 6.2 页面验证

- 编辑页选择一组强对比颜色
- 保存后进入公开页
- 验证三色是否落到预期区域

## 7. 风险

- 若继续保留前端/后端双轨主题生成，后续所有分享产物都将继续出现映射分叉
- 若只修公开页样式，不改主题事实源，问题会在海报、卡片预览、分享路径里重复出现
