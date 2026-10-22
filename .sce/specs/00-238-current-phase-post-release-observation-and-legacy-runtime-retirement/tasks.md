# 00-238 发布后观察与旧运行时退场 - 任务拆解

## T1 观察启动

- [ ] 启动观察窗口和指标采集。
- [ ] 记录正式 API、后台和容器基线。
- [ ] 验证测试环境仍独立可用。

**Validates: Requirements 3.1**

## T2 发布后回归

- [ ] 验证历史账号和旧分享。
- [ ] 验证新账号核心写入和公开页。
- [ ] 验证后台、Nacos、Redis、COS 和数据库无回归。

**Validates: Requirements 3.2**

## T3 异常和回切

- [ ] 固化 P0/P1 自动回切条件。
- [ ] 演练或验证旧 upstream 回切路径。
- [ ] 证明回切不覆盖新 Schema/新写入。
- [ ] 准备小程序版本回退方案。

**Validates: Requirements 3.3, 3.4**

## T4 旧运行时退场

- [ ] 检查观察窗口、缺陷和备份清单。
- [ ] 获取停止旧容器明确同意。
- [ ] 停止旧生产容器，保留可重启资源。
- [ ] 确认测试双环境继续可用。

**Validates: Requirements 3.5**

## T5 批次关闭

- [ ] 生成观察/回切/退场记录和 SHA256。
- [ ] 输出 `STABLE / ROLLED_BACK / EXTENDED_OBSERVATION`。
- [ ] 更新 00-230 总控和风险登记。

**Validates: Requirements 3.6**

## 当前状态

- [x] Spec 三件套已创建。
- [ ] 实施未开始，旧生产运行时保持不变。
