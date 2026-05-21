# 00-64 设计说明

## 1. 设计原则

- 先收口编辑页职责，再补具体能力
- 只保留服务当前 MVP 的编辑链，不继续兼容旧分享叙事
- 预览闭环必须指向真实公开页，而不是局部临时预览态
- 编辑页负责卡片配置，不抢档案页职责

## 2. 当前问题拆解

### 2.1 页面边界错位

`pkg-card/actor-card/index` 当前同时承担了：

- 单卡编辑
- 单卡分享
- 旧会员能力展示
- 旧命理主题能力展示
- 旧受众视角切换

这导致页面既像“编辑器”，又像“能力中心”，又像“旧分享面板”，边界已经混乱。

### 2.2 编辑能力缺口

当前后端 `ActorCardConfigSaveDTO` 已具备：

- `highlightedPhotos`
- `highlightedExperiences`
- `primaryColor`
- `accentColor`
- `backgroundColor`
- `layoutVariant`

但前端页面还缺：

- 代表照片选择器
- 高亮经历选择器
- 统一可理解的“保存后会影响公开名片”的操作反馈

### 2.3 生效链不清晰

虽然 `00-63` 已把公开页与编辑页的 latest-state 读取收口为共享 loader，但编辑页里仍残留：

- preview overlay
- 旧 capability gating
- 旧能力说明文案

因此用户会继续感觉“这里改了，但真实公开名片到底按哪套逻辑生效”不清楚。

## 3. 页面重构策略

### 3.1 新页面职责

`pkg-card/actor-card/index` 只保留 4 个区块：

1. 当前卡片基础信息
   - 风格名
   - 当前卡片摘要
   - 当前卡片基础视觉预览
2. 内容配置区
   - 代表照片选择
   - 高亮经历选择
3. 视觉配置区
   - 布局
   - 主配色 / 强调色 / 背景色
4. 底部动作区
   - 保存配置
   - 预览公开名片

### 3.2 明确移除项

以下内容不再属于当前编辑页：

- `KpCapabilityMatrixCard`
- 会员升级引导
- 命理驱动主题能力项
- 幸运色入口 `goFortunePage`
- audience selector

### 3.3 代表照片编辑

编辑模式：

- 数据源来自当前演员档案的全部照片分类
- 用户可选择 0~N 张，但公开页展示遵循当前主线规则，只取前若干张
- 选择结果保存到 `highlightedPhotos`

公开页消费：

- 若存在 `highlightedPhotos`，优先按其渲染
- 否则回退到默认照片推导逻辑

### 3.4 高亮经历编辑

编辑模式：

- 数据源来自当前演员档案 `workExperiences`
- 用户可勾选当前卡片想突出的经历
- 保存到 `highlightedExperiences`

公开页消费：

- 若存在 `highlightedExperiences`，优先按其渲染
- 否则回退到按场景推导的默认逻辑

### 3.5 视觉配置

编辑模式：

- 布局、主配色、强调色、背景色统一放在“视觉配置区”
- 当前阶段默认按卡片配置直接保存
- 不再继续用“会员是否可编辑”当页面级门禁

公开页消费：

- `pages/actor-profile/detail` 继续通过 `00-63` 已建立的 latest snapshot loader 获取最新 `cardConfig`
- 公开页主题、布局样式直接使用最新 `cardConfig`

### 3.6 预览公开名片

新增按钮：

- 文案：`预览公开名片`
- 路由：`/pages/actor-profile/detail?shared=1&shareCardId={shareCardId}`

目标：

- 让用户编辑后直接验证真实公开页，而不是停留在编辑页内自我解释

## 4. 非目标

以下问题明确不在本 Spec 中解决：

- 同一模板是否允许创建多张卡
- “新增分享卡片”是否生成全新实例
- `createCard()` 是否从 `ensureOwnedCard()` 改为全新 insert

这些都属于多实例模型重构，应由独立 Spec 处理。

## 5. 影响文件

- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- `kaipai-frontend/src/pages/actor-profile/detail.vue`
- `kaipai-frontend/src/utils/share-card-latest.ts`
- `kaipai-frontend/src/utils/actor-card.ts`
- 可能新增：
  - `kaipai-frontend/src/pkg-card/actor-card/components/*`

## 6. 验证思路

### 6.1 页面验证

- 编辑页不再出现会员 / 命理 / 受众视角噪音模块
- 编辑页新增“预览公开名片”按钮
- 代表照片与高亮经历具备可选交互

### 6.2 生效验证

- 保存配色后，公开页实时生效
- 保存代表照片后，公开页展示对应照片
- 保存高亮经历后，公开页展示对应经历

### 6.3 边界验证

- 编辑档案页仍只维护通用资料
- 编辑卡片页只维护当前卡片展示配置
- 多实例问题不在本轮内被偷偷混入实现
