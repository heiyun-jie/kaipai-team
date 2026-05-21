# 00-88 设计说明

## 1. 设计目标

`00-88` 只解决 `system/settings` 首屏：

1. **remove summary noise**：移除当前多余的 overview 摘要层
2. **compact settings cards**：把三组设置卡收成 reference 风格的窄宽度、紧凑列表
3. **preserve fact boundary**：继续只认真实事实源与待补标记

## 2. 已核实的事实

### 2.1 当前问题集中在首屏结构和条目密度

真实运行态量化：

- overview 卡：`367 × 161`，共 `3` 张
- 三组 `table-card` 宽度均为 `1134px`
- 第一组卡高度：`427px`
- 后两组卡高度：`529px`
- 设置项行高：约 `101-102px`

对应截图：

- current：`D:\XM\kaipai-team\output\playwright\00-88\settings-before.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-88\settings-reference.png`

### 2.2 reference 的核心语义

从 reference 可确认：

- 页面直接进入三组设置列表
- 没有单独的一排 overview 大卡
- 每组卡宽度明显收窄，并靠左排布
- 每条设置项更接近轻量列表，而不是当前的大号说明卡

## 3. 设计策略

### 3.1 移除 overview

当前 overview 摘要信息不是系统设置页的必要第一语义，而且压低了真正的设置列表。
本轮直接移除该层，而不是继续压缩。

### 3.2 设置卡局部 class

为三张设置卡增加本地 class，例如：

- `settings-card`

确保宽度、header 和条目样式只作用于 `SettingsView.vue`。

### 3.3 设置条目收紧

本轮只做局部密度收口：

- `settings-groups`
- `settings-card`
- `settings-list`
- `settings-item`
- `settings-item__copy`
- `settings-item__value`

### 3.4 事实源边界

reference 中的：

- `juming.app`
- `help@juming.app`

当前运行态没有稳定事实源，因此继续保留：

- 真实值
- 或显式“待补事实源”

不做伪造补全。

## 4. 风险与边界

### 4.1 已确认

- 当前是 `SettingsView.vue` 的首屏结构问题
- 不需要改共享壳层
- 不需要触碰子页能力

### 4.2 待验证

- overview 移除后首屏是否更接近 reference
- 条目收紧后可读性是否仍稳定
- 卡片宽度左收后是否不会造成文案拥挤

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
