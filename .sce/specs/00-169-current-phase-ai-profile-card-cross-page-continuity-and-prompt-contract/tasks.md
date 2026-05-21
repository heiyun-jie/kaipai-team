# AI 分享图跨页连续生图与中文 prompt 契约 Tasks

## Phase 1: Spec Creation

- [x] 创建本 spec，收口跨页连续生图与中文 prompt 契约。
- [x] 明确 `cover -> resume -> gallery` 必须使用上一页尾部参考带进行接续。
- [x] 明确 prompt 采用中文为主、英文短约束尾收口的写法。
- [x] 明确本 spec 为文档与契约层，不直接改业务代码。

## Phase 2: 连续性链路设计

- [x] 定义上一页尾部参考带的裁切比例与存储方式。
- [x] 定义 `cover` 到 `resume` 的参考带输入契约。
- [x] 定义 `resume` 到 `gallery` 的参考带输入契约。
- [x] 定义连续性失败时的降级状态与重试策略。

## Phase 3: Prompt 语言与 provider 适配

- [x] 设计中文主 prompt 模板。
- [x] 固化短英文硬约束尾。
- [x] 收敛 Tencent 混元的 prompt 组织方式，避免长英文说明和内部实现细节泄漏。
- [x] 为后续 provider 适配保留同一套逻辑契约。

## Phase 4: 持久化与审计

- [x] 定义页面级连续性元数据的持久化字段。
- [x] 定义页面级 prompt 与参考带的可追溯记录方式。
- [x] 定义 QA 需要检查的截图和白盒字段。

## Phase 5: 自动化验证

- [ ] 补充三页连续性 E2E 检查点。
- [x] 补充 prompt 文本审查检查点。
- [ ] 补充 `cover / resume / gallery` 接缝截图验证。

## Phase 6: Acceptance Criteria

- [ ] `cover -> resume -> gallery` 的接续点可从截图中确认。
- [x] prompt 中文可读，英文约束尾固定且短。
- [x] 连续性参考来自上一页尾部裁片，不是整页复用。
- [x] OCR 不是主要控制路径。
- [x] 旧的三页资料册与旧 artifact 仍然可用。

## Current Status

- 本 spec 已完成 backend 侧实现与定向单测验证，固定三页 `cover -> resume -> gallery` 的连续生图链路已接通。
- 当前实现已落地中文主 prompt、短英文硬约束尾、页面连续性元数据和连续性 reference band 裁切上传。
- `mvn -q -DskipTests compile` 与定向单测已通过；H5 / 小程序截图级 E2E 验证仍待后续执行。
