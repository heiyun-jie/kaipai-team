# 00-152 执行记录

## 2026-04-27 任务建立

触发原因：

- `pages/actor-profile/detail` 顶部间距过高。
- `pkg-card/actor-card/index` 第 3 步底部按钮仍显示旧的第 1 步文案。
- `pkg-card/card-list/index` 点击 `下一步` 后再次进入 `actor-card` 三步编辑器，和创建分享页三步流程冲突。

## 已完成修改

- `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - 移除 `.actor-detail-page__hero-copy` 的 `padding: 136rpx 0 0`。
- `kaipai-frontend/src/components/KpButton.vue`
  - 新增可选 `text` 属性。
  - 当传入 `text` 时优先渲染属性文本；未传入时继续渲染默认 slot。
- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - 第 3 步标题改为 `第 3 步：保存配置`。
  - 第 3 步主按钮改为 `保存配置`。
  - 编辑态主按钮使用 `:text="bottomActionText"`，并用 `editStep + bottomActionText` 作为 `key` 强制刷新节点，避免小程序端 slot 复用旧文案。
  - 第 1 步仍为 `下一步：快速调节`，第 2 步仍为 `下一步：内容配置`，第 3 步才保存。
- `kaipai-frontend/src/pkg-card/card-list/index.vue`
  - `buildCreatorPreviewPath` 增加 `shared=1`。
  - 底部 `下一步`、已创建列表的 `卡片/海报` 进入 `actor-card` 预览模式，不再展示三步编辑器。
  - 已创建列表的 `编辑` 仍使用 `buildShareCardEditorPath` 进入三步编辑器。
  - 底部提示改为：进入预览；如需调整布局和内容，在已创建分享里点击 `编辑`。

## 本地审查

- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过，并已同步到 `dist/dev/mp-weixin`。
- `npm run audit:mp-package`：通过。

包体结果：

```text
main      508.68 KB / 2 MB
pkg-card  114.02 KB / 2 MB
pkg-tools 28.21 KB / 2 MB
```

## 源码和产物审查

- `rg -n 'padding:\s*136rpx\s+0\s+0' ...`：无匹配。
- `rg -n '保存分享配置' ...`：无匹配。
- `rg -n '接下来的微调继续在预览页完成' ...`：无匹配。
- `dist/build/mp-weixin/pkg-card/actor-card/index.js` 与 `dist/dev/mp-weixin/pkg-card/actor-card/index.js` 均包含：
  - `第 3 步：保存配置`
  - `保存配置`
  - `text:Te.value`
  - `edit-action-${A.value}-${Te.value}`
- `dist/build/mp-weixin/components/KpButton.js` 与 `dist/dev/mp-weixin/components/KpButton.js` 均包含 `text` 属性。
- `dist/dev/mp-weixin/components/KpButton.wxml` 确认 `text` 属性优先渲染，未传入时才渲染默认 slot。
- `src/pkg-card/card-list/index.vue` 和构建产物均确认预览路径为：

```text
/pkg-card/actor-card/index?shared=1&shareCardId=${cardId}&artifact=${artifact}
```

- `handleCardEdit` 仍保留编辑路径 `buildShareCardEditorPath(buildShareCardEditorTarget(...))`，未添加 `shared=1`。
- `src/pkg-card/card-list/index.vue` 和构建产物均确认提示文案已改为 `如需调整布局和内容，请在已创建分享里点击“编辑”`。

## 审查结论

- `pages/actor-profile/detail` 顶部 136rpx padding 已删除。
- `pkg-card/actor-card/index` 第 3 步按钮将通过属性文本显示 `保存配置`，不再依赖可能被小程序端复用的默认 slot。
- `pkg-card/card-list/index` 的 `下一步` 进入分享预览模式，和 `actor-card` 三步编辑器不再叠加。

当前状态：已完成。

内部审查评分：96 / 95。
