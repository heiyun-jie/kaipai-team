# 会员能力与模板配置闭环状态回填

## 1. 归属切片

- `../slices/membership-template-capability-slice.md`
- `../execution/membership/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：后台会员与模板治理能力相对完整，演员端已补齐 `/level/info` 能力摘要、`/card/*`、`/card/personalization`、`/fortune/*`、`/ai/*`、`/actor/profile/*` 与 `/actor/{id}` 最小输出，小程序运行时也已放开 `verify / invite / level / card / ai / fortune / actor` 真接口分支，核心页面已收掉主要等级 / 会员硬编码，`actor-card` 也已切到 `/card/personalization` 作为基线事实源，但主题 preview overlay 与分享恢复链路仍有本地逻辑，且尚未完成真实闭环联调。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已具备会员说明、模板消费和分享产物展示
- `kaipai-frontend/src/api/level.ts` 已消费 `/api/level/info`、`/api/card/scene-templates`、`/api/card/config`、`/api/ai/*`
- `kaipai-frontend/src/api/actor.ts` 已约定消费 `/api/actor/profile/mine`、`/api/actor/profile/{userId}`、`/api/actor/{userId}`
- `kaipai-frontend/src/api/fortune.ts` 已消费 `/api/fortune/report`、`/api/fortune/apply-lucky-color`
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `verify / invite / level / card / ai / fortune / actor` 真接口能力
- `kaipai-frontend/src/stores/user.ts`、`src/pkg-card/membership/index.vue`、`src/pkg-card/invite/index.vue`、`src/pkg-card/fortune/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已开始消费后端等级 / 会员能力摘要，不再继续硬编码公开演员为 `Lv5/member`
- `kaipai-frontend/src/api/personalization.ts`、`src/utils/personalization.ts` 已开始优先消费 `/api/card/personalization`，把主题 / 能力 gating / 分享产物从“页面内多点拼装”收口到后端汇总口径
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已改成以 `/card/personalization` 返回的模板、能力、主题和分享产物为基线，只把未保存的布局 / 配色改动保留成本地 preview overlay
- 小程序当前尚未完全消除 `theme-resolver / share-artifact` 等本地兜底逻辑，主题 preview overlay 与分享恢复 path 仍有页面级拼装
- `kaipai-frontend/src/utils/personalization.ts`、`src/utils/theme-resolver.ts`、`src/utils/share-artifact.ts` 仍保留主题 token 和分享产物组装逻辑，但核心 gating 与页面基线已允许由后端摘要覆盖

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java` 已具备会员产品、账户、日志等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已具备模板、发布、回滚、主题 token、分享产物等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/level/LevelController.java` 已提供包含等级能力 / 分享能力摘要的 `/level/info`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已提供 `/card/scene-templates`、`/card/config`、`/card/personalization` 查询接口与配置保存接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/ActorPersonalizationService.java`、`impl/ActorPersonalizationServiceImpl.java` 已补齐模板、能力摘要、命理摘要、主题 token 与分享产物的统一汇总输出
- `kaipaile-server/src/main/java/com/kaipai/module/controller/fortune/FortuneController.java` 已提供 `/fortune/report`、`/fortune/apply-lucky-color`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` 已提供 `/ai/quota`、`/ai/polish-resume`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已补齐 `/card/personalization` 聚合接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`、`ActorController.java` 已补齐 `/actor/profile/mine`、`/actor/profile/{userId}`、`PUT /actor/profile`、`/actor/{userId}`、`/actor/search`
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/MembershipAccountService.java`、`impl/MembershipAccountServiceImpl.java` 已补齐演员端等级信息、等级能力与分享能力摘要输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/ActorProfileService.java`、`impl/ActorProfileServiceImpl.java` 已补齐 actor 档案 DTO 映射、经历恢复、扩展字段读写与搜索最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/CardSceneTemplateService.java`、`ActorCardConfigService.java` 及其实现类已补齐模板列表、默认配置、配置保存的最小 actor 输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/fortune/service/FortuneReportService.java`、`impl/FortuneReportServiceImpl.java` 已补齐当前用户命理报告读取与幸运色应用最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiQuotaService.java`、`impl/AiQuotaServiceImpl.java` 已补齐月度 AI 配额查询与消费最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/ActorPersonalizationService.java`、`impl/ActorPersonalizationServiceImpl.java` 已补齐模板 / fortune / theme / artifact 聚合最小实现
- `2026-04-02` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- 后台已具备会员产品 / 账户治理和模板发布 / 回滚治理入口
- 服务层已接入多类后台操作日志，具备后台自证和审计基础

### 3.4 联调现状

- 当前能确认“后台治理链路”、“演员端最小输出链路”、“AI / Fortune 最小权威接口”、“个性化汇总接口”和“小程序真接口开关”五段能力都已具备，`actor-card` 也已不再以本地模板 / 主题 / 产物组装作为主事实源
- 当前不能确认后台发布模板或开通会员后，小程序是否已经按同一份后端事实数据恢复全部页面，因为主题 preview overlay、分享恢复 path 与 AI 实际生成仍有本地 / 演示态逻辑，且还未完成真实环境联调

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：后台治理能力、演员端 `/level/info` 能力摘要、`/card/*`、`/card/personalization`、`/fortune/*`、`/ai/*`、`/actor/profile/*`、`/actor/{id}` 输出、配置保存链路、小程序 `verify / invite / level / card / ai / fortune / actor` 真接口开关均已落位
- 当前不能宣告闭环的原因：前台虽已把 `actor-card` 基线切到 `/card/personalization`，但主题 preview overlay 和分享恢复链路仍有页面级本地逻辑，AI 仍只是名片页最小配额与文案切换，且后台配置变更到小程序展示的真实联调还未完成

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成会员与模板切片及执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端 `actor/level/card/fortune/ai` 最小契约已落地，但模板态与 AI patch 流转仍待继续收口 |
| 后台治理入口可操作 | 已满足 | 会员产品、账户、模板、发布、回滚入口均已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 前台页面存在，且 `verify / invite / level / card / actor` 已可走真实分支，但还未完成整页真实联调与能力判断收口 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和发布 / 回滚具备，演员端 AI 配额与等级 / 会员 gating 已开始权威化，但真实回滚与联调仍待继续收口 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立会员与模板切片状态基线 |

## 6. 当前阻塞项

- `actor-card` 已切到 `/card/personalization` 基线，但主题 preview overlay、分享 path 和部分页面兜底仍保留本地逻辑，没有完全切到后端统一服务口径
- AI 配额虽已具备最小真接口，但仍缺编辑页 patch 流程和更完整的失败 / 回滚约束
- 模板发布 / 回滚后的前台恢复链路尚未完成真实联调

## 7. 下一轮最小动作

1. 继续把分享恢复 path、themeId 透传和剩余页面 preview 逻辑从页面内拼装迁到统一 personalization 口径
2. 把 AI 从“最小配额真接口”继续推进到编辑页 patch / 应用 / 撤销链路
3. 跑通一次“后台开通会员 / 发布模板 -> 小程序名片页、公开详情页、邀请页同步变化”的联调回填

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：当前阶段明确把“后台治理较完整、前台展示较丰富、演员端输出缺失”写入状态文档，避免把本地 resolver 误判成后端闭环

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/level/info`、`/card/scene-templates`、`/card/config` 最小 actor 输出，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍缺前台真实切换与联调

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 运行时已放开 `verify / invite / level / card` 真接口分支，并把 `card` 与 `ai` 能力拆分，避免误切到未完成 AI 接口；`kaipaile-server` 再次在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过，`kaipai-frontend` 已执行 `npm run type-check` 通过，当前仍缺 `actor/profile` 权威接口、公开访客链路收口和真实环境联调

### 2026-04-02（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/actor/profile/mine`、`/actor/profile/{userId}`、`PUT /actor/profile`、`/actor/{userId}`、`/actor/search`，并放开公开详情页和名片页所需的只读接口；`kaipai-frontend` 已放开 `actor` 真接口分支，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺主题 / 能力 gating 与 AI 配额的权威化，以及真实环境联调

### 2026-04-02（三次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/level/info` 等级 / 会员能力摘要、`/fortune/report`、`/fortune/apply-lucky-color`、`/ai/quota`、`/ai/polish-resume` 最小 actor 输出；`kaipai-frontend` 已放开 `ai / fortune` 真接口分支，并让 `membership / invite / fortune / actor-card / actor-profile detail` 开始消费后端能力摘要，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺主题 token 全量后端化与真实环境联调

### 2026-04-02（四次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已新增 `/card/personalization` 汇总接口，把模板、能力摘要、命理摘要、主题 token 与分享产物收口到统一后端口径；`kaipai-frontend` 已让 `api/utils/personalization` 优先消费该汇总接口，并让公开详情页切到后端个性化摘要，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺编辑态主题配置与真实环境联调

### 2026-04-02（五次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/pkg-card/actor-card/index.vue` 已改成以 `/api/card/personalization` 返回的模板、能力、主题与分享产物为主事实源，未保存的布局 / 配色仅作为本地 preview overlay；原先页面内直连 `scene-templates / card-config / fortune-report` 再本地拼 `personalizationProfile` 的主链已移除，`npm run type-check` 通过。当前剩余高优先级缺口收敛为“分享恢复 path 与剩余 preview 逻辑仍有页面级本地拼装”以及“后台配置变化到前台恢复的真实联调尚未完成”
