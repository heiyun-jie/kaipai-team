# share-card 当前阶段状态回填

## 1. 归属切片

- `../../00-68-current-phase-share-runtime-and-poster-capability-alignment/requirements.md`
- `../../00-68-current-phase-share-runtime-and-poster-capability-alignment/design.md`
- `../../00-68-current-phase-share-runtime-and-poster-capability-alignment/execution.md`
- `../../00-62-current-phase-minimal-share-card-mvp-alignment/requirements.md`（历史基础）
- `../../00-62-current-phase-minimal-share-card-mvp-alignment/design.md`（历史基础）
- `../execution/share-card-mvp/README.md`
- `../execution/share-card-mvp/evidence-index.md`
- `../execution/share-card-mvp/evidence-bundle-index.md`
- `../execution/share-card-mvp/release-post-checklist.md`
- `../execution/share-card-mvp/sms-capability-bridge.md`
- `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py`
- `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

## 2. 当前判定

- 回填日期：`2026-04-20`
- 当前判定：`局部完成`
- 一句话结论：`00-68` 当前阶段已完成“分享链事实源 + 海报能力口径 + 前端 active 入口 + 证据/runbook/自动总控”同轮收口；当前阻止新业务事实继续增长的主阻塞已固定为外部 DevTools 开发者授权缺失——截至 `2026-04-20 16:44:37 +0800`，最新探针 `share-card-devtools-auth-probe-r6` 仍返回 `probeResult=devtools_auth_gate`、`portCheckResult=NO_LISTENER`，因此暂不能产出新的小程序页面证据，但这已不再是 share 运行时或海报能力代码口径问题。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pages/home/index.vue` 已改为围绕“可分享卡片 / 风格模板”主入口消费真实 `/card/my-cards`
- `kaipai-frontend/src/pages/history/index.vue` 已切到后端查看历史，不再使用本地 storage 假历史
- `kaipai-frontend/src/pages/mine/index.vue` 已按 `档案信息 / 实名认证 / 已联系的列表 / 我的名片` 收口个人中心
- `kaipai-frontend/src/pkg-card/card-list/index.vue` 已支持真实建卡、移除非默认卡，并按 `cardId` 渲染持卡列表
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已承担单卡编辑、待审批联系方式处理入口与分享路径透传
- `kaipai-frontend/src/pages/actor-profile/detail.vue` 已开始按 `shareCardId` 解析公开卡、写入真实历史并走联系方式申请状态
- `kaipai-frontend/src/utils/share-card-latest.ts` 当前已把 `shareCardId -> personalization -> actor detail -> cardConfig/theme` 收口为共享 latest snapshot loader，`detail` 与 `actor-card` 不再各维护一套最新态读取链
- `00-64 current-phase-actor-card-editor-boundary-alignment` 当前已把 actor-card 页中会员 / 命理 / audience 残留、代表照片不可编辑、预览公开页入口缺失与配色闭环不清晰问题拆为独立治理入口
- `00-65 current-phase-share-card-multi-instance-refactor` 当前已把“新增分享卡片却仍复用同模板唯一实例”的问题拆为独立模型重构入口
- `kaipai-frontend/src/pages/history/index.vue`、`src/pages/contacts/index.vue` 与 `src/utils/share-artifact.ts` 已在持有 `shareCardId` 时优先生成 `shareCardId-first` 再次进入路径，不再把 `actorId + sceneKey` 作为主键级必填
- `kaipai-frontend/src/pages/home/index.vue`、`src/pkg-card/card-list/index.vue`、`src/pkg-card/fortune/index.vue` 与 `src/utils/share-card-mvp.ts` 已把“进入编辑页”收口为优先透传 `shareCardId/cardId` 的显式目标对象，不再继续按 `sceneKey` 单独定位卡片编辑态
- `kaipai-frontend/src/pages/actor-profile/detail.vue` 与 `src/pkg-card/actor-card/index.vue` 当前又已修正 `shareCardId-only` 读链：当实例主键已知时，不再冗余透传 `actorId`；公开页也会在首个个性化响应后回填真实 owner `actorId`，避免查看页绑错用户
- `kaipai-frontend/src/pages/actor-profile/detail.vue` 与 `src/pkg-card/actor-card/index.vue` 当前又已把“编辑后返回 / 保存后再次加载”的 latest-state 刷新统一收口到共享 loader，不再分别手写 `personalization + actor detail` 重新拼装逻辑
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把编辑页 path helper 收口为“实例已知时不再拼接 `actorId`”，因此首页、我的名片和命理页返回编辑的路径口径继续向实例主键统一
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把编辑页/详情页再次进入 helper 收口为联合类型，要求调用方在“`shareCardId` 实例目标”与“`actorId + sceneKey` legacy 目标”之间二选一；首页、我的名片、命理页、查看历史和已联系列表等入口已同步改成实例已知只传 `shareCardId`
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把首页 / 我的名片入口共用的“已持有卡片按 scene 查找 / 编辑目标拼装”下沉为 `buildOwnedShareCardSceneMap(...)`、`findOwnedShareCardByScene(...)` 与 `buildShareCardEditorTarget(...)`；`src/pages/home/index.vue` 与 `src/pkg-card/card-list/index.vue` 不再各自散写一版 `sceneKey` 推断
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把查看历史 / 已联系列表再次进入公开详情共用的“实例目标 / legacy 目标”判断下沉为 `buildShareCardDetailTarget(...)`；`src/pages/history/index.vue` 与 `src/pages/contacts/index.vue` 不再各自散写一版 `shareCardId` 分流
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把“当前卡片上下文”的个性化查询、联系状态/申请、查看历史写入、幸运色应用与配置保存共用分流下沉为 `buildShareCardContextTarget(...)`、`buildShareCardPersonalizationParams(...)`、`buildShareCardContactLookupParams(...)`、`buildShareCardContactApplyPayload(...)`、`buildShareCardHistoryPayload(...)`、`buildShareCardLuckyColorPayload(...)` 与 `buildShareCardConfigSaveTarget(...)`；`src/pages/actor-profile/detail.vue`、`src/pkg-card/actor-card/index.vue` 与 `src/pkg-card/fortune/index.vue` 不再各自散写一版 `shareCardId ? undefined : actorId/sceneKey`
- `kaipai-frontend/src/utils/share-card-mvp.ts` 当前又已把分享路径层共用的公开详情 query 分流下沉为 `buildShareCardDetailQueryParams(...)`；`src/utils/share-artifact.ts` 的 `buildPublicCardPath(...)` 与 `resolveShareArtifactPath(...)` 不再各自散写一版 `shareCardId ? actorId/scene 置空`
- `kaipai-frontend/src/types/level.ts` 当前又已把 `MyShareCardItem.cardId` 收紧为必填，首页与“我的名片”围绕 `cardId` 的空值 fallback 和 `configId` 兜底 key 也已同步删减，因此前端持卡列表状态层开始把“卡片实例主键始终存在”当作真实事实源
- `kaipai-frontend/src/utils/share-artifact.ts` 当前又已把分享产物 path helper 收口为“实例已知时不再拼接 `actorId/scene`”，因此分享预览与分享再进入路径也继续向 `shareCardId-only` 统一
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 当前又已把 `/card/personalization` 返回的 `artifacts.path` 同步收口为“实例已知时不再拼接 `actorId/scene`”，因此后端聚合结果本身也不再继续向前端扩散 legacy 主键
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 当前又已把持卡实例的场景选择收口为“实例已知时强制认当前卡片的 `sceneKey`”，因此已拥有的风格卡不会因为后台后续调高门槛而在个性化读链里被误回退到其它场景
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 当前又已修正 `shareCardId-only` 编辑页读链：会先用实例主键解析真实 owner，再加载档案，不再因为缺少 URL `actorId` 而回退到当前登录用户自己
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java`、`ActorCardConfigServiceImpl.java` 与 `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已把 `/card/config` 配置读写推进到 `shareCardId-first`，编辑页保存配置时会显式绑定当前卡片实例
- `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/ActorCardConfigSaveDTO.java`、`ActorCardConfigServiceImpl.java` 与 `kaipai-frontend/src/pkg-card/actor-card/index.vue` 当前又已把配置保存门禁进一步放宽为“`shareCardId` 或 `actorId + sceneKey` 至少一组”，因此编辑页在已知卡片实例时不再继续把 `actorId` 当成主写链必填
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 当前又已把配置读取与持卡列表组装推进到 `latest_config_id-first`，因此编辑态、持卡列表和配置回写开始围绕同一条实例配置记录对齐
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 与 `UserShareCardServiceImpl.java` 当前又已把“同场景 latest config”从长期猜测降级为一次性回填来源：当 `user_share_card.latest_config_id` 缺失、失效或元数据不齐时，当前只会临时回查一次同场景 latest，并立刻回绑 `latest_config_id`，不再持续裸读 scene 级 latest
- `kaipaile-server/src/main/resources/db/migration/V20260405_007__actor_share_preference_share_card_id.sql`、`ActorSharePreference.java`、`ActorCardConfigServiceImpl.java` 与 `ActorPersonalizationServiceImpl.java` 当前又已把分享偏好从 `userId + sceneKey` 推进到 `shareCardId-first`：偏好表已补 `share_card_id`，保存与读取都会优先围绕真实卡片实例，命中旧偏好记录时也会被动回填 `share_card_id`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 与 `ActorPersonalizationServiceImpl.java` 当前又已把 legacy `actorId + sceneKey` 入口推进到“先解析真实 `UserShareCard` 再继续执行”：旧 `actorConfig` / `personalization` / 配置保存入口在仍能映射到真实持卡实例时，会自动补出 `shareCardId`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java`、`UserShareCardServiceImpl.java`、`ActorCardConfigServiceImpl.java`、`ActorPersonalizationServiceImpl.java`、`ShareCardContactRequestServiceImpl.java` 与 `ShareCardViewHistoryServiceImpl.java` 当前又已把 legacy 场景查卡统一改成只认 `active` 持卡实例，不再让已归档卡片继续参与当前卡片上下文解析
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java`、`UserShareCardServiceImpl.java`、`ActorCardConfigServiceImpl.java`、`ActorPersonalizationServiceImpl.java`、`ShareCardContactRequestServiceImpl.java` 与 `ShareCardViewHistoryServiceImpl.java` 当前又已把活动卡解析入口进一步统一到 `resolveActiveCard(...)`：服务层共享同一套 `shareCardId / owner(actor)Id + sceneKey` 查卡分流，各业务服务只再保留自己的一致性校验、默认卡补偿与异常语义
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 当前又已把默认普通卡补偿、后台默认卡状态检查与分享偏好读写进一步对齐到同一口径：默认 `general` 卡查找统一复用 `resolveActiveCard(...)`，偏好链里的 `sceneKey` 也统一按 `normalizeSceneKey(...)` 存取与回填
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 当前又已把命理应用幸运色链里的配置读路径收回统一入口：`applyLuckyColor(...)` 不再单独裸读 scene latest config，`actor_card_config` 的场景级 latest 当前只继续保留在 `resolveConfigForShareCard(...)` 内部作为 legacy 修复来源
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java`、`UserShareCardServiceImpl.java` 与 `ActorCardConfigServiceImpl.java` 当前又已把实例配置绑定修复进一步统一到 `backfillLatestConfigBinding(...)`：`latest_config_id / actor_profile_id / template_id` 的回绑判断当前只保留一处服务层事实源，不再在持卡服务和配置服务里各维护一版
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java`、`UserShareCardServiceImpl.java` 与 `ActorCardConfigServiceImpl.java` 当前又已把实例绑定配置校验进一步统一到 `resolveBoundLatestConfig(...)`：`latest_config_id` 指向配置是否仍与当前 user/scene 匹配的判断当前也只保留一处服务层事实源，不再在持卡服务和配置服务里各维护一版私有校验方法
- `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/ActorCardConfigQueryDTO.java`、`ActorPersonalizationQueryDTO.java`、`ContactRequestStatusQueryDTO.java` 与 `kaipaile-server/src/main/java/com/kaipai/module/model/fortune/dto/ApplyLuckyColorReqDTO.java` 当前又已把 controller / DTO 入参门禁显式收口到 `shareCardId-first`：`/card/config`、`/card/personalization`、`/card/contact-requests/status` 与命理应用请求都开始在 controller 层明确表达“`shareCardId` 优先，scene 仅兼容”
- `kaipai-frontend/src/utils/share-card-mvp.ts`、`src/utils/share-artifact.ts`、`src/pages/actor-profile/detail.vue`、`src/pkg-card/actor-card/index.vue` 与 `src/pkg-card/fortune/index.vue` 当前又已把前端个性化查询与分享路径层的冗余旧键透传继续收口：`shareCardId` 已知时不再继续额外透传 `actorId / sceneKey / requestedScene`，公开页 path 与分享路径当前也开始显式按 `target` 驱动
- `kaipai-frontend/src/types/personalization.ts`、`src/api/personalization.ts`、`src/api/level.ts`、`src/api/fortune.ts`、`src/api/contact.ts`、`src/api/history.ts` 与 `src/pkg-card/actor-card/index.vue` 当前又已把前端 API 类型与请求组包继续收口到 `shareCardId-first`：`personalization / config / fortune / contact / history` 这些主链当前都使用显式联合类型并按实例分支或 legacy 分支分别组包，不再把多余旧键混发到请求层
- `kaipai-frontend/src/utils/share-card-mvp.ts` 与 `src/pkg-card/card-list/index.vue` 当前又已把“我的名片”显示层文案从 `sceneKey` 直接回退收口到统一场景展示 helper：模板缺失时会退回“普通 / 都市 / 古代”等用户可读标题，而不再把 `general / urban / costume` 直接展示给用户
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/CardSceneTemplateService.java`、`src/main/java/com/kaipai/module/server/card/service/impl/ShareCardViewHistoryServiceImpl.java`、`src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java`、`kaipai-frontend/src/utils/share-card-mvp.ts`、`src/api/history.ts`、`src/api/contact.ts` 与 `kaipai-admin/src/views/content/ContactRequestsView.vue` 当前又已把历史 / 已联系 / 后台联系方式的展示文案继续收口到单一来源：后端模板展示名解析统一下沉到 `resolveSceneDisplayName(...)`，前端与后台只再消费统一 `templateName` 并保留最后一层用户可读 fallback；`sceneKey` 当前只保留为技术上下文，不再作为主展示文案裸露
- `kaipai-frontend/src/utils/share-card-mvp.ts`、`src/api/personalization.ts`、`src/api/level.ts`、`src/api/contact.ts`、`src/api/history.ts`、`src/api/fortune.ts`、`src/pages/actor-profile/detail.vue`、`src/pkg-card/actor-card/index.vue`、`src/pkg-card/fortune/index.vue`、`kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java`、`src/main/java/com/kaipai/module/controller/card/CardContactRequestController.java` 与 `src/main/java/com/kaipai/module/controller/fortune/FortuneController.java` 当前又已把分享卡主链推进到 `shareCardId-only`：公开查看、再次进入、联系方式申请、查看历史写入、配置保存与幸运色应用主链已不再继续接受 `actorId + sceneKey` 作为卡片定位参数
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java`、`src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` 与 `kaipai-admin/src/views/content/ShareCardsView.vue` 当前又已把旧数据治理显式化：后台现已可以查看历史 / 联系方式申请 / 分享偏好中尚未绑定 `shareCardId` 的存量，并触发 `repair-legacy` 一次性修复，不再只依赖运行时被动回填
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardViewHistoryServiceImpl.java`、`src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java`、`src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 与 `src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 当前又已把主链 runtime 自动回填继续退场：查看历史、联系方式状态/列表与分享偏好主链只再消费已绑定 `shareCardId` 的记录，旧数据修复责任已进一步转移到后台显式治理动作
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java` 与 `src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` 当前又已把兼容型实例解析入口继续退场：`resolveActiveCard(...)` 已删除，主链与治理链开始分别显式调用 card-id 解析、owned-card 查询与 legacy 修复专用入口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/fortune/FortuneController.java`、`src/main/java/com/kaipai/module/server/fortune/service/impl/FortuneReportServiceImpl.java` 与 `kaipai-frontend/src/pkg-card/fortune/index.vue` 当前又已把“进入命理页 -> 应用幸运色 -> 返回编辑页”推进到 `shareCardId-first`，不再继续按 `currentUserId + sceneKey` 猜当前要修改的卡片配置
- `kaipai-frontend/src/pkg-card/fortune/index.vue` 与 `src/api/fortune.ts` 当前又已把命理页冗余入参继续删减为“实例已知时不再继续透传 `requestedScene / sceneKey`”，因此命理页主写链也继续向 `shareCardId-only` 收口
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 当前又已把联系方式申请待处理列表收口为“实例已知时优先按 `shareCardId` 精确过滤”，因此编辑页处理入口也不再继续把“同场景”当成当前卡片的唯一处理范围
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` 当前又已把建卡回包推进到 `latest_config_id-first`，因此“创建卡片 -> 立即拿回 cardId/configId -> 进入编辑页”的首跳也开始围绕真实卡片实例而不是场景 latest 猜测
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 当前又已把默认普通卡补偿与后台治理检查推进到 `latest_config_id-first`，因此默认卡治理面开始与真实绑定卡片保持同一条配置事实源
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java` 与 `ShareCardViewHistoryServiceImpl.java` 当前又已把旧联系方式申请 / 历史记录的 `share_card_id` 被动回填落到原表记录，legacy 兼容键开始随着真实读取逐步退场
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java` 当前又已把联系方式状态查询、审批返回与后台详情统一收口到“先解析真实卡片再吐 DTO”，因此联系方式返回面也继续向 `shareCardId-first` 对齐
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardViewHistoryServiceImpl.java` 与 `ShareCardContactRequestServiceImpl.java` 当前又已把旧记录校正从“只回填 `share_card_id`”推进到“整组校正 `ownerUserId / sceneKey / shareCardId`”，因此 legacy 记录的残余影响面继续缩小
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java` 当前又已把后台联系方式申请主列表也收口到“先解析真实卡片实例，再加载双方用户上下文并组装 DTO”，同时 `resolveRequestCard(...)` 在记录已带 `shareCardId` 时也会继续回正整组卡片上下文；因此后台治理面最后一条仍可能直接依赖旧申请单字段的主读链也已开始向实例事实源统一

