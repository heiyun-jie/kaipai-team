# 00-152 需求

## 范围

- `pages/actor-profile/detail`
- `pkg-card/actor-card/index`
- `pkg-card/card-list/index`
- 共享按钮组件仅允许为解决小程序渲染状态不同步问题做兼容当前新逻辑的干净改造，不保留旧流程兜底。

## 用户问题

1. `pages/actor-profile/detail` 顶部存在过高间距：
   - `.actor-detail-page__hero-copy { padding: 136rpx 0 0; }`
2. `pkg-card/actor-card/index` 已经在第 3 步时，底部主按钮仍显示 `下一步：快速调节`。
   - 第 3 步底部主按钮必须显示 `保存配置`。
3. `pkg-card/card-list/index` 本身已有创建分享页三步流程，点击 `下一步` 进入 `pkg-card/actor-card/index` 后又展示三步编辑流程，操作逻辑冲突。

## 验收标准

- `pages/actor-profile/detail` 构建产物中不再出现 `.actor-detail-page__hero-copy` 的 `padding:136rpx 0 0`。
- `pkg-card/actor-card/index` 第 3 步底部主按钮显示 `保存配置`，不再显示第 1 步文案。
- `pkg-card/actor-card/index` 的编辑态第 1 步和第 2 步仍然是下一步操作，第 3 步才保存。
- `pkg-card/card-list/index` 点击底部 `下一步` 或已创建列表的 `卡片/海报` 进入 `actor-card` 时，进入分享预览模式，不展示 `actor-card` 的三步编辑器。
- `pkg-card/card-list/index` 已创建列表的 `编辑` 入口仍进入 `actor-card` 三步编辑器。
- `npm run type-check`、`npm run build:mp-weixin`、`npm run audit:mp-package` 必须通过。
- 源码和构建产物必须正向审查通过，评分不得低于 95。
