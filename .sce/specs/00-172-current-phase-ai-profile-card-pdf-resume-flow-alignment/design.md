# AI 分享图详情页 PDF 简历展示范围同步 - 技术设计

## 1. 设计结论

本轮只改小程序前端 AI 分享图详情页：

```text
loadShareCardLatestSnapshot
  -> personalization.actorSnapshot
  -> ActorProfile.resumePdfPageImageUrls
  -> pkg-card/ai-profile-card-detail content-flow PDF section
```

PDF 简历不进入 AI 生图链路，不进入 prompt，不影响 `generatedImageUrl` 的成功判断。它只是 `00-171` 主题内容流中的一个确定性资料 section。

## 2. 影响范围

### 2.1 代码文件

1. `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
   - 新增 `resumePdfPageImageUrls` 计算属性。
   - 新增 `resumePdfDesc` 计算属性。
   - 新增 PDF 简历 section。
   - 新增 PDF 页预览函数。
   - 新增 PDF section 样式。

2. `.sce/specs/README.md`
   - 增量登记 `00-172`。

### 2.2 不改范围

1. 不改后端 PDF 上传与转换。
2. 不改 `ActorProfile` 类型字段。
3. 不改普通公开详情页 `pages/actor-profile/detail.vue` 已有 PDF 展示。
4. 不改 AI profile card 生成任务、provider、质检或 `generatedImageUrl` 合同。

## 3. 前端设计

### 3.1 数据来源

使用现有 `actor`：

```ts
const resumePdfPageImageUrls = computed(() =>
  [...(actor.value?.resumePdfPageImageUrls || [])].filter(Boolean),
);
```

展示资格：

```ts
resumePdfPageImageUrls.value.length > 0
```

该判断与普通公开详情页保持同一字段语义，避免新增 AI 详情页专属展示状态。

### 3.2 模板结构

插入在内容流最底部，即“视频简历”之后、底部操作栏之前：

```text
section PDF 简历
  section head: PDF 简历 / N 页
  description: 公开原稿：filename 或默认说明
  pdf pages:
    image mode=widthFix lazy-load
```

插入位置的理由：

1. PDF 简历是原稿附件，信息密度高，适合作为完整资料补充放在结构化内容之后。
2. 放在最底部可以先让访客浏览 AI 封面、基础资料、经历、照片与视频，再查看原始 PDF。
3. 不影响首屏单封面和主题内容流的阅读节奏。

### 3.3 预览

点击 PDF 单页时调用：

```ts
uni.previewImage({
  urls: resumePdfPageImageUrls.value,
  current: resumePdfPageImageUrls.value[index],
});
```

### 3.4 样式

1. PDF section 继续使用 `--ai-share-surface / --ai-share-border / --ai-share-background`。
2. 图片使用 `mode="widthFix"` 保持页面比例。
3. 单页容器使用浅背景与边框承接图片加载态。
4. 内容流现有底部 padding 继续承接固定底部操作栏。

## 4. 测试设计

1. `cd kaipai-frontend && npm run type-check`
2. `cd kaipai-frontend && npm run build:mp-weixin`
3. `node .sce/specs/00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment/e2e-ai-detail-pdf-flow.mjs`
4. 静态确认 `pkg-card/ai-profile-card-detail/index.vue` 不新增 PDF.js、web-view 或 AI 专属 PDF 状态。

### 4.1 自动化 H5 E2E

`e2e-ai-detail-pdf-flow.mjs` 启动本地 mock API 与 H5 dev server，并使用 Chrome headless 访问：

```text
/#/pkg-card/ai-profile-card-detail/index?shareCardId=17201&shared=1
```

覆盖链路：

```text
mock /api/card/personalization
  -> actorSnapshot.resumePdfPageImageUrls
  -> loadShareCardLatestSnapshot
  -> AI 分享图详情页 content-flow
  -> PDF 简历 section DOM
```

断言内容：

1. 页面出现 `PDF 简历` 标题。
2. 页面出现 mock PDF 文件名。
3. 页面出现 `2 页` 页数。
4. 页面出现 PDF 页容器 class。
5. 页面包含两张 PDF 图片页 URL。
6. 页面顺序满足 `PDF 简历` 出现在内容流 `视频简历` 之后。

## 5. 风险与边界

1. 如果 `personalization.actorSnapshot` 未携带 PDF 字段，前端会自然不展示 PDF 区块；这属于接口事实源缺口，不在本轮伪造展示。
2. 如果 PDF 图片页 URL 加载失败，当前小程序 `<image>` 失败不会阻断页面主流程；后续如需页级失败占位可单独建 Spec。
3. 本轮不执行真实样例 PDF 上传验证，该未完成项仍归 `05-13` 的真实上传与详情页展示检查。
