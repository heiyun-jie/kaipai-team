# 00-148 小程序页面操作流程审查与重构任务

## 目标

按用户 2026-04-26 最新要求，重构小程序指定页面的操作流程和 UI 细节。所有条目必须完成源码审查、构建审查和残留关键词审查后才允许标记通过。

## 范围

- `kaipai-frontend/src/pages/home/index.vue`
- `kaipai-frontend/src/pkg-card/card-list/index.vue`
- `kaipai-frontend/src/pages/actor-profile/edit.vue`
- `kaipai-frontend/src/pages/mine/index.vue`
- `kaipai-frontend/src/pkg-tools/webview/index.vue`
- 必要时新增风格详情页、收藏列表页，并同步 `pages.json`

## 用户验收标准

- [x] `pages/home/index` 风格分馆点击进入风格详情，不直接进入创建或编辑分享卡。
- [x] `pages/home/index` 操作指南是视频入口，不允许在无视频时跳转 `pages/actor-profile/edit`。
- [x] `pkg-card/card-list/index` 底部主按钮文案为“下一步”，不是“生成分享卡片”。
- [x] `pages/actor-profile/edit` 顶部说明文案放在标题右侧，两行展示。
- [x] `pages/actor-profile/edit` `.kp-header.kp-header--gradient.actor-edit-page__header` 的 `padding-bottom: 72rpx` 缩减一半。
- [x] `pages/actor-profile/edit` 页面框与框的上下间距按统一节奏收敛，不保留异常大间距。
- [x] `pages/actor-profile/edit` 底部只保留“确认保存”。
- [x] `pages/mine/index` “我的作品集”跳转到我可分享的列表。
- [x] `pages/mine/index` “收藏的分享”跳转到我收藏的列表，不跳转记录页。
- [x] `pkg-tools/webview/index` 删除 `.tool-page__hero-copy { margin-top: 36rpx; }`。

## 审查门禁

- [x] `npm run type-check`
- [x] `npm run build:mp-weixin`
- [x] `npm run audit:mp-package`
- [x] 源码关键词审查：不得保留被点名的旧路由、旧按钮、旧样式残留。
- [x] 构建产物关键词审查：不得保留被点名的旧按钮和旧样式残留。

## 审查评分

- 代码实现完整度 45 分。
- 页面流程一致性 25 分。
- UI 细节与残留清理 15 分。
- 构建与分包审查 10 分。
- 人工验收预留 5 分。

内部审查低于 95 分时必须继续修改，不允许收尾。
