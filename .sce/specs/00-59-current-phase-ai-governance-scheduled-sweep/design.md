# 00-59 设计说明

## 1. 设计原则

- 调度必须内建在后端服务内部，不允许借道外部 crontab
- 继续复用既有 `governance-sweep` 规则实现，不复制规则代码
- 默认安全优先：未显式启用前不自动执行
- 自动动作继续纳入现有失败样本时间线与操作日志审计

## 2. 设计策略

### 2.1 调度配置模型

新增一组后端配置：

- `enabled`
- `initial-delay`
- `fixed-delay`
- `limit`
- `lock-ttl`
- `reason`

其中：

- `enabled=false` 作为默认值，避免本地和未准备环境自动改写真实失败样本
- `fixed-delay` 负责控制 sweep 间隔
- `limit` 负责约束单轮处理规模
- `lock-ttl` 负责多实例互斥锁超时释放
- `reason` 作为默认审计说明，落到自动动作时间线和操作日志

### 2.2 调度执行链

调度链路统一为：

1. `@Scheduled` 任务按配置触发
2. 先尝试获取 Redis 互斥锁
3. 生成本轮统一 `requestId`
4. 组装 `AdminAiResumeGovernanceSweepRequestDTO`
5. 调用现有 `executeGovernanceSweep(...)`
6. 复用既有 `auto_remind / timeout_escalation` 写库、时间线和审计逻辑
7. 释放互斥锁并输出运行日志

### 2.3 系统操作者口径

当前手动 `execute` 依赖后台登录管理员上下文。

为兼容定时任务，本轮把治理 sweep 的执行操作者口径扩成两类：

- 有后台会话时：沿用当前管理员
- 无后台会话时：退回固定 `system` 操作者

这样既不要求调度任务伪造后台登录态，也不会让失败样本 `handledByAdmin*` 为空。

### 2.4 审计归并

当前 `AdminOperationLogger` 在没有 HTTP 请求时会为每条日志生成随机 `requestId`。

为保证同一轮定时 sweep 的自动动作可以归并回看，本轮增加：

- `AdminOperationLogCommand.requestId`
- `AdminAiResumeGovernanceSweepRequestDTO.requestId`

调度入口会先生成一次 sweep 级 `requestId`，再让本轮所有 `auto_remind / timeout_escalation` 复用同一标识写入审计。

### 2.5 防重入

为了避免多实例或重复触发同时执行同一轮治理 sweep，本轮使用 Redis 互斥锁：

- 加锁：`SET NX EX`
- 解锁：仅当锁值仍为当前实例 token 时才删除
- 兜底：即使实例异常退出，也由 `lock-ttl` 自动释放

## 3. 影响文件

- `kaipaile-server/src/main/java/com/kaipai/KaipaiApplication.java`
- `kaipaile-server/src/main/java/com/kaipai/common/auth/AdminOperationLogCommand.java`
- `kaipaile-server/src/main/java/com/kaipai/common/auth/AdminOperationLogger.java`
- `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AdminAiResumeGovernanceSweepRequestDTO.java`
- `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AdminAiResumeGovernanceSweepResultDTO.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/config/AiResumeGovernanceSchedulerProperties.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/job/AiResumeGovernanceSweepScheduler.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AdminAiResumeGovernanceServiceImpl.java`
- `kaipaile-server/src/main/resources/application.yml`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`

## 4. 验证策略

- 编译验证：`kaipaile-server mvn -q -DskipTests compile`
- 代码级验证点：
  - 未显式启用时，调度任务不会执行治理动作
  - 调度任务会复用既有 `executeGovernanceSweep(...)`
  - 同一轮 sweep 自动动作可通过同一 `requestId` 归并
  - 互斥锁未获取时，本轮任务直接跳过

## 5. 后续边界

- `00-59` 只负责“如何稳定触发现有服务端治理规则”
- 真实通知发送 / 回执事实继续由 `00-50` 负责
- 目标环境启用、发布、smoke 与证据留存仍要继续走 `00-29` 标准发布流程
