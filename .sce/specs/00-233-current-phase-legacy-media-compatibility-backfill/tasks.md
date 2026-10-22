# 00-233 历史媒体数据兼容回填 - 任务拆解

## T1 数据盘点与模型

- [ ] 确认四类历史来源的真实列和 JSON 格式。
- [ ] 固化 URL 规范化、host allowlist 和 sourceKey 算法。
- [ ] 新增幂等 migration map 表设计及测试。

**Validates: Requirements 3.1, 3.4**

## T2 Dry-run 工具

- [ ] 实现只读扫描、解析、去重和对象检查。
- [ ] 输出 PII-free 聚合和异常清单。
- [ ] 验证 dry-run 对 DB/COS 零写入。

**Validates: Requirements 3.1, 3.2, 3.6**

## T3 Apply 工具

- [ ] 实现 test/prod bucket 硬隔离。
- [ ] 实现稳定对象 key、复制和复用。
- [ ] 创建 asset、头像字段和照片/视频关系。
- [ ] 实现逐项状态和断点续跑。

**Validates: Requirements 3.2, 3.3, 3.4**

## T4 兼容测试

- [ ] 验证旧字段字节不变。
- [ ] 验证新 UI 可读、新旧客户端合同可用。
- [ ] 验证重跑创建数为 0。
- [ ] 验证删除新素材不会触碰原公有对象。

**Validates: Requirements 3.4, 3.5**

## T5 阶段签收

- [ ] 保存 dry-run/apply/重跑证据及 SHA256。
- [ ] 输出未迁移异常清单和 `GO / NO-GO`。
- [ ] 回填 `00-230 execution-plan.md`。

**Validates: Requirements 3.6**

## 当前状态

- [x] Spec 三件套已创建。
- [ ] 实施未开始。
