# 会员能力与模板配置闭环状态回填

## 1. 归属切片

- `../slices/membership-template-capability-slice.md`
- `../execution/membership/README.md`

## 2. 当前判定

- 回填日期：`2026-04-01`
- 当前判定：`局部完成`
- 一句话结论：后台会员与模板治理能力相对完整，演员端也已补齐 `/level/info`、`/card/scene-templates`、`/card/config` 最小输出，但小程序还没完成从本地 resolver 切到真实消费链路，所以仍未形成“后台配置 -> 后端下发 -> 前台恢复”的真实闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已具备会员说明、模板消费和分享产物展示
- `kaipai-frontend/src/utils/personalization.ts`、`src/utils/level.ts`、`src/utils/theme-resolver.ts`、`src/utils/share-artifact.ts` 仍在本地推导等级、主题 token、能力 gating 和分享产物
- `kaipai-frontend/src/api/level.ts` 约定的 `/api/level/info`、`/api/card/scene-templates`、`/api/card/config` 已有演员端最小公开实现，但前台仍未完成从本地 resolver 到真实接口结果的彻底切换

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java` 已具备会员产品、账户、日志等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已具备模板、发布、回滚、主题 token、分享产物等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/level/LevelController.java` 已提供 `/level/info`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已提供 `/card/scene-templates`、`/card/config` 查询与保存接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/MembershipAccountService.java`、`impl/MembershipAccountServiceImpl.java` 已补齐演员端等级信息输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/CardSceneTemplateService.java`、`ActorCardConfigService.java` 及其实现类已补齐模板列表、默认配置、配置保存的最小 actor 输出
- `2026-04-01` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- 后台已具备会员产品 / 账户治理和模板发布 / 回滚治理入口
- 服务层已接入多类后台操作日志，具备后台自证和审计基础

### 3.4 联调现状

- 当前能确认“后台治理链路”和“演员端最小输出链路”都已具备
- 当前不能确认后台发布模板或开通会员后，小程序是否已经按同一份后端事实数据恢复页面，因为前台仍大量依赖本地 resolver

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：后台治理能力、演员端 `/level/info` 与 `/card/*` 输出、配置保存链路均已落位
- 当前不能宣告闭环的原因：前台仍主要依赖本地规则库，且后台配置变更到小程序展示的真实联调还未完成

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成会员与模板切片及执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端 `level/card` 最小契约已落地，但会员态与模板态的完整权威输出仍待继续收口 |
| 后台治理入口可操作 | 已满足 | 会员产品、账户、模板、发布、回滚入口均已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 前台页面存在，且后端最小输出已补齐，但还未完成真实切换与联调 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和发布 / 回滚具备，演员端 AI 配额和更细粒度 gating 仍待继续收口 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立会员与模板切片状态基线 |

## 6. 当前阻塞项

- 小程序仍主要依赖本地 resolver 推导等级、模板、产物能力，没有彻底切到后端权威结果
- `membership` 控制器层仍没有更完整的演员端会员摘要接口，当前先由 `/level/info` 承接最小等级信息
- 模板发布 / 回滚后的前台恢复链路尚未完成真实联调

## 7. 下一轮最小动作

1. 让小程序把 `/level/info`、`/card/scene-templates`、`/card/config` 接到真实链路，校验页面结果与本地 resolver 是否一致
2. 视前台切换结果决定是否继续补 `membership` actor 摘要接口，降低页面对本地规则的依赖
3. 跑通一次“后台开通会员 / 发布模板 -> 小程序名片页、公开详情页、邀请页同步变化”的联调回填

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：当前阶段明确把“后台治理较完整、前台展示较丰富、演员端输出缺失”写入状态文档，避免把本地 resolver 误判成后端闭环

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/level/info`、`/card/scene-templates`、`/card/config` 最小 actor 输出，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍缺前台真实切换与联调
