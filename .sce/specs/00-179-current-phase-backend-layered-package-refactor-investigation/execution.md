# 当前阶段后端分层包结构重构调查 Execution

## 2026-06-01

### SCE 基线

- 已读取：
  - `.sce/README.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `.sce/specs/README.md`
  - `.sce/specs/SHARED_CONVENTIONS.md`
  - `00-178-current-phase-tencent-cloud-realname-two-factor-enablement`
- 当前最新已登记 Spec 为 `00-178`。
- 本轮新增 `00-179-current-phase-backend-layered-package-refactor-investigation`，用于承接本次后端包结构重构调查。

### 后端仓库状态

后端仓库：

```text
D:\XM\kaipai-team\kaipaile-server
```

当前分支与 HEAD：

```text
## master...origin/master
bd598a0 修改
7225ac8 修改
a365f69 Merge branch 'master' of https://github.com/yinuocarl-droid/kaipaile-server
69df743 修改
670aeed feat: integrate Tencent realname verification
```

当前后端仓库在 `mvn compile` 后存在编译产物 dirty：

```text
M target/classes/application.yml
M target/classes/com/kaipai/KaipaiApplication.class
```

这些文件是构建产物，不属于本 Spec 文档改动范围。

### 重构范围

对比范围：

```text
670aeed..bd598a0
```

变更规模：

```text
534 files changed, 3955 insertions(+), 1942 deletions(-)
```

旧 `module` 路径 rename 记录数：

```text
472
```

当前顶层包 Java 文件数：

```text
common      23
controller  36
integration 36
mapper      39
model      250
module       0
service    127
```

结论：

- 当前后端已从 `com.kaipai.module.*` 迁移到 `controller / service / model / mapper / integration` 分层结构。
- `src/main/java/com/kaipai/module` 在当前源码树下没有 Java 文件。
- 后续开发不应继续按旧 `module` 包落代码。

### 关键配置复核

`KaipaiApplication.java` 当前 MapperScan：

```java
@MapperScan("com.kaipai.mapper.**")
```

`application.yml` 当前 MyBatis-Plus aliases：

```yaml
mybatis-plus:
  type-aliases-package: com.kaipai.model.**.entity
```

腾讯云配置当前已存在顶层块：

```yaml
tencent:
  secret-id: ${TENCENT_CLOUD_SECRET_ID:}
  secret-key: ${TENCENT_CLOUD_SECRET_KEY:}
  faceid:
    enabled: ${TENCENT_FACEID_ENABLED:false}
    endpoint: ${TENCENT_FACEID_ENDPOINT:https://faceid.tencentcloudapi.com}
    version: ${TENCENT_FACEID_VERSION:2018-03-01}
  cos:
    region: ${TENCENT_COS_REGION:}
    bucket-name: ${TENCENT_COS_BUCKET_NAME:}
```

### 腾讯云实名模块复核

当前 `integration/verify` 文件列表：

```text
IdCardCryptoSupport.java
ManualRealNameVerificationProvider.java
RealNameVerificationCommand.java
RealNameVerificationProperties.java
RealNameVerificationProvider.java
RealNameVerificationResult.java
RoutingRealNameVerificationProvider.java
TencentIdCardVerificationClient.java
TencentIdCardVerificationProperties.java
TencentIdCardVerificationResult.java
TencentRealNameVerificationProvider.java
```

关键迁移：

```text
src/main/java/com/kaipai/module/controller/verify/VerifyController.java
  -> src/main/java/com/kaipai/controller/api/verify/VerifyController.java

src/main/java/com/kaipai/module/server/verify/realname/*
  -> src/main/java/com/kaipai/integration/verify/*
```

新增腾讯云二要素客户端：

```text
src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationClient.java
src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationProperties.java
src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationResult.java
```

结论：

- `00-178` 的实名 provider 代码已经迁移到 `integration/verify`。
- 排查小程序实名提交入口时，应从 `controller/api/verify` 和 `service/verify` 开始，而不是旧 `module/controller/verify` 或 `module/server/verify`。

### Actor 本地 stash 影响

当前后端 stash：

```text
stash@{0}: On master: codex-pre-pull-actor-profile-local-work-20260601
stash@{1}: On master: codex-pre-pull-target-artifacts-20260601
```

`stash@{0}` 保存的是 pull 前 actor profile 本地工作，基于旧路径。后续如要恢复，应人工迁移到：

```text
src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java
src/main/java/com/kaipai/model/actor/dto/ActorProfilePdfResumeSaveDTO.java
src/main/java/com/kaipai/service/actor/ActorProfileService.java
src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java
src/main/java/com/kaipai/service/actor/support/ActorProfileTextEncodingGuard.java
src/test/java/com/kaipai/service/actor/support/ActorProfileTextEncodingGuardTest.java
```

本轮没有 pop 或 apply 任何 stash。

### Agent 文档旧路径

已发现以下后端 agent 文档仍引用旧 `module` 路径：

```text
kaipaile-server/.agents/admin-operations-agent.md
kaipaile-server/.agents/ai-governance-agent.md
kaipaile-server/.agents/auth-security-agent.md
kaipaile-server/.agents/backend-conventions.md
kaipaile-server/.agents/project-architect.md
kaipaile-server/.agents/recruit-transaction-agent.md
kaipaile-server/.agents/talent-profile-agent.md
```

本轮只记录该风险，后续应单独治理。

### 验证记录

已执行：

```text
cd kaipaile-server
mvn -q -DskipTests compile
```

结果：

```text
通过
```

收尾复核已再次执行同一命令，退出码为 `0`。

副作用：

- `target/classes/application.yml` dirty。
- `target/classes/com/kaipai/KaipaiApplication.class` dirty。

这些 dirty 是编译产物，不纳入本 Spec。

### 当前根目录无关状态

根仓库当前已有无关未跟踪文件：

```text
.sce/specs/05-14-actor-profile-mojibake-recovery-guard/
backend-tencent-stderr.log
backend-tencent-stdout.log
```

本轮不触碰这些文件。

## 2026-06-01 后续文档对齐

- 已创建并执行 `00-180-current-phase-backend-docs-package-path-alignment`。
- 已更新 `kaipaile-server/AGENTS.md` 与 `kaipaile-server/.agents/*.md`，后端 agent 活文档不再把旧 `module` 路径作为当前目录。
- 已更新 `.sce/steering/CURRENT_CONTEXT.md` 与 `.sce/specs/spec-code-mapping.md`，当前事实源增加后端包结构迁移说明。
- 已为 `00-176 / 00-177 / 00-178` 追加迁移后当前路径注记；历史执行路径保留为当时记录。
