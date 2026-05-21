# 00-155 设计

## 方案

在 `pkg-card/actor-card/index` 中按分享产物区分底部动作：

- `miniProgramCard`：只显示一个主按钮 `发送给好友`，使用 `open-type="share"`。
- `poster`：显示 `保存相册` 和 `分享到朋友圈`。

## 清理

- 删除 `copyCurrentShareLink`。
- 删除卡片模式下的 `复制链接` 按钮。
- 调整卡片模式底部按钮为单列布局。

## 不做事项

- 不删除 `buildSelectedSharePath`，该方法仍用于微信分享状态和海报入口路径。
- 不修改 `actor-card` 的预览数据加载链路。
