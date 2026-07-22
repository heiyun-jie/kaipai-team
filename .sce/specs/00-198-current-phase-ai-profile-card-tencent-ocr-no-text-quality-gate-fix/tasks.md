# 00-198 当前阶段 AI 分享图腾讯 OCR 无文字质检修复 - 任务拆解

## T1 Spec 与根因

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [x] 记录生产任务、错误码、堆栈和生成/质检/落卡调用顺序。
- [x] 建立 requirements、design、tasks、execution。
- [x] 明确只放行精确 `FailedOperation.ImageNoText`，不关闭 OCR、不回写历史任务。

## T2 TDD 红灯

**Validates: Requirements 3.1, 3.2**

- [x] 新增 `imageNoTextResponseShouldBeAccepted()`。
- [x] 新增其他腾讯 API Error 仍失败的保护测试。
- [x] 执行定向测试并确认因缺少响应语义映射而失败。

## T3 最小实现

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 提取腾讯 OCR JSON 业务响应解释方法。
- [x] 精确 Code 映射 `ImageNoText -> accept()`。
- [x] 保持文字拦截、UnOpenError 和其他 Error 行为不变。

## T4 验证与审查

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 定向 inspector 测试通过。
- [x] inspector + service 相关测试通过。
- [x] clean package 通过。
- [x] 执行 diff/security review，确认没有扩大放行范围。

## T5 生产发布

**Validates: Requirements 3.5**

- [x] 确认生产发布 browser-smoke 偏差、host 和 `kaipai_prod` 门禁。
- [x] 复用标准 backend-only precheck/build/upload/helper 链路发布并生成偏差 release record。
- [x] 回读运行态、JAR SHA、API/browser smoke 和日志。

## T6 真实用户验收

**Validates: Requirements 3.3, 3.4, 3.5**

- [x] `userId=4` 创建发布后的新任务。
- [x] 新任务 status=success、generated_image_url/share_card_id 非空。
- [x] 分享卡和演员卡配置关联存在。
- [x] 生成图 URL 可访问。
- [x] 回填 execution、README 和 spec-code-mapping 最终状态。
