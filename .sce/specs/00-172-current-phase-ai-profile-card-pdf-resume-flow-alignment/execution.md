# 00-172 执行记录

## 1. 问题契约

用户反馈：“AI 分享图详情页的前端展示范围没有跟 PDF 简历 Spec 同步扩展。”

已核对：

1. `05-13` 要求公开分享详情页在 `resumePdfPageImageUrls` 存在时展示 PDF 简历图片页。
2. 普通公开详情页 `pages/actor-profile/detail.vue` 已实现 PDF 简历区块。
3. `00-171` 的 AI 分享图详情页内容流只覆盖基础资料、形象语言、技能、简介、拍摄经历、照片和视频，未展示 PDF 简历。

## 2. 本轮边界

只补 `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue` 的内容流展示范围。

不改：

1. PDF 上传和后端转换。
2. `ActorProfile` 类型字段。
3. AI profile card 生成任务、provider、prompt、质检。
4. 普通公开详情页既有 PDF 展示。

## 3. 实施记录

已完成：

1. 新增 `00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment`，明确本轮只同步 AI 分享图详情页展示范围。
2. 更新 `.sce/specs/README.md`，追加 `00-172` 增量登记与 Spec 目录行。
3. 修改 `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`：
   - 新增 `resumePdfPageImageUrls` 计算属性，展示资格只来自 `ActorProfile.resumePdfPageImageUrls.length > 0`。
   - 新增 `resumePdfDesc`，优先展示 `actor.resumePdfName`。
   - 在主题内容流最底部、“视频简历”之后新增“PDF 简历”section。
   - 使用 `<image mode="widthFix" lazy-load>` 按顺序展示 PDF 图片页。
   - 新增 `previewPdfPage(index)`，点击 PDF 页时用同一图片页列表预览。
   - 新增 PDF section 样式，复用 `--ai-share-*` theme token。

未改：

1. 未改 PDF 上传、保存、后端转图片页。
2. 未改 AI 分享图生成、prompt、provider、质检或 `generatedImageUrl` 合同。
3. 未新增 PDF.js、web-view 或 AI 详情页专属 PDF 状态。

## 4. 验证记录

已执行：

```powershell
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:mp-package
```

```powershell
node .sce\specs\00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment\e2e-ai-detail-pdf-flow.mjs
```

结果：

1. `type-check` 通过。
2. `build:mp-weixin` 通过，并执行 `postbuild:mp-weixin` 同步到 `dist/dev/mp-weixin`。
3. 构建过程只有既有 `Dart Sass legacy JS API` deprecation warning、uni 新版本提示和 `types/project` empty chunk 提示，无阻断。
4. `audit:mp-package` 通过：
   - main：`533.24 KB / 2.00 MB`
   - pkg-card：`201.87 KB / 2.00 MB`
   - pkg-tools：`28.31 KB / 2.00 MB`
5. 已用 `rg` 确认构建产物 `dist/build/mp-weixin/pkg-card/ai-profile-card-detail` 包含 “PDF 简历”、`pdf-page` 与 `resumePdfPageImageUrls` 相关输出。
6. 自动化 H5 E2E 通过：
   - 启动 mock API：`http://127.0.0.1:58072`
   - 启动 H5 dev server：`http://127.0.0.1:58073`
   - 使用 Chrome headless 访问 `/#/pkg-card/ai-profile-card-detail/index?shareCardId=17201&shared=1`
   - 断言通过：`PDF 简历`、`自动化演员PDF简历.pdf`、`2 页`、`ai-share-detail-page__pdf-page`、两张 `resumePdfPageImageUrls` 图片页 URL
   - 断言通过：`PDF 简历` 出现在内容流 `视频简历` 之后。
   - 断言页面未进入 `分享图加载失败` 或 `暂无 AI 封面` 状态。

当前未执行真实样例 PDF 上传和页面人工浏览验收；该项仍归 `05-13` 的真实上传与详情页展示检查，不作为本轮 `00-172` 的阻断项。

## 5. 复测记录

2026-05-22 19:33:30 +08:00 已重新实际执行以下验证命令：

```powershell
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:mp-package
cd ..
node .sce\specs\00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment\e2e-ai-detail-pdf-flow.mjs
```

复测结果：

1. `npm run type-check` 通过。
2. `npm run build:mp-weixin` 通过，并同步 `dist/dev/mp-weixin`。
3. `npm run audit:mp-package` 通过：
   - main：`533.24 KB / 2.00 MB`
   - pkg-card：`201.87 KB / 2.00 MB`
   - pkg-tools：`28.31 KB / 2.00 MB`
4. `node .sce\specs\00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment\e2e-ai-detail-pdf-flow.mjs` 通过，输出 `status: passed`。
5. E2E 断言包含 `PDF section is rendered after video section`，确认 PDF 简历位于内容流视频简历之后。
6. 复测后确认 `58072 / 58073` 无残留监听，临时 Chrome profile 无残留。