### 3.2 后端 / 数据

- `kaipaile-server/src/main/resources/db/migration/V20260404_005__user_share_card.sql` 已新增 `user_share_card` 和 `share_card_contact_request.share_card_id`
- `kaipaile-server/src/main/resources/db/migration/V20260404_006__share_card_view_history_share_card_id.sql` 已为查看历史补 `share_card_id`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` 已承接最小独立持卡实体
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已补齐 `/card/my-cards`、建卡、归档和 `shareCardId` 版个性化解析
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardContactRequestController.java` 与 `ShareCardContactRequestServiceImpl.java` 已补齐联系方式申请 / 审批 / 已联系列表
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardViewHistoryController.java` 与 `ShareCardViewHistoryServiceImpl.java` 已补齐真实查看历史
- `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/ContactRequestApplyDTO.java`、`ShareCardHistoryRecordDTO.java`、`ShareCardContactRequestServiceImpl.java` 与 `ShareCardViewHistoryServiceImpl.java` 已把联系申请、状态查询、历史写入、历史/已联系列表出参与旧记录回放统一收口到 `shareCardId-first`

### 3.3 后台治理

- `kaipai-admin/src/views/content/TemplatesView.vue` 已承担风格模板启停、邀请门槛与发布治理
- `kaipai-admin/src/views/content/ContactRequestsView.vue` 已新增“联系方式申请”治理页，可按申请单、分享卡、持卡人、查看人、状态回看记录
- `kaipai-admin/src/views/content/ShareCardsView.vue` 已新增“分享卡治理”页，可按真实 `UserShareCard` 回看 `latest_config_id`、默认卡标记、查看历史和联系方式申请统计，直接核对持卡实例是否已成为三端共享事实源
- `kaipai-admin/src/views/content/DefaultGeneralCardView.vue` 已新增“默认普通卡”治理页，可查看 `general` 默认卡承载策略、单用户状态并执行手工补偿
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已新增 `/admin/content/contact-requests` 列表 / 详情接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已新增 `/admin/content/share-cards` 列表 / 详情接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已新增 `/admin/content/share-cards/legacy-summary` 与 `/admin/content/share-cards/repair-legacy`，当前最新远端回归已确认 `legacy-summary.totalPendingCount=0`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已新增 `/admin/content/default-general-card/strategy`、`/users/{userId}`、`/users/{userId}/compensate`
- `kaipai-admin/src/constants/menus.ts`、`src/router/index.ts`、`src/constants/permission-registry.ts` 已把 `page.content.contact-requests`、`page.content.share-cards`、`page.content.default-general-card` 与对应补偿动作权限纳入菜单、路由和角色授权矩阵
- `2026-04-05 00:43:24 +0800` 已按 `00-29` 标准 schema 发布脚本补齐远端缺失的 `V20260404_003 ~ 006`，记录为 `.sce/runbooks/backend-admin-release/records/20260405-004324-backend-schema-share-card-mvp-governance.md`
- `2026-04-05 00:47:21 +0800` 与 `00:53:13 +0800` 已按 `00-29` 标准 backend 发布脚本连续完成两次后端发布，分别修复“线上旧 jar 缺 `/card/my-cards`”与“新注册用户默认普通卡补偿命中 `actor_profile_id` 非空冲突”，记录为 `.sce/runbooks/backend-admin-release/records/20260405-004721-backend-only-share-card-mvp-runtime-align.md` 与 `.sce/runbooks/backend-admin-release/records/20260405-005313-backend-only-share-card-register-fix.md`
- `2026-04-05 01:01:04 +0800` 已按 `00-29` 标准 `admin-only` 脚本发布管理端静态页，记录为 `.sce/runbooks/backend-admin-release/records/20260405-010104-admin-only-share-card-governance-pages.md`
- `2026-04-05 00:57:40 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-005740-dev-remote-governance-sample/summary.md` 跑通：
  - owner `/card/my-cards`
  - viewer register + `/card/personalization`
  - `/card/view-histories`
  - `/card/contact-requests` apply/approve/approved
  - admin `/admin/content/contact-requests`
  - admin `/admin/content/default-general-card/*`
- `2026-04-05 22:43:34 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-224334-dev-remote-governance-sample-v2/summary.md` 再次跑通：
  - owner `/card/my-cards`
  - viewer `/card/personalization`、`/card/view-histories`、`/card/contact-requests/*`
  - admin `/admin/content/contact-requests`
  - admin `/admin/content/share-cards` 列表 / 详情
  - admin `/admin/content/share-cards/legacy-summary`，并确认 `totalPendingCount=0`
  - admin `/admin/content/default-general-card/*`
- `2026-04-05 01:16:31 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-011454-share-card-mini-program-page-evidence/summary.md` 固定 owner 首页 / 我的名片 / 卡片编辑 / 个人中心，以及 viewer 公开名片 / 查看历史六张小程序页面证据
- `2026-04-05 23:15:24 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-231337-share-card-mini-program-page-evidence-v2/summary.md` 把 owner 小程序卡片 / 分享海报终态截图与 `onShareAppMessage / onShareTimeline` payload 补入小程序页面证据
- `2026-04-05 23:23:43 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md` 把 viewer 从真实分享 path 再次进入小程序卡片 / 海报页的回流证据补入小程序页面证据
- `2026-04-05 23:32:15 +0800` 已新增样本 `../execution/share-card-mvp/samples/20260405-233215-share-card-release-post-checklist-record/summary.md`，把发布后检查清单的执行结果按 API / 小程序 / 后台 / blocker 四组核对项留档
- `2026-04-05 23:33:50 +0800` 已通过样本 `../execution/login-auth/samples/20260405-233350-dev-share-card-sms-bridge/summary.md` 与 `../execution/share-card-mvp/sms-capability-bridge.md`，把 share-card 当前剩余的 `sendCode` 口径显式桥接到 `00-51 current-phase-formal-sms-capability-deferral`
- `2026-04-05` 已新增 `../execution/login-auth/formal-sms-validation-gate.md`，把正式短信能力何时允许进入真实验证、需要哪些前提和样本入口显式固化；share-card 当前不再单独承接这类门禁判断
- `2026-04-05 23:49:12 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py` 产出样本 `../execution/share-card-mvp/samples/20260405-234912-share-card-release-post-checklist-record-auto-v2/summary.md`，把 checklist 执行结果留档推进为可重复自动生成
- `2026-04-05 23:53:48 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v3` 产出样本 `../execution/share-card-mvp/samples/20260405-235348-share-card-release-post-checklist-record-auto-v3/summary.md`，并把 backend / admin / schema 发布记录自动关联进 checklist 留档
- `2026-04-05 23:57:56 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v4` 产出样本 `../execution/share-card-mvp/samples/20260405-235756-share-card-release-post-checklist-record-auto-v4/summary.md`，并把 backend / admin / schema 发布记录中的关键 smoke 摘要抽取进 checklist 留档
- `2026-04-06 00:05:25 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v5` 产出样本 `../execution/share-card-mvp/samples/20260406-000525-share-card-release-post-checklist-record-auto-v5/summary.md`，并把发布记录 smoke 结果进一步收口为结构化字段写入 checklist 留档
- `2026-04-06 00:11:53 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v6` 产出样本 `../execution/share-card-mvp/samples/20260406-001153-share-card-release-post-checklist-record-auto-v6/summary.md`，并把 `backendContainerUp / apiDocsStatusCode / migrationApplied` 等状态字段补入结构化 smoke
- `2026-04-06 00:19:55 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v7` 产出样本 `../execution/share-card-mvp/samples/20260406-001955-share-card-release-post-checklist-record-auto-v7/summary.md`，并把 `adminLoginStatusCode / publicHomeStatusCode / staticAssetStatusCode / publicHomeUp / staticAssetUp` 等管理端发布后冒烟字段补入结构化 smoke
- `2026-04-06 00:25:43 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v8` 产出样本 `../execution/share-card-mvp/samples/20260406-002543-share-card-release-post-checklist-record-auto-v8/summary.md`，并把 backend 发布记录里的 `adminRecruitRolesStatusCode / actorRoleSearchStatusCode` 与对应 `401` 预期态判断补入结构化 smoke
- `2026-04-06 00:30:21 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v9` 产出样本 `../execution/share-card-mvp/samples/20260406-003021-share-card-release-post-checklist-record-auto-v9/summary.md`，并把主要 smoke URL 的 `ExpectedStatusCode / MatchesExpected` 判定补入结构化 smoke
- `2026-04-06 00:35:38 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v10` 产出样本 `../execution/share-card-mvp/samples/20260406-003538-share-card-release-post-checklist-record-auto-v10/summary.md`，并把主要 smoke URL 的统一 `Verdict` 判定补入结构化 smoke
- `2026-04-06 00:41:24 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v11` 产出样本 `../execution/share-card-mvp/samples/20260406-004124-share-card-release-post-checklist-record-auto-v11/summary.md`，并把 release-level `overallVerdict / failedKeys / missingKeys` 汇总补入结构化 smoke
- `2026-04-06 00:46:24 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v12` 产出样本 `../execution/share-card-mvp/samples/20260406-004624-share-card-release-post-checklist-record-auto-v12/summary.md`，并把 `release_records_all_pass` 接入 blocker judgment 与 overall 汇总
- `2026-04-06 00:53:08 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v13` 产出样本 `../execution/share-card-mvp/samples/20260406-005308-share-card-release-post-checklist-record-auto-v13/summary.md`，并把 `finalJudgment / finalJudgmentReason / newBlockingIssues / knownBlockingIssues` 补入总控结果区
- `2026-04-06 00:59:20 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v14` 产出样本 `../execution/share-card-mvp/samples/20260406-005920-share-card-release-post-checklist-record-auto-v14/summary.md`，并把 `newBlockingIssueKeys / newBlockingIssueReasons / knownBlockingIssueKeys / knownBlockingIssueReasons / blockingIssueSources` 补入总控结果区
- `2026-04-06 01:07:17 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v15` 产出样本 `../execution/share-card-mvp/samples/20260406-010717-share-card-release-post-checklist-record-auto-v15/summary.md`，并把 `blockingIssueMatrix` 补入总控结果区
- `2026-04-06 01:11:57 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v16` 产出样本 `../execution/share-card-mvp/samples/20260406-011157-share-card-release-post-checklist-record-auto-v16/summary.md`，并把 `blockingIssueSummary` 补入总控结果区
- `2026-04-06 01:18:28 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v17` 产出样本 `../execution/share-card-mvp/samples/20260406-011828-share-card-release-post-checklist-record-auto-v17/summary.md`，并把 `blockingIssueActionPlan` 补入总控结果区
- `2026-04-06 01:25:33 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v18` 产出样本 `../execution/share-card-mvp/samples/20260406-012533-share-card-release-post-checklist-record-auto-v18/summary.md`，并把 `releaseDecisionCard / blockingIssueDashboard` 补入总控结果区
- `2026-04-06 01:33:02 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v19` 产出样本 `../execution/share-card-mvp/samples/20260406-013302-share-card-release-post-checklist-record-auto-v19/summary.md`，并把 `releaseGoNoGoCard / operatorRunCard` 补入总控结果区
- `2026-04-20 10:04:49 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v21` 产出样本 `../execution/share-card-mvp/samples/20260420-100449-share-card-release-post-checklist-record-auto-v21/summary.md`，并把 `miniProgramBlockerSample`、DevTools 授权 blocker 与 `mini_program_blocker_recorded` 检查项接入自动总控结果区
- `2026-04-20 11:55:22 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v22` 产出样本 `../execution/share-card-mvp/samples/20260420-115522-share-card-release-post-checklist-record-auto-v22/summary.md`，并把 `ReleaseDecisionCard.topRisk`、`ReleaseGoNoGoCard.owner / nextAction` 与 `OperatorRunCard.immediateSteps` 优先对齐到当前 DevTools 授权 blocker
- `2026-04-20 11:59:11 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v23` 产出样本 `../execution/share-card-mvp/samples/20260420-115911-share-card-release-post-checklist-record-auto-v23/summary.md`，并把 `FinalJudgmentReason / Known Blocking Issue Keys / Known Blocker / Blocking Issue Matrix / Action Plan` 的 blocker 排序继续统一成 DevTools 授权 blocker 优先
- `2026-04-20 12:02:49 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v24` 产出样本 `../execution/share-card-mvp/samples/20260420-120249-share-card-release-post-checklist-record-auto-v24/summary.md`，并把 `operatorRunCard.primaryIssueKey / followupBatch` 继续收口到当前 DevTools 授权 blocker
- `2026-04-20 12:07:24 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v25` 产出样本 `../execution/share-card-mvp/samples/20260420-120724-share-card-release-post-checklist-record-auto-v25/summary.md`，并把 `releaseGoNoGoCard.primaryIssueKey / needsBatchSwitch` 继续收口到当前 DevTools 授权 blocker
- `2026-04-20 12:14:17 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v26` 产出样本 `../execution/share-card-mvp/samples/20260420-121417-share-card-release-post-checklist-record-auto-v26/summary.md`，并把 `blockingIssueDashboard.primaryIssueKey / topRisk / primaryOwner / nextAction` 与 `Notes` 顺序继续对齐到当前 DevTools 授权 blocker
- `2026-04-20 12:20:17 +0800` 已通过脚本 `../execution/share-card-mvp/run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v27` 产出样本 `../execution/share-card-mvp/samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`，并把 `OperatorRunCard.primaryIssueKey` 与 `Blocker Judgment` 顺序继续对齐到当前 DevTools 授权 blocker
- `2026-04-20` 当前已把 `auto-v27` 固化为 share-card 发布后总控默认基线版本；runbook、总包索引与发布后检查清单当前都默认先读 `releaseGoNoGoCard / operatorRunCard`，并允许自动总控继续显式回看 page-evidence blocker 样本
- `2026-04-20 13:06:35 ~ 14:12:16 +0800` 已把小程序 page-evidence / 自动总控 / 后台页面证据脚本接入同一轮标准化样本收口：
  - page-evidence 脚本已接入内置 DevTools preflight；当 `probeResult=devtools_auth_gate` 且 `9421=NO_LISTENER` 时，会直接生成 blocker 摘要并回链配套 `-preflight` 样本，不再先进入整套截图链路
  - 自动总控 `auto-v28 ~ auto-v29` 已验证：新的 preflight blocker 样本进入总控后，`releaseDecisionCard / blockingIssueDashboard / releaseGoNoGoCard / operatorRunCard` 仍一致收口到当前 DevTools 授权 blocker；且在不显式传 `--mini-blocker-sample` 时，会自动命中执行当时的最新 blocker 样本
  - 后台页面证据脚本 `v4` 起已统一落盘 `admin-page-evidence-result.json`，并在 summary / stdout 显式带出 `sourceSampleSelection*`
- `2026-04-20 14:33` 又已把 `../execution/share-card-mvp/run-share-card-devtools-auth-probe.py`、`../execution/share-card-mvp/run-share-card-mini-program-page-evidence.py` 与 `../execution/share-card-mvp/run-share-card-admin-page-evidence.py` 的参数入口统一补成 `argparse`；当前执行 `--help` 会直接输出帮助并正常退出，不会再误生成样本目录。同步核验时 `samples/` 目录数量保持 `76 -> 76`，且不存在 `*help*` 样本目录。
- 同轮又已把 mini/admin 两支脚本的 `--help` 文案同步改成当前真实调用规则：省略 `source_sample` 即自动命中最新 source sample；PowerShell 下一参未知 positional 自动按 label 解释，不再继续要求空字符串占位。
- `2026-04-20 14:29:22 ~ 16:44:37 +0800` 已继续通过脚本 `../execution/share-card-mvp/run-share-card-devtools-auth-probe.py` 复跑 `share-card-devtools-auth-probe-r2 ~ r6`；当前口径始终固定为 `AppID=wxd38339082a9cfa4e / probeResult=devtools_auth_gate / port-check=NO_LISTENER`。其中从 `r5` 起，探针 CLI stdout 与 `probe-result.json` 已同步显式带出 `sampleId / probeSummaryPath / resultPath / portCheckResult / cliReplay`；截至最新样本 `r6`，外部 DevTools 授权 blocker 仍未解除
- `2026-04-20 14:41:39 ~ 16:38:35 +0800` 已把最近一轮 blocker / admin / 自动总控样本继续收口为当前口径：
  - `r7 ~ r9`：验证 PowerShell 一参 label-only 调用、blocked 分支统一落盘、以及默认解析 / 并发场景下最新 blocker 样本的自动命中行为
  - `v5 ~ v7 + auto-v39 ~ auto-v40`：验证后台页面样本在默认解析与 admin 并发场景下的稳定命中，并据此把等待窗口收口到当前可用口径
  - `auto-v41 ~ auto-v42`：验证“最终结果文件优先”已进入结构化输出层，以及 `adminSampleSelectionMode / Display / Note` 已同步写入 summary、`checklist-result.json` 与 CLI stdout
  - `r10 ~ r11 + auto-v43 ~ auto-v46`：验证 probe stdout 扩字段、`preflightProbeResultPath` 引入，以及 blocker preflight `summary / result` 继续进入 summary、`checklist-result.json` 与 CLI stdout 三层输出；当前最完整验证样本固定为 `../execution/share-card-mvp/samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`
- `2026-04-05 01:26:54 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-012644-share-card-admin-page-evidence/summary.md` 固定“联系方式申请”列表 / 详情与“默认普通卡”治理页后台页面证据
- `2026-04-05 22:55:50 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-225535-share-card-admin-page-evidence-v2/summary.md` 把“分享卡治理”列表 / 详情补入后台页面证据基线
- `2026-04-05 23:08:13 +0800` 已通过样本 `../execution/share-card-mvp/samples/20260405-230757-share-card-admin-page-evidence-v3/summary.md` 把“分享卡治理 -> 执行 legacy 修复”动作截图与动作返回结果补入后台页面证据
- `2026-04-05` 已新增 `../execution/share-card-mvp/evidence-index.md`，把 API 回归样本、小程序页面证据与后台页面证据聚合为单入口索引，后续发布后可直接按统一入口取证
- `2026-04-05` 已新增 `../execution/share-card-mvp/evidence-bundle-index.md`，把当前发布回归使用的 API / 小程序 / 后台三类基线样本再聚合成总包入口
- `2026-04-05` 已新增 `../execution/share-card-mvp/release-post-checklist.md`，把发布后必须逐项确认的 API / 小程序 / 后台 / blocker 项固化为标准检查清单
- `2026-04-05` 已把 `.sce/runbooks/backend-admin-release/README.md` 与 `backend-admin-standard-release.md` 显式串到 share-card 的总包索引与发布后检查清单，后续发版后默认可直接按 runbook 进入这套回归
- 同批次还已确认 `ADMIN` 角色原本缺少 `page.content.contact-requests`、`page.content.default-general-card` 与 `action.content.default-general-card.compensate`，当前已通过后台角色更新接口补齐并重新登录管理员会话刷新权限

### 3.4 联调现状

- 本轮已完成本地三端静态验证：`kaipaile-server mvn -DskipTests compile`、`kaipai-admin npm run build`、`kaipai-frontend npm run type-check` 与 `npm run build:mp-weixin` 在本轮相关改造后均已通过
- `00-62` 已沉淀 share-card 基础结构样本：独立持卡实体、真实历史、联系方式申请闭环与后台治理入口都已落到代码与构建产物；`00-68` 当前阶段则继续在其上收口分享运行时与海报能力事实
- 当前默认入口已固定为：probe `r6`、mini blocker `r11`、admin 页面样本 `v7`、自动总控最完整验证样本 `auto-v46`
- 当前已具备围绕 `shareCardId` 主键、后台联系方式治理、分享卡治理、legacy-summary 零存量与默认普通卡治理的真实环境 API 样本，以及独立补齐的小程序 / 后台页面证据样本；`shareCardId-first` 主路径也已完成三轮收口，但当前更新后的 `00-68` 小程序 page-evidence 复验仍受 DevTools 授权 preflight 阻塞；正式短信能力仍归 `00-51` future batch，不再作为当前 `00-68` 主阻塞
- 当前发布后检查清单自动留档能力已经收口到一条可程序判断的总控链：
  - backend / admin / schema 发布记录当前都已具备结构化 smoke、`ExpectedStatusCode / MatchesExpected / Verdict`、release-level `overallVerdict / failedKeys / missingKeys`
  - 总控结果区当前也已具备 `finalJudgment / finalJudgmentReason / blockingIssueSources / blockingIssueMatrix / blockingIssueSummary / blockingIssueActionPlan`
  - 展示层当前已稳定输出 `releaseDecisionCard / blockingIssueDashboard / releaseGoNoGoCard / operatorRunCard`
  - runbook 当前默认仍以 `auto-v27` 为总控结构基线，同时以 `auto-v46` 作为“当前最完整验证口径”；若小程序 page evidence 阻塞，则默认先看最新 `miniProgramBlockerSample`（当前为 `20260420-161105-share-runtime-poster-page-evidence-r11`）与配套 preflight，再决定是否继续重跑 page evidence
  - 同时 share-card 的总控结构也已提炼为通用模板 `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
- 当前 `shareCardId-first / latest_config_id-first` 主链也已进入收敛尾段：
  - 用户侧卡片编辑入口当前已从“按场景打开”推进到“按实例打开”，并通过 `share-card-mvp.ts / share-card-latest.ts` 共享 helper 契约与 latest snapshot 入口
  - `/card/config` 读写、建卡回包、默认普通卡补偿与命理应用当前已围绕 `shareCardId-first + latest_config_id-first` 收口，编辑态开始具备“按实例进入、按实例读取、按实例保存、按实例应用命理主题”的最小闭环
  - 旧联系方式申请 / 历史记录 / 分享偏好当前已继续向真实卡片实例回填与校正，`actorId + sceneKey` / scene latest 依赖已缩到兼容修复与一次性回填范围
  - 后台联系方式申请主列表 / 详情、公开详情页与分享路径 helper 当前也都已回到“先解真实卡片实例，再消费 DTO / path”的口径
- 更细一层的服务与前端契约收口也已基本完成：
  - 服务层当前已把活动卡解析、`latest_config_id` 一致性修复、默认普通卡治理、分享偏好与命理配置读取继续压回统一入口，不再长期依赖 scene latest 猜测或散落的 `actorId + sceneKey` 分流
  - controller / DTO / API 类型 / helper 当前也已继续对齐到 `shareCardId-first` 契约，实例已知时不再混发冗余旧键，展示层对 `sceneKey` 的裸露也已继续收口
  - 后台“分享卡治理”当前已可直接核对 `UserShareCard -> actor_card_config -> history/contact-request` 的实例一致性，旧数据治理也已从“隐式 runtime backfill”推进到“后台显式修复动作”
  - 因此前台、后端、后台围绕同一张卡片实例的闭环当前已明显收紧，但在 DevTools 授权恢复前，仍不能用新的小程序 page-evidence 样本宣告闭环完成

## 4. 联调结论

- 当前是否具备三端联调条件：`部分具备`
- 已确认走通的链路：
  - 默认普通卡补偿 -> `/card/my-cards` -> 首页 / 我的名片真实持卡列表
  - 公开卡详情 -> 查看历史写入 -> 历史列表回看
  - 公开卡详情申请联系方式 -> 持卡人在卡片编辑页审批 -> 查看人已联系列表回看
  - 后台 `联系方式申请` 治理页 -> `/admin/content/contact-requests` 列表 / 详情
  - 后台 `分享卡治理` -> `/admin/content/share-cards` 列表 / 详情 -> `legacy-summary=0`
  - 后台 `默认普通卡` 治理页 -> `/admin/content/default-general-card/*` 策略摘要 / 单用户检查 / 手工补偿
- 当前不能宣告闭环的原因：
  - `run-share-card-mini-program-page-evidence.py` 的最新复验仍卡在 DevTools 开发者授权 preflight，当前无法产出新的 `00-68` 小程序截图证据
  - DevTools 授权恢复前，当前阶段只能继续回读 blocker / preflight / admin / auto checklist 样本，不能用新的小程序页面证据宣告 `00-68` 闭环完成

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-68` 已成为当前阶段上位边界，`00-62` 保留为 share-card 基础盘 |
| 数据模型、接口、状态流转清楚 | 部分满足 | `UserShareCard / history / contact-request` 已落地，`shareCardId-first` 主路径已统一，`00-68` 的分享链事实源与海报能力口径也已收口；但 DevTools 授权 gate 未恢复，仍缺修复后的新一轮小程序页面证据 |
| 后台治理入口可操作 | 已满足 | 模板治理、联系方式申请治理、分享卡治理与默认普通卡治理均已有真实环境样本，`legacy-summary` 已验证为 0，后台页面当前默认样本已推进到 `v7` |
| 小程序或前台用户侧落点可验证 | 部分满足 | 首页 / 历史 / 个人中心 / 公开详情 / 我的名片都已开始消费真实链路，且 active 入口已切到共享 capability；但 `00-68` 当前缺少 DevTools gate 解除后的最新 page-evidence 样本 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | probe / blocker / preflight / auto checklist / runbook 均已收口成统一读法，但外部 DevTools 授权 gate 仍阻塞新的页面级闭环证据 |
| 文档、映射表、验证记录已回填 | 已满足 | `00-68 execution`、`share-card-mvp` 执行卡、统一证据索引、发布回归总包索引、发布后检查清单与后台分享卡治理页面证据基线都已回填 |

## 6. 当前阻塞项

- 当前主阻塞：WeChat DevTools 登录账号仍未获得 appid `wxd38339082a9cfa4e` 的开发者授权，`9421` automation endpoint 继续 `NO_LISTENER`
- 未来批次提醒：`sendCode` 仍是开发态验证码返回，但正式短信能力继续归 `00-51` 跟踪，不混入当前 `00-68` blocker 判定

## 7. 下一轮最小动作

1. 先恢复当前 WeChat DevTools 登录账号对 appid `wxd38339082a9cfa4e` 的开发者授权，并复跑 `../execution/share-card-mvp/run-share-card-devtools-auth-probe.py`
2. 只有探针不再返回 `devtools_auth_gate / NO_LISTENER`，再复跑 `../execution/share-card-mvp/run-share-card-mini-program-page-evidence.py`
3. 若 page evidence 仍失败，直接回读 `../execution/share-card-mvp/samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md` 与配套 `-preflight` 样本；若探针通过，则更新小程序页面证据与自动总控卡
4. DevTools 授权问题解除后，剩余未来能力缺口继续按 `00-51` 处理正式短信验证，不混入当前 `00-68` 主线

### 2026-04-13

- 当前判定：`局部完成`
- 备注：本轮线上复核已确认 share-card 主链存在新的运行时风险：部分 `shareCardId` 能正常返回 `/api/card/personalization`，但继续读取 `/api/actor/{actorId}` 会返回 `演员档案不存在`；同时 `poster` artifact 仍在对部分用户返回 `locked=true / lockReason=会员可生成定制海报`，而首页 / 卡片列表 / 编辑页仍持续展示“分享海报”按钮。当前已将两类问题提升为 `00-68 current-phase-share-runtime-and-poster-capability-alignment` 独立 Spec，后续按“分享公开链事实源收口 + 海报能力口径统一”整改。

### 2026-04-20

- 当前判定：`局部完成`
- 备注：`00-68` 当前又继续完成一刀前端 active 入口收口：`home / card-list / actor-card` 三处“分享海报”入口现已统一服从共享 capability 判断，不再保留“按钮先展示、点击后才提示海报锁定”的旧交互；`npm run type-check` 与 `npm run build:mp-weixin` 已再次通过。
- 备注补充：同日继续尝试复跑 `run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-runtime-poster-page-evidence`，新样本 `samples/20260420-083603-share-runtime-poster-page-evidence/` 已固定失败现场。`stderr` 明确报 `Failed connecting to ws://127.0.0.1:9421`；复用仓内历史同机命令 `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9421` 后，仍返回 `登录用户不是该小程序的开发者`，且 `9421` 继续 `NO_LISTENER`。因此当前剩余主阻塞已明确收口为 DevTools 开发者授权，而不是前端页面或取证脚本本身。
- 备注补充：同日又已把 `run-share-card-mini-program-page-evidence.py` 补成“失败也产 blocker 包”的标准入口，并用同一条失败路径复跑产出首个标准 blocker 包样本 `samples/20260420-090456-share-runtime-poster-page-evidence-r2/`。当前即使 DevTools 仍未授权，也会自动留存 `summary.md + captures/devtools-auth-blocker.txt + captures/devtools-cli-auto*.log + captures/port-check.txt`，后续不再需要手工补写阻塞现场。
- 备注补充：同日 `13:06:35 +0800` 又已把 `run-share-card-mini-program-page-evidence.py` 进一步接入内置 DevTools preflight，并产出 `samples/20260420-130633-share-runtime-poster-page-evidence-r3/` 与配套 `samples/20260420-130633-share-runtime-poster-page-evidence-r3-preflight/`。当前若 `probeResult=devtools_auth_gate` 且 `9421=NO_LISTENER`，脚本会在 preflight 阶段直接拦截并回链探针摘要，不再先进入整套截图链路。
- 备注补充：同日 `13:06:53 +0800` 又已通过 `samples/20260420-130653-share-card-release-post-checklist-record-auto-v28/summary.md` 验证：新的 preflight blocker 样本进入自动总控后，默认读法与主风险排序仍保持 `mini_program_devtools_auth_gate` 优先；默认总控基线仍为 `auto-v27`。
- 备注补充：截至 `16:44:37 +0800`，最新探针样本已推进到 `samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`，当前结论继续固定为 `AppID=wxd38339082a9cfa4e`、`probeResult=devtools_auth_gate`、`portCheckResult=NO_LISTENER`；与之对应的当前默认 blocker / admin / auto 入口分别为 `r11 / v7 / auto-v46`，说明当前文档主线应以 `00-68 + auto 当前入口` 为准，而不再停留在 `00-62` 的旧摘要口径。

## 8. 回填记录

### 2026-04-05

- 当前判定：`局部完成`
- 备注：本轮已把默认普通卡从“只有后端隐式补偿逻辑”推进为“后台可见、可检查、可手工补偿”的独立治理入口，并在 `00:43:24 +0800 -> 22:43:34 +0800` 的同一轮排障 / 回归中补齐了 share-card 真实环境总控样本、schema 漏发修复、backend 旧 jar 修复、新注册用户默认卡兼容修复、后台角色权限数据回填、小程序 / 后台页面证据样本，以及分享卡治理 / legacy-summary 零存量二次回归样本。
- 备注补充：同日又已把 API 样本、小程序页面证据与后台页面证据聚合为 `execution/share-card-mvp/evidence-index.md`，并补齐后台“分享卡治理”列表 / 详情页面证据，后续发布可直接按单入口做回归取证。
- 备注补充：同日又已新增 `execution/share-card-mvp/evidence-bundle-index.md` 作为发布回归总包入口，后续发布后默认可直接从总包入口查看 API / 小程序 / 后台三类基线证据。
- 备注补充：同日又已新增 `execution/share-card-mvp/release-post-checklist.md`，后续发布后除看总包索引外，还可按清单逐项确认关键核对项，减少漏检。

### 2026-04-04

- 当前判定：`局部完成`
- 备注：本轮已把 `00-62` 从“只有 requirements/design/tasks/execution”推进为 `00-28` 下可持续回填的独立状态对象，并明确当前口径不是“还没落到真实结构”，而是“已落到第一批真实前后端 / 后台结构，但仍未完全闭环”。
