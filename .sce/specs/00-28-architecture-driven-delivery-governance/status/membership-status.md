# 会员能力与模板配置闭环状态回填

## 1. 归属切片

- `../slices/membership-template-capability-slice.md`
- `../execution/membership/README.md`

## 2. 当前判定

- 回填日期：`2026-04-01`
- 当前判定：`局部完成`
- 一句话结论：后台会员与模板治理能力相对完整，但演员端 `membership / card` 控制器还没有公开接口，小程序仍主要依赖本地 resolver 推导等级、主题和产物，尚未形成“后台配置 -> 后端下发 -> 前台恢复”的真实闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已具备会员说明、模板消费和分享产物展示
- `kaipai-frontend/src/utils/personalization.ts`、`src/utils/level.ts`、`src/utils/theme-resolver.ts`、`src/utils/share-artifact.ts` 仍在本地推导等级、主题 token、能力 gating 和分享产物
- `kaipai-frontend/src/api/level.ts` 虽约定了 `/api/card/*`、`/api/ai/*` 等接口，但演员端控制器尚未提供对应公开实现

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java` 已具备会员产品、账户、日志等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已具备模板、发布、回滚、主题 token、分享产物等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/membership/MembershipController.java`、`src/main/java/com/kaipai/module/controller/card/CardController.java` 当前仅保留控制器壳，没有演员端公开接口

### 3.3 后台治理

- 后台已具备会员产品 / 账户治理和模板发布 / 回滚治理入口
- 服务层已接入多类后台操作日志，具备后台自证和审计基础

### 3.4 联调现状

- 当前能确认“后台治理链路”相对完整
- 当前不能确认后台发布模板或开通会员后，演员端是否按同一份后端事实数据恢复到小程序页面

## 4. 联调结论

- 当前是否具备三端联调条件：`不具备`
- 已确认走通的链路：后台治理能力可独立成立，小程序页面可独立展示本地推导结果
- 当前不能宣告闭环的原因：演员端公开接口为空，且等级 / 模板 / 产物能力仍由前端本地规则库主导

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成会员与模板切片及执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 后台治理模型明确，但演员端统一输出契约未落地 |
| 后台治理入口可操作 | 已满足 | 会员产品、账户、模板、发布、回滚入口均已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 前台页面存在，但主要依赖本地 resolver，并非后端权威结果 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和发布 / 回滚具备，前台消费尚未完成统一收口 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立会员与模板切片状态基线 |

## 6. 当前阻塞项

- 演员端 `membership`、`card` 公开接口缺失
- 等级、会员、模板、分享产物 gating 仍由前端本地规则推导，没有单一后端权威源
- 模板发布 / 回滚后的前台恢复链路尚未完成真实联调

## 7. 下一轮最小动作

1. 先定义演员端会员状态、模板状态、主题 token、分享产物的统一响应模型
2. 在 `MembershipController`、`CardController` 暴露公开查询接口，并让小程序切到真实消费链路
3. 跑通一次“后台开通会员 / 发布模板 -> 小程序名片页、公开详情页、邀请页同步变化”的联调回填

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：当前阶段明确把“后台治理较完整、前台展示较丰富、演员端输出缺失”写入状态文档，避免把本地 resolver 误判成后端闭环
