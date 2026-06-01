# 当前阶段后端分层包结构重构调查文档

## 1. 摘要

本次后端远端更新不是局部修复，而是一次全仓级 Java 包结构重构。

核心变化：

- 旧业务主目录 `src/main/java/com/kaipai/module` 已退出当前源码运行态。
- 后端按职责拆成顶层 `controller`、`service`、`model`、`mapper`、`integration`。
- 管理端接口和小程序 API 控制器被拆到不同入口。
- 第三方供应商能力从业务 service 包中抽出，集中到 `integration`。
- MyBatis MapperScan 和 type aliases 已切到新包。
- `00-178` 腾讯云实名二要素接入也已随重构迁移到新 `integration/verify` 结构。

本轮调查结论：后续后端开发必须以新分层结构为准，不应继续创建或恢复 `com.kaipai.module.*` Java 文件。

## 2. 变更范围

对比范围：

```text
670aeed feat: integrate Tencent realname verification
  -> bd598a0 修改
```

提交列表：

```text
bd598a0 修改
7225ac8 修改
a365f69 Merge branch 'master' of https://github.com/yinuocarl-droid/kaipaile-server
69df743 修改
```

规模：

```text
534 files changed, 3955 insertions(+), 1942 deletions(-)
```

旧 `module` 路径 rename：

```text
472
```

这说明本次不是“新增几个文件”，而是后端源代码主结构调整。

## 3. 当前源码结构

当前 `src/main/java/com/kaipai` 下 Java 文件数：

| 包根 | Java 文件数 | 判断 |
|------|-------------|------|
| `common` | 23 | 保留通用基础层 |
| `controller` | 36 | 新控制器入口 |
| `integration` | 36 | 新外部集成入口 |
| `mapper` | 39 | 新 Mapper 入口 |
| `model` | 250 | 新 DTO / entity 入口 |
| `module` | 0 | 旧结构已退出 |
| `service` | 127 | 新业务服务入口 |

### 3.1 Controller

控制器拆成：

```text
src/main/java/com/kaipai/controller/admin
src/main/java/com/kaipai/controller/api
```

含义：

- `controller/admin`：后台管理端接口。
- `controller/api`：小程序 / C 端 API 接口。

示例：

```text
src/main/java/com/kaipai/module/controller/verify/VerifyController.java
  -> src/main/java/com/kaipai/controller/api/verify/VerifyController.java

src/main/java/com/kaipai/common/controller/FileController.java
  -> src/main/java/com/kaipai/controller/api/file/FileController.java
```

### 3.2 Service

业务服务从旧 `module/server/{domain}/service` 移到：

```text
src/main/java/com/kaipai/service/{domain}
```

示例：

```text
src/main/java/com/kaipai/module/server/actor/service/ActorProfileService.java
  -> src/main/java/com/kaipai/service/actor/ActorProfileService.java

src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java
  -> src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java
```

### 3.3 Model

DTO / entity 从旧 `module/model/{domain}` 移到：

```text
src/main/java/com/kaipai/model/{domain}
```

示例：

```text
src/main/java/com/kaipai/module/model/actor/*
  -> src/main/java/com/kaipai/model/actor/*

src/main/java/com/kaipai/module/model/verify/*
  -> src/main/java/com/kaipai/model/verify/*
```

### 3.4 Mapper

Mapper 从旧 service 内部目录移到顶层：

```text
src/main/java/com/kaipai/mapper/{domain}
```

运行态扫描也已同步为：

```java
@MapperScan("com.kaipai.mapper.**")
```

### 3.5 Integration

第三方供应商、外部系统和存储能力从旧业务包抽出到：

```text
src/main/java/com/kaipai/integration
```

当前子目录：

```text
ai
sms
storage
verify
wechat
```

这意味着：

- 腾讯云实名不再属于 `module/server/verify/realname`。
- 腾讯云短信不再属于 `module/server/auth/sms`。
- 微信能力不再属于 `module/server/wechat`。
- COS 存储不再属于 `common/util`。

## 4. 迁移规则

| 旧路径模式 | 新路径模式 | 迁移原则 |
|------------|------------|----------|
| `module/controller/admin/*` | `controller/admin/*` | 管理端 API |
| `module/controller/{domain}/*` | `controller/api/{domain}/*` | 小程序 / C 端 API |
| `module/server/{domain}/service/*` | `service/{domain}/*` | 业务 service |
| `module/server/{domain}/service/impl/*` | `service/{domain}/impl/*` | 业务 service 实现 |
| `module/server/{domain}/mapper/*` | `mapper/{domain}/*` | MyBatis Mapper |
| `module/model/{domain}/*` | `model/{domain}/*` | DTO / entity |
| `module/server/verify/realname/*` | `integration/verify/*` | 实名供应商和加密支撑 |
| `module/server/auth/sms/*` | `integration/sms/*` | 短信供应商 |
| `module/server/wechat/*` | `integration/wechat/*` | 微信开放能力 |
| `common/util/CosUtil.java` | `integration/storage/CosUtil.java` | COS 存储适配 |

人工迁移旧改动时，不应只做字符串替换。需要先判断旧 `support` 是领域业务 support 还是供应商 support：

- 领域业务 support 放入 `service/{domain}/support`。
- 供应商 / 外部 API support 放入 `integration/{provider-or-domain}`。

## 5. 运行配置变化

### 5.1 MapperScan

当前入口：

