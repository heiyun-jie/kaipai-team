# 00-201 任务拆解 — 首页 AI 优先简化与阴阳鱼双入口

> **状态：已降级为历史 Spec（`00-210` 轮次，用户裁决）。以下任务勾选状态只反映当时事实，不再作为当前门禁。**
>
> 实现载体 `pages/home/index.vue` 已被 `00-206 T7` 整体替换，本 Spec 的任务与验收断言已无对应运行态结构。
> 不要再执行、修复或试图让这些断言转绿；当前首页以 `00-206` / `00-210` 为准。
>
> 历史记录：`600rpx` → `540rpx` 仅减少 `30px`、用户感知不明显，后改为减少 `60px` 的 `480rpx`。该结论已随首页替换失效。

## T1 书面 Spec（requirements + design）
- [x] requirements.md：主动作 / 诚实语义 / 删除手动选风格 / 手动创建分享次级入口 / 继承 00-187
- [x] design.md：元素盘点、目标层级、低保真布局、分支跳转、验证方式
- [x] 用户以明确实现指令通过门禁

## T2 首页实现（评审通过后）
- [x] 移除 stats-strip 内 `home-page__ai-link`（AI pill）
- [x] 移除 `home-page__section--guide` 视频封面 `home-page__guide-stage` 与 `openGuideVideo` 触发
- [x] 移除并列主 CTA `home-page__guide-cta`（`开始创建分享页`）
- [x] 新增首屏唯一 AI 主入口内容（复用 `goAiProfileCard()`）+ 诚实前置提示文案
- [x] 完整删除「手动选风格」标题、三风格卡、加载 / 空态和对应数据消费
- [x] 删除 `我的数据 ›` 轻链接（保留 `goMine` 供 crew 身份分支复用）
- [x] 清理因移除内容而产生的死代码 / 死依赖（视频、模板、卡片列表加载与风格 helper）
- [x] 精简 hero 高度与标题字号
- [x] 生成并接入 `/static/home/yin-yang-creation.png`：黑鱼左上、米白鱼右下，图片内固化 S 曲线和反色鱼眼
- [x] 以单一 `home-page__creation-stage` 背景舞台替换上下卡结构，删除鱼身 / 鱼眼拼形节点、手动入口圆形图标和两张独立卡面
- [x] 将 AI 文案锚定左上黑色安全区、手动文案锚定右下米白安全区；后台等尺寸预览确认两区未遮挡位图鱼眼或 S 形主体
- [x] 新增两个无背景 / 边框 / 阴影且互不重叠的透明点击区，分别复用 `goAiProfileCard()` / `goCardList()`；舞台自身不绑定第三个动作
- [x] 将背景图从 `1316x1200` 上下居中裁切为 `1316x1080`，保持鱼身、S 曲线、鱼眼和纹理比例不变
- [x] 将 `home-page__creation-stage` 高度从 `600rpx` 调整为 `540rpx`，入口内边距从 `30rpx` 调整为 `26rpx`，两点击区各保持 `270rpx`
- [x] 将背景图从 `1316x1080` 再居中裁切为 `1316x960`，保持鱼身、S 曲线、鱼眼和纹理比例不变
- [x] 将舞台从 `540rpx` 调整为 `480rpx`，入口内边距从 `26rpx` 调整为 `22rpx`，步骤区上下间距从 `20rpx` 调整为 `16rpx`

## T3 构建与产物核验
- [x] CSS 拼形历史轮次曾完成 type-check、构建、双路由与 `00-187` / `00-192` 验证；该证据不核销最新位图背景合同
- [x] 位图背景轮次重新执行 type-check、构建、`00-187`、`00-192` 与 steering audit，全部通过
- [x] 重新执行包体审计；命令被既有 `dist/build/mp-weixin/api/actor-asset.js` 本地 URL 阻断，并已单独核算主包与各分包均低于 2 MB
- [x] 核对 `/static/home/yin-yang-creation.png`、两个独立 `bindtap` 与双路由进入产物；`creation-pair`、`*-fish-lobe`、`*-fish-eye`、`KpMineIcon` 及旧风格区全部消失
- [x] 核对 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 首页 WXML / WXSS / JS 及背景位图 SHA-256 一致
- [x] 使用无头浏览器按 `375x812` 视口、`329x300` 舞台等尺寸预览真实背景与当前文字叠层，确认单一画面、左上 / 右下锚点及无相互遮挡
- [x] 高度调整后重新执行 type-check、构建、产物尺寸 / 哈希 / 关键字核对及 `329x270` 无头视觉预览
- [x] `480rpx` 调整后重新执行 type-check、构建、source / build / dev 三层值核对及 `329x240` 无头视觉预览
- [ ] 微信开发者工具手动点击一次“编译”，使当前模拟器缓存从 `540rpx` 刷新到 `480rpx`；遵守后台操作要求，本轮不代替用户聚焦窗口点击
- [ ] 微信开发者工具前台运行态实点：遵守用户不置顶、不切换桌面窗口的要求，本轮不执行且不声称已验证

## T4 文档同步
- [x] `spec-code-mapping.md` 登记 00-201 ↔ `home/index.vue`
- [x] `README.md` 与 `spec-code-mapping.md` 将 00-201 更新为位图背景视觉调整中
- [x] 新增 `execution.md`，记录实现、产物、门禁与残余审计事实
- [x] `CURRENT_CONTEXT.md` 本轮不改；当前事实由 00-201 package、全局 Spec 索引与代码映射共同承接
