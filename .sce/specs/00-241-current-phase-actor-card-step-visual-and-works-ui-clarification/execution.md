# 演员卡主视觉与参演作品步骤 UI 澄清 - 执行记录

> 完成时间：2026-08-28

## 1. 实现

- 保留 `backgroundImageUrl`、`source_image/sourceImageUrl`、`expandedImageUrl` 三套现有合同；步骤页 AI 扩图可见性已由 `00-245` 收口，扩图结果仅作为内部/历史字段。
- 主视觉页新增两个清晰区段；原图使用 `aspectFit + 520rpx` 稳定预览，根容器和 `scroll-view` 建立 `100vh -> flex/height:0` 高度链。
- 两页 `onShow` 均复位 `navigating`，从下一页返回后不再残留 loading。
- 作品列表尾入口和计数只在 `works.length > 0` 且无 loading/error 时显示，空态保留单一“去新增作品”入口。

## 2. 构建与产物

- `npx uni build -p mp-weixin`：成功。
- `npm run dev:mp-weixin`：成功生成固定开发目录后结束本轮 watcher，未关闭或置顶微信开发者工具。
- MCP artifact check：两个路由的 build/dev JS、WXML、WXSS 哈希全部一致；页面未使用 scoped style，双方 `data-v` 集合均为空。

## 3. 验证

- `verify:actor-card-step-ui`：19 项通过。
- `verify:v3-step-works`：12 项通过。
- `verify:v3-asset-wizard`：68 项通过。
- `verify:v3-home`：17 项通过。
- `verify:nav-title`：101 项通过。
- `verify:tdesign-migration`：1331 项通过。
- `type-check`：通过。
- 内部模拟器截图确认空列表无重复入口、主视觉底部可达且不被 CTA 遮挡。

## 4. 兼容与残余

接口、数据库、路由、素材 usage、旧草稿和已发布演员卡均未变化。包体保持低于 2 MB；全局包体审计仍报告 7 条既有外链字符串，本轮差异未新增 URL。

完整命令、输入、输出、哈希和副本回滚证据见 `.sce/evidence/20260828-actor-card-step-ui/VERIFICATION.txt`。
