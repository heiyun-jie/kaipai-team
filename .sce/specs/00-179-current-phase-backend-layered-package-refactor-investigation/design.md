# 当前阶段后端分层包结构重构调查 - 技术设计

## 1. 设计结论

本轮采用“调查文档接管 + 新包结构门禁 + 后续治理清单”的方式承接后端远端重构。

```text
旧结构：com.kaipai.module.*
  -> 新结构：com.kaipai.controller / service / model / mapper / integration
  -> 本轮：只沉淀 SCE 文档和索引，不迁移业务代码
  -> 后续：按新结构迁移旧本地改动，并更新 stale agent 文档
```

本 Spec 的交付物是文档，不创建兼容层，不恢复旧包，不修改运行时代码。

_Requirements: 3.1, 3.2, 3.6_

## 2. 调查范围

后端仓库：`kaipaile-server`

重构范围：

```text
670aeed feat: integrate Tencent realname verification
  -> bd598a0 修改
```

关键事实：

- `534 files changed, 3955 insertions(+), 1942 deletions(-)`
- 旧 `src/main/java/com/kaipai/module/*` 到新包根的 rename 记录为 `472` 条。
- 当前源码树中 `src/main/java/com/kaipai/module` 下 Java 文件数为 `0`。
- `mvn -q -DskipTests compile` 已通过。

_Requirements: 3.1, 3.6_

## 3. 新分层职责

| 包根 | 当前职责 | 例子 |
|------|----------|------|
| `com.kaipai.controller.admin` | 后台管理端接口 | 后台用户、角色、系统设置、运营治理 |
| `com.kaipai.controller.api` | 小程序 / C 端 API 接口 | `actor`、`auth`、`card`、`verify` |
| `com.kaipai.service` | 业务服务接口、实现、领域内 support | `service/actor`、`service/verify` |
| `com.kaipai.model` | DTO、entity、业务数据模型 | `model/actor`、`model/verify` |
| `com.kaipai.mapper` | MyBatis Mapper 接口 | `mapper/actor`、`mapper/verify` |
| `com.kaipai.integration` | 第三方供应商、外部系统、基础设施适配 | `integration/verify`、`integration/sms`、`integration/wechat`、`integration/storage` |
| `com.kaipai.common` | 跨域通用配置、工具、异常和基础组件 | `common/config`、`common/util` |

当前包根 Java 文件数：

| 包根目录 | Java 文件数 |
|----------|-------------|
| `common` | 23 |
| `controller` | 36 |
| `integration` | 36 |
| `mapper` | 39 |
| `model` | 250 |
| `module` | 0 |
| `service` | 127 |

_Requirements: 3.1_

