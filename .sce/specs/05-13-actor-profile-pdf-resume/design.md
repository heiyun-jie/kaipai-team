# 演员档案 PDF 简历上传与图片页渲染 - 技术设计

## 1. 设计结论

第一版把 PDF 视为“演员简历原稿附件”，不把 PDF 解析为结构化档案字段。

```text
小程序选择 PDF
  -> POST /api/file/upload/pdf
  -> 后端校验 PDF
  -> 后端上传原 PDF 到 COS
  -> 后端用 PDFBox 渲染每页图片
  -> 后端上传页面图片到 COS
  -> 前端保存 PDF 元数据到演员档案
  -> 公开详情页按图片页顺序渲染
```

## 2. 后端设计

### 2.1 PDF 上传接口

新增：

```text
POST /api/file/upload/pdf
```

返回：

```json
{
  "url": "https://.../actor-resume-pdf/2026/05/21/xxx.pdf",
  "name": "演员舒宁～.pdf",
  "pageCount": 13,
  "pageImageUrls": [
    "https://.../actor-resume-pdf-pages/2026/05/21/xxx-001.jpg"
  ]
}
```

接口职责：

1. 校验大小，第一版限制 20MB。
2. 校验文件名后缀、MIME 和 `%PDF-` 文件头。
3. 校验页数，第一版限制 20 页。
4. 渲染图片页并上传 COS。
5. 任何一步失败时整体返回失败，不给前端半成品。

### 2.2 PDF 转图片服务

新增 `ActorProfilePdfResumeRenderService`：

```java
PdfResumeRenderResult renderAndUpload(MultipartFile file)
```

实现策略：

1. 使用 Apache PDFBox 加载 PDF。
2. 拒绝加密或不可读取 PDF。
3. 使用 `PDFRenderer` 渲染每页。
4. 控制输出宽度，目标最大宽度约 1200px。
5. JPEG 压缩上传到 COS，文件夹 `actor-resume-pdf-pages`。

### 2.3 COS 工具扩展

`CosUtil` 扩展：

1. `uploadPdf(MultipartFile file, String folder)`
2. `uploadBytes(byte[] bytes, String contentType, String folder, String extension)`

继续由后端统一生成 COS URL，前端不接触 COS 凭证。

### 2.4 档案 DTO 扩展

`ActorProfileDTO` / `ActorProfileSaveDTO` 增加：

```java
private String resumePdfUrl;
private String resumePdfName;
private Integer resumePdfPageCount;
private List<String> resumePdfPageImageUrls = new ArrayList<>();
```

第一版落库沿用 `actor_profile.extended_field`，扩展 `ProfileExtras`，避免为单 PDF 原稿展示引入新表。

## 3. 前端设计

### 3.1 类型扩展

`types/actor.ts`：

```ts
interface ActorProfile {
  resumePdfUrl?: string
  resumePdfName?: string
  resumePdfPageCount?: number
  resumePdfPageImageUrls?: string[]
}
```

### 3.2 上传工具

`utils/upload.ts` 扩展：

```ts
uploadPdf(filePath: string, fileName?: string): Promise<PdfUploadResult>
```

`utils/media-picker.ts` 扩展：

```ts
choosePdfFile(): Promise<{ path: string; name: string; size?: number } | null>
```

微信小程序优先使用 `uni.chooseMessageFile({ type: 'file', extension: ['pdf'] })`。

### 3.3 编辑页

新增组件：

```text
pages/actor-profile/components/PdfResumeSection.vue
```

职责：

1. 展示当前 PDF 文件名、页数、图片页数量。
2. 支持上传、替换、删除。
3. 上传中展示进度或状态。

`edit.vue` 继续集中维护表单状态，新增字段写入 `ActorProfileFormModel`。

### 3.4 公开详情页

`pages/actor-profile/detail.vue` 新增“PDF 简历”卡片：

```text
PDF 简历
  page 1 image
  page 2 image
  ...
```

渲染规则：

1. `resumePdfPageImageUrls.length > 0` 才展示。
2. 使用 `<image mode="widthFix" lazy-load>` 保持页面比例。
3. 单页加载失败时显示页级占位。
4. 详情页底部安全距离继续保留，避免操作栏遮挡最后一页。

## 4. 兼容边界

1. 没有 PDF 的旧档案不受影响。
2. 旧客户端忽略新增字段即可。
3. 删除 PDF 时只清空档案元数据，不强制同步删除 COS 历史文件。
4. PDF 原稿和图片页都属于公开资料附件，进入分享详情页后访客可见。

## 5. 验证设计

后端：

1. `mvn -q -DskipTests compile`
2. PDF 渲染服务单测：构造最小 PDF，确认输出 page image URL 数量与页数一致。
3. 文件上传校验单测或编译级验证。

前端：

1. `npm run type-check`
2. `npm run build:mp-weixin`
3. 用真实 PDF 上传后检查详情页 PDF 图片页顺序和显示比例。