```java
@MapperScan("com.kaipai.mapper.**")
```

旧入口 `com.kaipai.module.server.**.mapper` 不再是当前运行态。

### 5.2 MyBatis aliases

当前配置：

```yaml
mybatis-plus:
  type-aliases-package: com.kaipai.model.**.entity
```

旧配置 `com.kaipai.module.model.**.entity` 不再是当前运行态。

### 5.3 腾讯云配置

当前配置同时存在顶层 `tencent` 与业务级 `kaipai.sms` / `kaipai.realname`：

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

注意：

- 文档和代码中不得写入真实 SecretId / SecretKey。
- `TENCENT_FACEID_ENABLED` 是顶层 faceid 开关。
- `KAIPAI_REALNAME_PROVIDER_CODE` 仍控制实名 provider 路由。

## 6. 实名接入影响

`00-178` 的腾讯云身份证二要素接入已随本次重构迁移。

### 6.1 入口

```text
src/main/java/com/kaipai/controller/api/verify/VerifyController.java
```

旧路径：

```text
src/main/java/com/kaipai/module/controller/verify/VerifyController.java
```

### 6.2 Provider

当前路径：

```text
src/main/java/com/kaipai/integration/verify
```

当前文件：

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

### 6.3 维护结论

以后排查实名认证：

1. 接口路由先看 `controller/api/verify`。
2. 状态机先看 `service/verify`。
3. DTO / entity 先看 `model/verify`。
4. Mapper 先看 `mapper/verify`。
5. 腾讯云 provider、身份证加密、供应商返回解析先看 `integration/verify`。

## 7. 本地改动影响

### 7.1 当前 stash

```text
stash@{0}: On master: codex-pre-pull-actor-profile-local-work-20260601
stash@{1}: On master: codex-pre-pull-target-artifacts-20260601
```

`stash@{0}` 是 pull 前 actor profile 本地工作。它基于旧 `module` 路径，不能直接作为当前结构恢复。

### 7.2 推荐迁移目标

| 旧 stash 路径 | 新目标路径 |
|---------------|------------|
| `module/controller/actor/ActorProfileController.java` | `controller/api/actor/ActorProfileController.java` |
| `module/model/actor/dto/ActorProfilePdfResumeSaveDTO.java` | `model/actor/dto/ActorProfilePdfResumeSaveDTO.java` |
| `module/server/actor/service/ActorProfileService.java` | `service/actor/ActorProfileService.java` |
| `module/server/actor/service/impl/ActorProfileServiceImpl.java` | `service/actor/impl/ActorProfileServiceImpl.java` |
| `module/server/actor/support/ActorProfileTextEncodingGuard.java` | `service/actor/support/ActorProfileTextEncodingGuard.java` |
| `src/test/java/com/kaipai/module/server/actor/support/ActorProfileTextEncodingGuardTest.java` | `src/test/java/com/kaipai/service/actor/support/ActorProfileTextEncodingGuardTest.java` |

恢复建议：

1. 用 `git stash show -p 'stash@{0}'` 查看具体差异。
2. 在新路径中手工 port。
3. 编译和对应测试通过后再删除 stash。
4. 不要直接 `git stash pop` 让 Git 自动恢复旧目录。

## 8. Agent 文档风险

后端新增 agent 文档仍引用旧路径：

```text
kaipaile-server/.agents/admin-operations-agent.md
kaipaile-server/.agents/ai-governance-agent.md
kaipaile-server/.agents/auth-security-agent.md
kaipaile-server/.agents/backend-conventions.md
kaipaile-server/.agents/project-architect.md
kaipaile-server/.agents/recruit-transaction-agent.md
kaipaile-server/.agents/talent-profile-agent.md
```

风险：

- 后续如果按这些文档分派任务，可能把新代码写回旧 `module` 路径。
- `backend-conventions.md` 中“业务目录主要在 `src/main/java/com/kaipai/module`”已经与当前源码事实冲突。
- `auth-security-agent.md` 中实名 / 短信模块路径仍描述为 `module/server/*`，与当前 `integration/*` 冲突。

建议后续单独开治理任务：

```text
00-180-current-phase-backend-agent-docs-package-path-alignment
```

该任务只更新 `.agents` 文档，不应混入业务代码修改。

## 9. 验证结果

已执行后端编译：

```text
cd kaipaile-server
mvn -q -DskipTests compile
```

结果：

```text
通过
```

已知副作用：

```text
M target/classes/application.yml
M target/classes/com/kaipai/KaipaiApplication.class
```

判断：

- 这是 Maven 编译产生的 tracked build artifact dirty。
- 不属于本次 SCE 文档变更。
- 不应随文档提交。

## 10. 后续门禁

后续后端开发前，应执行：

```text
Get-ChildItem -Path 'kaipaile-server/src/main/java/com/kaipai/module' -Recurse -Filter '*.java'
```

期望：

```text
无输出
```

后续 review 中如出现以下情况，应要求回退或重做：

- 新增 `src/main/java/com/kaipai/module/**/*.java`。
- `@MapperScan` 回退到 `com.kaipai.module.server.**.mapper`。
- `mybatis-plus.type-aliases-package` 回退到 `com.kaipai.module.model.**.entity`。
- 腾讯云实名 provider 又写回 `service/verify/realname` 或旧 `module/server/verify/realname`。
- `.agents` 文档继续指导新任务写入旧路径。