## 4. 迁移映射

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/main/java/com/kaipai/module/controller/admin/*` | `src/main/java/com/kaipai/controller/admin/*` | 后台管理接口保留 admin 语义 |
| `src/main/java/com/kaipai/module/controller/{domain}/*` | `src/main/java/com/kaipai/controller/api/{domain}/*` | 小程序 / C 端接口统一进入 `controller/api` |
| `src/main/java/com/kaipai/module/server/{domain}/service/*` | `src/main/java/com/kaipai/service/{domain}/*` | 业务 service 从 server 层脱出 |
| `src/main/java/com/kaipai/module/server/{domain}/service/impl/*` | `src/main/java/com/kaipai/service/{domain}/impl/*` | service 实现同步迁移 |
| `src/main/java/com/kaipai/module/server/{domain}/support/*` | `src/main/java/com/kaipai/service/{domain}/support/*` 或 `src/main/java/com/kaipai/integration/{domain}/*` | 纯业务 support 进 service，供应商 support 进 integration |
| `src/main/java/com/kaipai/module/server/{domain}/mapper/*` | `src/main/java/com/kaipai/mapper/{domain}/*` | Mapper 独立为顶层包 |
| `src/main/java/com/kaipai/module/model/{domain}/*` | `src/main/java/com/kaipai/model/{domain}/*` | DTO / entity 独立为顶层包 |
| `src/main/java/com/kaipai/module/server/verify/realname/*` | `src/main/java/com/kaipai/integration/verify/*` | 实名供应商与加密支撑进入 integration |
| `src/main/java/com/kaipai/module/server/auth/sms/*` | `src/main/java/com/kaipai/integration/sms/*` | 短信供应商进入 integration |
| `src/main/java/com/kaipai/module/server/wechat/*` | `src/main/java/com/kaipai/integration/wechat/*` | 微信开放能力进入 integration |
| `src/main/java/com/kaipai/common/util/CosUtil.java` | `src/main/java/com/kaipai/integration/storage/CosUtil.java` | COS 存储适配进入 integration |
| `src/main/java/com/kaipai/common/controller/FileController.java` | `src/main/java/com/kaipai/controller/api/file/FileController.java` | 文件接口归入 C 端 API 控制器 |

迁移旧本地改动时，应先按表定位新路径，再手动搬移代码差异。

_Requirements: 3.2, 3.4_

## 5. 运行配置变化

`KaipaiApplication.java` 当前 Mapper 扫描：

```java
@MapperScan("com.kaipai.mapper.**")
```

`application.yml` 当前 MyBatis-Plus 类型别名：

```yaml
mybatis-plus:
  type-aliases-package: com.kaipai.model.**.entity
```

腾讯云配置已出现顶层 `tencent` 配置块：

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

`kaipai.sms` 与 `kaipai.realname` 仍保留各自 provider 配置，现阶段不把二者合并为同一业务配置。

_Requirements: 3.1, 3.3_

## 6. 腾讯云实名模块新落点

`00-178` 的实名能力在当前结构下已迁移为：

| 能力 | 当前路径 |
|------|----------|
| 小程序实名提交控制器 | `src/main/java/com/kaipai/controller/api/verify/VerifyController.java` |
| 实名业务状态机 | `src/main/java/com/kaipai/service/verify/*` |
| 实名 DTO / entity | `src/main/java/com/kaipai/model/verify/*` |
| 实名 Mapper | `src/main/java/com/kaipai/mapper/verify/*` |
| 身份证加密 / hash / 脱敏 | `src/main/java/com/kaipai/integration/verify/IdCardCryptoSupport.java` |
| 人工 provider | `src/main/java/com/kaipai/integration/verify/ManualRealNameVerificationProvider.java` |
| provider 路由 | `src/main/java/com/kaipai/integration/verify/RoutingRealNameVerificationProvider.java` |
| 腾讯云 provider | `src/main/java/com/kaipai/integration/verify/TencentRealNameVerificationProvider.java` |
| 腾讯云二要素客户端 | `src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationClient.java` |

当前 `integration/verify` 下共有：

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

_Requirements: 3.3_

## 7. 本地 stash 迁移策略

当前后端存在两个 stash：

```text
stash@{0}: codex-pre-pull-actor-profile-local-work-20260601
stash@{1}: codex-pre-pull-target-artifacts-20260601
```

`stash@{0}` 是 actor profile 相关本地工作，旧路径包括：

```text
src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java
src/main/java/com/kaipai/module/model/actor/dto/ActorProfilePdfResumeSaveDTO.java
src/main/java/com/kaipai/module/server/actor/service/ActorProfileService.java
src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java
src/main/java/com/kaipai/module/server/actor/support/ActorProfileTextEncodingGuard.java
src/test/java/com/kaipai/module/server/actor/support/ActorProfileTextEncodingGuardTest.java
```

对应新路径应先人工定位为：

```text
src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java
src/main/java/com/kaipai/model/actor/dto/ActorProfilePdfResumeSaveDTO.java
src/main/java/com/kaipai/service/actor/ActorProfileService.java
src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java
src/main/java/com/kaipai/service/actor/support/ActorProfileTextEncodingGuard.java
src/test/java/com/kaipai/service/actor/support/ActorProfileTextEncodingGuardTest.java
```

本轮不恢复该 stash。后续需要恢复时，应先查看 stash diff，再按新路径手工移植。

_Requirements: 3.4_

## 8. Agent 文档后续治理

后端新增的 `.agents/*.md` 仍有旧路径引用。当前已发现以下文件包含 `src/main/java/com/kaipai/module` 或 `module/server`：

```text
kaipaile-server/.agents/admin-operations-agent.md
kaipaile-server/.agents/ai-governance-agent.md
kaipaile-server/.agents/auth-security-agent.md
kaipaile-server/.agents/backend-conventions.md
kaipaile-server/.agents/project-architect.md
kaipaile-server/.agents/recruit-transaction-agent.md
kaipaile-server/.agents/talent-profile-agent.md
```

这些文件是后续治理对象。本轮不直接修改，避免把“重构调查”扩大为 agent 文档批量改造。

_Requirements: 3.5_

## 9. 验证设计

本 Spec 的验证分三类：

1. 文档完整性：
   - `requirements.md`
   - `design.md`
   - `tasks.md`
   - `execution.md`
   - `refactor-audit.md`
2. 索引完整性：
   - `.sce/specs/README.md` 登记 `00-179`
3. 事实复核：
   - `git -C kaipaile-server diff --shortstat 670aeed..bd598a0`
   - `git -C kaipaile-server diff --name-status 670aeed..bd598a0`
   - `Get-ChildItem kaipaile-server/src/main/java/com/kaipai`
   - `cd kaipaile-server && mvn -q -DskipTests compile`

_Requirements: 3.6_

## 10. 非目标

- 不迁移 `stash@{0}` 中的 actor profile 本地代码。
- 不修改 `.agents/*.md`。
- 不修改后端业务代码、前端代码或后台代码。
- 不处理 `target/classes` dirty 产物。
- 不重新验证腾讯云真实实名 API。腾讯云 provider 级 smoke 已由 `00-178` 记录。
