# AI 生成分享图分析图必填上传 Execution

## 2026-06-10

### 1. 相关性分析

已确认：

- 目标页面为 `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue`。
- 当前生成 payload 类型 `AiProfileCardGeneratePayload` 已有 `sourceImageUrl?: string`。
- 当前 API `generateAiProfileCard(payload)` 会原样提交 payload。
- 当前上传工具为 `chooseImageFiles(...)` 与 `uploadImage(...)`。
- 后端 `AiProfileCardGenerateReqDTO` 已有 `sourceImageUrl`。
- 后端 `AiProfileCardServiceImpl.resolveSourceImage(...)` 已承接该字段，并会校验该图属于当前个人档案候选图。
- 因此本轮前端不能只上传图片再提交 URL；上传成功后还必须把图片同步写入演员档案照片池。

本轮实现限定为前端生成入口 UI、档案照片池同步与提交参数，不变更详情页首图排序。

### 2. 实现记录

已完成：

- `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue` 步骤条从 `风格 / 生成` 扩展为 `风格 / 分析图 / 生成`。
- 新增 `STEP 02 上传分析图` 模块，未上传时展示必填上传占位，已上传时展示缩略图、`已上传`、`更换图片` 与 `移除`。
- 上传链路复用 `chooseImageFiles(1)` 与 `uploadImage(filePath, 'photo')`。
- 上传前校验当前 `profile` 存在；若尚未建立演员档案，则提示 `请先完善演员档案后再上传分析图`，不进入图片选择 / 上传 / 档案保存。
- 上传成功后调用 `updateActorProfile(...)`，把分析图 URL 写入演员档案照片池，再刷新当前档案。
- 生成前增加上传中 / 未上传门禁；生成请求显式携带 `sourceImageUrl: analysisImageUrl.value`。
- 页面文案明确“上传图仅作为 AI 分析图，生成后的 AI 图会作为详情首图”。

### 3. 验证记录

已通过：

```powershell
node .sce\specs\05-15-ai-profile-card-source-image-required-upload\verify-ai-profile-card-source-image.mjs D:\XM\kaipai-team\kaipai-frontend
cd kaipai-frontend && npm run type-check
cd kaipai-frontend && npm run build:mp-weixin
cd kaipai-frontend && npm run audit:steering
cd kaipai-frontend && npm run audit:mp-package
```

生成产物已检查：

- `kaipai-frontend/dist/build/mp-weixin/pkg-card/ai-profile-card/index.wxml`
- `kaipai-frontend/dist/build/mp-weixin/pkg-card/ai-profile-card/index.wxss`
- `kaipai-frontend/dist/build/mp-weixin/pkg-card/ai-profile-card/index.js`
- `kaipai-frontend/dist/dev/mp-weixin/pkg-card/ai-profile-card/index.wxml`
- `kaipai-frontend/dist/dev/mp-weixin/pkg-card/ai-profile-card/index.wxss`
- `kaipai-frontend/dist/dev/mp-weixin/pkg-card/ai-profile-card/index.js`

已确认生成产物包含：

- `ai-profile-card-page__analysis-card`
- `ai-profile-card-page__analysis-empty`
- `ai-profile-card-page__analysis-preview`
- `上传分析图`
- `生成依据`
- `sourceImageUrl`
- `请先上传分析图`
- `分析图上传中，请稍后`
- `请先完善演员档案后再上传分析图`
- `syncAnalysisImageToProfile`
- `buildAnalysisImageProfilePayload`

最新包体审计结果：

| Package | Size | Limit | Status |
|---------|------|-------|--------|
| main | 521.35 KB | 2.00 MB | OK |
| pkg-card | 209.78 KB | 2.00 MB | OK |
| pkg-tools | 28.31 KB | 2.00 MB | OK |
