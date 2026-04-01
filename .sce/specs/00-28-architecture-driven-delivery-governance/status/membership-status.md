# 会员能力与模板配置闭环状态回填

## 1. 归属切片

- `../slices/membership-template-capability-slice.md`
- `../execution/membership/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：后台会员与模板治理能力相对完整，演员端已补齐 `/level/info`、`/card/scene-templates`、`/card/config`、`/actor/profile/*` 与 `/actor/{id}` 最小输出，小程序运行时也已放开 `verify / invite / level / card / actor` 真接口分支，但主题 / 能力 gating 仍主要靠本地 resolver，AI 配额也仍未权威化，尚未完成真实闭环联调。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已具备会员说明、模板消费和分享产物展示
- `kaipai-frontend/src/api/level.ts` 已消费 `/api/level/info`、`/api/card/scene-templates`、`/api/card/config`，并把 `card` 与 `ai` 能力拆开，避免误切到未完成的 AI 接口
- `kaipai-frontend/src/api/actor.ts` 已约定消费 `/api/actor/profile/mine`、`/api/actor/profile/{userId}`、`/api/actor/{userId}`
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `verify / invite / level / card / actor` 真接口能力
- `kaipai-frontend/src/utils/personalization.ts`、`src/utils/level.ts`、`src/utils/theme-resolver.ts`、`src/utils/share-artifact.ts` 仍在本地推导等级、主题 token、能力 gating 和分享产物
- `kaipai-frontend/src/pages/actor-profile/detail.vue`、`src/pkg-card/actor-card/index.vue`、`src/pkg-card/verify/index.vue`、`src/pages/actor-profile/edit.vue` 等页面已具备切到 actor 真接口的前置条件，但主题 / 能力判断仍未后端化

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java` 已具备会员产品、账户、日志等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已具备模板、发布、回滚、主题 token、分享产物等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/level/LevelController.java` 已提供 `/level/info`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已提供 `/card/scene-templates`、`/card/config` 查询与保存接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`、`ActorController.java` 已补齐 `/actor/profile/mine`、`/actor/profile/{userId}`、`PUT /actor/profile`、`/actor/{userId}`、`/actor/search`
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/MembershipAccountService.java`、`impl/MembershipAccountServiceImpl.java` 已补齐演员端等级信息输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/ActorProfileService.java`、`impl/ActorProfileServiceImpl.java` 已补齐 actor 档案 DTO 映射、经历恢复、扩展字段读写与搜索最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/CardSceneTemplateService.java`、`ActorCardConfigService.java` 及其实现类已补齐模板列表、默认配置、配置保存的最小 actor 输出
- `2026-04-02` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- 后台已具备会员产品 / 账户治理和模板发布 / 回滚治理入口
- 服务层已接入多类后台操作日志，具备后台自证和审计基础

### 3.4 联调现状

- 当前能确认“后台治理链路”、“演员端最小输出链路”和“小程序真接口开关”三段能力都已具备，actor 档案主链路不再只靠 mock
- 当前不能确认后台发布模板或开通会员后，小程序是否已经按同一份后端事实数据恢复全部页面，因为主题 / 能力 gating 仍大量依赖本地 resolver，且 AI 配额仍未接入权威接口

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：后台治理能力、演员端 `/level/info`、`/card/*`、`/actor/profile/*`、`/actor/{id}` 输出、配置保存链路、小程序 `verify / invite / level / card / actor` 真接口开关均已落位
- 当前不能宣告闭环的原因：前台主题 / 能力 gating 仍主要依赖本地规则库，AI 配额未完成权威化，且后台配置变更到小程序展示的真实联调还未完成

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成会员与模板切片及执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端 `actor/level/card` 最小契约已落地，但模板态与能力 gating 的完整权威输出仍待继续收口 |
| 后台治理入口可操作 | 已满足 | 会员产品、账户、模板、发布、回滚入口均已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 前台页面存在，且 `verify / invite / level / card / actor` 已可走真实分支，但还未完成整页真实联调与能力判断收口 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和发布 / 回滚具备，演员端 AI 配额和更细粒度 gating 仍待继续收口 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立会员与模板切片状态基线 |

## 6. 当前阻塞项

- 小程序仍主要依赖本地 resolver 推导主题、模板、产物能力，没有彻底切到后端权威结果
- AI 配额与更细粒度会员能力仍未补齐权威 actor 输出，部分页面仍需本地 fallback
- 模板发布 / 回滚后的前台恢复链路尚未完成真实联调

## 7. 下一轮最小动作

1. 让主题 / 能力 gating 逐步从本地 resolver 迁到后端权威字段或统一服务口径
2. 补齐 AI 配额与更细粒度会员摘要接口，继续收掉页面级 fallback
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
