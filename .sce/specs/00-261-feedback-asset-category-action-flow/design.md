# 技术设计

## 1. 事件证据
tdesign-miniprogram@1.16.0 miniprogram_dist/action-sheet/action-sheet.js 中 onSelect 依次触发 selected、close(trigger=select)、visible-change(false)。assets/index.vue selected同步打开同一sheet后，后两个事件覆盖新visible状态。

## 2. 修复
素材操作菜单与分类选择菜单各持独立 visible、items 和回调，原菜单 close 只影响原菜单。分类目标保留当前素材，分类busy锁与错误反馈独立。不靠延迟定时器猜事件间隔。

_Requirements: 2_

## 3. 验证
按真实事件顺序 selected→close→visible-change 注入，分类sheet仍保持打开；选项保存失败/重试/重复点击与既有操作回归；TDesign、游客、照片网格、type-check和固定dev构建产物。

## 4. 2026-10-20 “修改后没有生效”根因
- 测试环境 Candidate `20260901-221652-v3-draft` 的 `pages/assets/index.js` 仍是单弹层实现：`changeCategory` 在 selected 回调中把同一 ActionSheet 切成分类列表，随后 close / visible-change(false) 立刻关掉，且无任何成功/失败反馈 —— 用户实际遇到的“没生效”。本地 2026-10-13 修复未部署，测试环境不含该修复。
- 后端 `PUT /api/actor/assets/{id}` 在已提交版与本地均校验并 `updateById` 写入 `category_code`；`version NOT NULL DEFAULT 0`，乐观锁不会静默 0 行。后端不是根因。
- 第二层：00-227 三列照片网格只渲染图片、状态与“…”，不显示分类；分类弹层也不标当前值。即使保存成功，照片 Tab 上没有任何可见变化，用户仍会判定未生效。
- 修复：照片格子左上角新增 `assets-page__photo-category` 分类角标（右上为操作按钮、底部为处理状态，互不遮挡）；分类 ActionSheet 使用 `description` 显示当前分类，当前项追加“（当前）”并着品牌色；选择当前分类直接关闭不提交。

_Requirements: 4_
