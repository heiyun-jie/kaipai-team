# 00-52 执行记录

## 1. 调查结论

- 现代码中的 `pkg-card/invite/index` 已经收口为邀请记录页
- `05-12` 仍把它描述成前台唯一邀请码 / 链接 / 海报 / 分享操作页
- `00-28 invite-status` 也仍残留“invite 页消费 `inviteLink / qrCodeUrl`、展示二维码降级态”的旧口径
- 后端 `/api/card/personalization` 仍直接返回 `miniProgramCard / poster / publicCardPage / inviteCard` 四种 artifact
- 名片配置保存链路 `saveActorCardConfig -> saveSharePreference` 仍会把 legacy `preferredArtifact` 原样写回偏好表
- 前端虽然已在真接口模式下过滤 legacy artifacts，但类型层和 helper 仍残留历史 artifact 分支，主事实源尚未真正统一

## 2. 本轮落地

- 新增 `00-52` Spec，正式记录 invite 当前阶段记录页边界
- 回写 `00-28` 路线图、任务、invite 切片、invite 状态卡与总体评估
- 回写 `05-12` 顶部说明，明确其为历史收口 Spec，当前阶段以 `00-52` 为准
- 后端新增 `CurrentPhaseShareArtifactSupport`，把当前阶段 artifact 单一口径固定为 `miniProgramCard / poster`
- `/api/card/personalization` 已改为只返回当前阶段两种分享产物，不再下发 `publicCardPage / inviteCard`
- `saveActorCardConfig` 保存偏好时已统一归一化 `preferredArtifact`，legacy 值会回落到 `miniProgramCard`
- 前端 `ShareArtifactType` 与 `share-artifact.ts` 已同步收口为当前阶段两种分享产物；公开名片页路径保留为独立 helper
- 完成 spec 索引与映射登记

## 3. 验证

- 本轮包含小范围运行时收口，不涉及后端或管理端发布
- 已执行 `kaipai-frontend npm run type-check`，通过
- 已执行 `kaipaile-server mvn -q -DskipTests compile`，通过
- 本机默认 Maven 运行在 JDK 8，首次 compile 因 `pom.xml` 要求 Java 17 而失败；随后切换 `JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot` 后复跑通过
- 已复核当前源码：
  - `kaipai-frontend/src/pkg-card/invite/index.vue` 只保留邀请记录与状态展示
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue` 与 `src/pkg-card/membership/index.vue` 负责分享入口和邀请记录入口
  - `kaipai-frontend/src/pages/login/index.vue` 承接 `inviteCode / scene`
  - `kaipai-frontend/src/utils/personalization.ts` 已在真接口模式下把 legacy artifacts 收口为当前阶段两种分享产物
  - `kaipai-frontend/src/types/personalization.ts` 与 `src/utils/share-artifact.ts` 当前阶段只暴露 `miniProgramCard / poster`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue` 已不再依赖后端 `publicCardPage` artifact 才能恢复公开名片分享态
  - `kaipai-frontend src/pkg-card/actor-card/index.vue` 与 `src/pkg-card/membership/index.vue` 的 invite 文案已同步改为“邀请记录页”口径
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 已只返回当前阶段两种 artifact
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 已对 `preferredArtifact` 执行当前阶段归一化

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28/tasks.md` 勾选
