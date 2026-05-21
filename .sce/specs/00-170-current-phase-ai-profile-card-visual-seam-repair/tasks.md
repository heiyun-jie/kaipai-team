# AI 资料册视觉接缝与封面遮罩修复 Tasks

## Phase 0: Baseline

- [x] 提交根仓库基线：`3302e42 chore: checkpoint spec and runbook baseline`
- [x] 提交前端仓库基线：`f2308d4 fix: render generated backgrounds for all profile pages`
- [x] 提交后端仓库基线：`de39574 feat: add profile card continuity metadata flow`
- [x] 明确 `SecretKey.csv`、`output/`、临时日志、构建输出不进入本轮代码提交。

## Phase 1: Spec Creation

- [x] 创建本 spec，承接 `00-169` 的落地修复问题。
- [x] 明确封面左上白块来自前端固定遮罩。
- [x] 明确封面右下白块来自前端水印遮挡层。
- [x] 明确跨页连续性需要渲染层确定性兜底。

## Phase 2: Frontend Repair

- [x] 移除或禁用 `cover-identity-shield` 的默认渲染。
- [x] 移除或禁用 `cover-watermark-shield` 的默认渲染。
- [x] 为非 cover 页新增 continuity reference band 渲染。
- [x] 使用 `continuityBandRatio` 控制参考带高度，默认 15%，并做边界保护。
- [x] 为参考带底部增加轻量 fade，避免硬断层。
- [x] 确认 H5 类型检查通过，相关样式不使用浏览器专属能力。

## Phase 3: Backend Prompt/Data Repair

- [x] 强化 cover 底部 15% 为干净可延展背景过渡带。
- [x] 强化 resume/gallery 顶部 15% 必须接近参考带主要形状、色彩、光线、纹理和空间方向。
- [x] 确认页面 DTO 返回前端需要的 continuity 字段。
- [x] 补充或调整后端单测，覆盖新 prompt 关键语义。

## Phase 4: Flow Diagnosis

- [ ] 对真实任务检查 `cover/resume/gallery` 三页是否都有 `generatedImageUrl`。
- [ ] 如果真实任务只有一张背景，定位是历史任务、生成失败、返回字段缺失还是前端映射问题。
- [x] 明确 mock 测试与真实任务测试的区别，避免旧样本误判新实现。

## Phase 5: Verification

- [x] 后端运行 compile 与定向单测。
- [x] 前端运行 type-check。
- [x] 运行 H5 mock 截图测试，保存三页截图。
- [x] 输出封面首屏截图，验证左上和右下白块消失。
- [x] 输出两组接缝截图：`resume` 顶部沿用 `cover` 底部参考带，`gallery` 顶部沿用 `resume` 底部参考带。
- [x] 做代码审查，列出剩余风险。

## Acceptance

- [x] 封面左上无大面积浅色遮罩。
- [x] 封面右下无无条件白色遮挡。
- [x] `resume` 顶部确定性沿用 `cover` 底部参考带。
- [x] `gallery` 顶部确定性沿用 `resume` 底部参考带。
- [x] 三页截图和接缝截图证据完整保存。
- [x] 代码审查无阻断级问题。

## Remaining Follow-Up

- [ ] 需要用重新生成的新真实任务再跑一次小程序截图，确认线上/本地真实数据的 `cover/resume/gallery` 都有 `generatedImageUrl` 和 continuity 字段。
