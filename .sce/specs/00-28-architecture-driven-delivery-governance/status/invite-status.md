# 邀请裂变与邀请资格闭环状态回填

## 1. 归属切片

- `../slices/invite-referral-capability-slice.md`
- `../execution/invite/README.md`

## 2. 当前判定

- 回填日期：`2026-04-01`
- 当前判定：`局部完成`
- 一句话结论：小程序邀请页、登录页邀请码承接、后台风控 / 资格治理，以及演员端 `/invite/*` 兼容接口现已齐备，但“邀请 -> 注册绑定 -> 风控 / 资格发放 -> 前台更新”的真实闭环还没跑通。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/api/invite.ts` 约定前端消费 `/api/invite/code`、`/api/invite/stats`、`/api/invite/records`、`/api/invite/qrcode`
- `kaipai-frontend/src/pages/login/index.vue` 已承接 `inviteCode` 注册链路
- `kaipai-frontend/src/pkg-card/invite/index.vue`、`src/pkg-card/membership/index.vue`、`src/stores/user.ts` 已消费邀请码、邀请统计与资格展示

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java` 已兼容 `/referral` 与 `/invite` 两套前缀，并补齐 `code / stats / records / qrcode` 最小演员端查询接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/InviteCodeService.java`、`InviteCodeServiceImpl.java` 已补齐邀请码生成 / 复用逻辑
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRecordService.java`、`ReferralRecordServiceImpl.java` 已补齐邀请统计和邀请记录输出
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java` 已具备记录、风险、策略、资格发放等后台治理接口
- 后台服务层已接入风控与资格相关操作日志，但未形成演员端统一消费契约
- `2026-04-01` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- `kaipai-admin/src/views/referral/RiskView.vue` 已具备异常邀请筛选、详情、通过 / 作废 / 复核完成等治理入口
- 后台侧接口覆盖邀请记录、风险复核、资格发放和日志回看能力

### 3.4 联调现状

- 当前能确认“前台邀请展示能力”、“后台治理能力”和“演员端查询接口”三段能力都已落位
- 当前不能确认“邀请 -> 注册绑定 -> 记录生成 -> 风险复核 / 资格发放 -> 前台同步”的真实链路

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：登录页邀请码承接、小程序邀请页展示、后台异常邀请治理入口、演员端 `/invite/*` 查询接口
- 当前不能宣告闭环的原因：注册绑定、记录生成、风险复核、资格发放与前台消费还没有完成真实联调

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已为邀请裂变补齐切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 查询接口已落地，但注册绑定和资格流转链路仍待联调确认 |
| 后台治理入口可操作 | 已满足 | 风控、策略、资格发放等治理接口和页面已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 邀请页、登录页和演员端查询接口都已落地，但真实业务链路未闭环 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和治理动作已接入，资格发放与前台消费仍待联调 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立邀请切片的状态回填文档 |

## 6. 当前阻塞项

- 注册绑定邀请关系、风险命中和资格生效三类测试数据尚未建立统一联调样本
- 小程序码当前仍是占位返回，未接真实二维码生成能力
- 邀请资格发放虽然后台能力已具备，但前台未完成同一事实数据消费验证

## 7. 下一轮最小动作

1. 跑通一次“邀请 -> 注册 -> 记录生成 -> 风险复核 / 资格发放 -> 前台更新”联调，并回填结论
2. 校验注册绑定邀请关系是否稳定落库，以及风险状态 / 资格状态是否正确影响前台展示
3. 视联调结果决定是否需要把占位二维码替换成真实生成链路

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先把“前台邀请页存在”和“后台治理存在”拆开记录，避免把两端各自完成误判成邀请闭环完成

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐演员端 `/invite/*` 兼容查询接口，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍缺真实闭环联调
