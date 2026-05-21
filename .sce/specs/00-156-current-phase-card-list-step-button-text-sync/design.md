# 00-156 设计

## 原因

`card-list` 当前使用 `KpButton` 默认 slot 传入 `creatorActionText`：

```vue
<KpButton>{{ creatorActionText }}</KpButton>
```

在小程序自定义组件编译产物中，slot 内容没有稳定跟随父组件状态刷新，导致页面已进入 `STEP 03`，按钮仍显示旧的 `STEP 01` 文案。

## 方案

- 改为使用 `KpButton` 的 `text` prop：`:text="creatorActionText"`。
- `creatorActionText` 在 `currentStep === 3` 时固定返回 `保存并预览`。

## 不做事项

- 不修改 `KpButton` 全局组件行为，避免影响其他页面。
- 不恢复旧直跳预览流程。
