# 00-152 设计

## 顶部间距

`pages/actor-profile/detail` 直接移除 `actor-detail-page__hero-copy` 的 `padding: 136rpx 0 0`，不新增兜底样式。

## actor-card 底部按钮

第 3 步主按钮文案统一为 `保存配置`。

截图显示标题已经进入第 3 步，但按钮仍显示第 1 步文案，说明小程序端组件插槽存在复用后未刷新风险。为避免旧文本残留：

- `KpButton` 增加可选 `text` 属性。
- `actor-card` 的动态主按钮使用 `:text="bottomActionText"`，不再把动态文案放在默认 slot 中。
- 编辑态主按钮增加基于步骤和文案的 `key`，步骤变化时强制刷新按钮节点。

## card-list 到 actor-card 流程

`card-list` 是创建分享页流程，底部 `下一步` 的目标应是分享预览，不应再次进入编辑三步。

- `buildCreatorPreviewPath` 增加 `shared=1`。
- `handleCardEdit` 保持使用 `buildShareCardEditorPath`，不加 `shared=1`，作为唯一进入三步编辑器的入口。

## 不做事项

- 不改后端接口。
- 不保留旧跳转逻辑兜底。
- 不新增第二套草稿模型。
