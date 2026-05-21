# 00-85 设计说明

## 1. 设计目标

`00-85` 只解决分享内容详情抽屉：

1. **drawer shell**：抽屉宽度、header 与 body padding 收紧
2. **detail hero**：标题、身份与状态保持可读，但降低首屏占高
3. **detail density**：字段块由默认大卡片节奏收成更高密度的治理详情面板

## 2. 已核实的事实

### 2.1 当前问题仍只在 `ShareCardsView.vue`

真实浏览器已确认：

- 路径：`http://127.0.0.1:5100/content/share-cards`
- 操作：切到 `列表视图` 后点击首行 `查看详情`
- 截图：`D:\XM\kaipai-team\output\playwright\00-85\share-cards-detail-drawer-before.png`

当前量化：

- 抽屉宽度：`920px`
- header 高度：`77px`
- body padding：`22px 26px 26px 26px`
- hero 高度：`85px`
- `detail-block` 高度：`92px`
- 第一组 `detail-card` 高度：约 `665px`

### 2.2 当前不应混入其它区域

`00-83` 和 `00-84` 已分别完成卡片墙与列表视图收口。详情抽屉是同页剩余的自然后续问题，但不能回退改动范围。

## 3. 设计策略

### 3.1 增加抽屉本地 class

为 `el-drawer` 增加本地 class：

- `content-detail-drawer`

所有壳层收口通过该 class 限定，避免影响其他 Element Plus drawer。

### 3.2 抽屉壳层

本轮收紧：

- `size`
- `el-drawer__header`
- `el-drawer__body`
- close button 尺寸

### 3.3 详情内容

本轮只做视觉密度：

- `.detail-layout` gap
- `.drawer-hero` padding / radius / 标题层级
- `.detail-card` header / body padding
- `.detail-grid` gap
- `.detail-block` padding / min-height / 字号 / 行高
- `.issue-section` 与 issue item 的间距和高度

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及详情抽屉视觉密度
- 不影响详情数据读取
- 不影响 `查看详情` 可点击性
- 不影响 legacy 修复动作

### 4.2 待验证

- 字段块收紧后是否仍可读
- 抽屉宽度收紧后双列字段是否仍不拥挤
- 首屏是否比修复前能呈现更多有效详情

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
