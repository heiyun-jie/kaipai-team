# AI 生成分享图分析图必填上传 Tasks

## Phase 1: Spec

- [x] 建立 `05-15` Spec。
- [x] 完成现有前端、上传工具与后端 `sourceImageUrl` 合同相关性分析。

## Phase 2: Test First

- [x] 增加最小静态验收脚本，校验 `ai-profile-card/index.vue` 必须包含分析图上传 UI、上传状态、必填门禁与 `sourceImageUrl` 提交。
- [x] 在当前实现上运行脚本，确认失败。

## Phase 3: Implementation

- [x] 修改 `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue`，新增分析图上传模块。
- [x] 接入 `chooseImageFiles` 与 `uploadImage`。
- [x] 上传前校验当前演员档案存在，避免用空字段创建半成品档案。
- [x] 上传成功后同步写入演员档案照片池，满足后端 `sourceImageUrl` 候选图校验。
- [x] 在 `handleGenerate` 中增加上传中 / 未上传门禁，并提交 `sourceImageUrl`。

## Phase 4: Verification

- [x] 运行静态验收脚本并确认通过。
- [x] 运行 `cd kaipai-frontend && npm run type-check`。
- [x] 运行 `cd kaipai-frontend && npm run build:mp-weixin`。
- [x] 检查 `dist/build/mp-weixin/pkg-card/ai-profile-card/index.*`。
- [x] 检查 `dist/dev/mp-weixin/pkg-card/ai-profile-card/index.*`。
- [x] 运行 `cd kaipai-frontend && npm run audit:steering`。
- [x] 运行 `cd kaipai-frontend && npm run audit:mp-package`。
