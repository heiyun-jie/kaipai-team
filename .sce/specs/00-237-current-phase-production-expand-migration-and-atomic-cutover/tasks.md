# 00-237 正式环境扩展迁移与原子切流 - 任务拆解

## T1 生产 Go 卡与备份

- [ ] 核对 `00-236 GO` 和所有上游证据 SHA256。
- [ ] 通知窗口、记录运行摘要。
- [ ] 备份 prod DB、JAR、compose、Nginx、管理端。
- [ ] 验证备份可读和 SHA256。

**Validates: Requirements 3.1**

## T2 生产 Schema 与媒体

- [ ] 对 `kaipai_prod` 执行同一 14 migration。
- [ ] 执行 Schema/history/data assertion。
- [ ] 执行 prod media dry-run/apply/重跑。
- [ ] 确认旧字段未改变、生产 bucket 正确。

**Validates: Requirements 3.2, 3.3**

## T3 候选后端

- [ ] 启动 prod 候选端口和容器。
- [ ] 回读 profile/Nacos/schema。
- [ ] 执行健康、后台、历史账号、旧合同 smoke。
- [ ] 保存候选 JAR 和配置证据。

**Validates: Requirements 3.4**

## T4 Nginx 切流

- [ ] 备份 Nginx 配置。
- [ ] 修改 upstream/root。
- [ ] 通过 `nginx -t`。
- [ ] reload 并执行正式公网 smoke。
- [ ] 失败时回切旧 upstream。

**Validates: Requirements 3.5**

## T5 小程序 release

- [ ] 构建正式小程序 release。
- [ ] 运行专项门禁、包体审计和 URL 扫描。
- [ ] 上传/提交正式版本。
- [ ] 记录审核/发布状态。

**Validates: Requirements 3.6**

## T6 阶段签收

- [ ] 生成生产切流证据包和 SHA256。
- [ ] 输出 `CUTOVER_OK / NO-GO / ROLLED_BACK`。
- [ ] 保留旧实例并解锁 00-238 观察。

**Validates: Requirements 3.7**

## 当前状态

- [x] Spec 三件套已创建。
- [ ] 实施未开始，未执行生产迁移或切流。
