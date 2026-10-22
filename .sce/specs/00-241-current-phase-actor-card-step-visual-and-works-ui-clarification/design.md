# 演员卡主视觉与参演作品步骤 UI 澄清 - 技术设计

_Requirements: 2.1-2.3, 3, 4_

## 1. 字段追溯

| 页面概念 | 现有字段 / usage | 写入与消费 | 本次处理 |
|---|---|---|---|
| 版式背景 | `backgroundImageUrl` | 步骤 1 保存；演员卡渲染器作为版式主背景候选 | 只改可见名称和区段层级 |
| 主视觉原图 | `source_image` / `sourceImageUrl` | 素材绑定；AI 扩图输入；旧 URL 兼容写入 | 统一命名，预览改 `aspectFit` |
| AI 扩图结果 | `expandedImageUrl` | 内部扩图任务或历史草稿 | 保持字段与保存合同；步骤页可见性由 `00-245` 定义 |

三个字段承担不同职责，因此不合并字段、不迁移数据。UI 通过名称、说明和区段边界消除“背景图等于首图”的误解。

## 2. 页面布局

### 2.1 `step-visual`

1. 根容器使用 `height: 100vh; min-height: 0`，导航头保持 `flex-shrink: 0`。
2. `scroll-view` 使用 `flex: 1; height: 0; min-height: 0`，底部 padding 覆盖固定操作栏和安全区。
3. 版式背景与主视觉原图分别使用白底细边区段，内部遵循 `24rpx` 内边距、`16rpx` 连续间距和 `12/16rpx` 圆角合同。
4. 主视觉预览固定为 `520rpx` 高，图片使用 `aspectFit`，背景使用 muted surface，避免不同比例图片改变布局或裁掉人物；步骤页不渲染 AI 扩图区段。
5. `onShow` 首先重置 `navigating=false`，再消费素材选择会话。

### 2.2 `step-works`

列表尾追加入口与计数统一受 `!loading && !loadError && works.length` 控制。空态继续提供单一可执行 CTA；作品卡内首张剧照继续显示“封面”。`onShow` 首先重置导航状态，再处理剧照选择返回值。

## 3. 产物门禁

新增 `verify-00241-actor-card-step-ui.mjs`：

- 源码检查三个字段未被合并、文案区分、`aspectFit`、固定高度链和 `onShow` 复位。
- 源码检查作品空态与列表尾入口互斥、计数文案收敛。
- build/dev 检查 WXML 可见文案与 WXSS 布局规则。
- build/dev 检查两个页面的 scoped `data-v` 一致。

## 4. 回滚

回滚只需恢复两个页面的原始副本并重新执行 `npm run build:mp-weixin`。接口、数据库和历史数据未变化，不需要数据回滚。
