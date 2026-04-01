# 邀请裂变与邀请资格闭环状态回填

## 1. 归属切片

- `../slices/invite-referral-capability-slice.md`
- `../execution/invite/README.md`

## 2. 当前判定

- 回填日期：`2026-04-01`
- 当前判定：`局部完成`
- 一句话结论：小程序邀请页、登录页邀请码承接和后台风控 / 资格治理都已成形，但演员端邀请接口为空，且 `/api/invite/*` 与 `/referral` 契约断层仍未收口，无法确认真实邀请闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/api/invite.ts` 约定前端消费 `/api/invite/code`、`/api/invite/stats`、`/api/invite/records`、`/api/invite/qrcode`
- `kaipai-frontend/src/pages/login/index.vue` 已承接 `inviteCode` 注册链路
- `kaipai-frontend/src/pkg-card/invite/index.vue`、`src/pkg-card/membership/index.vue`、`src/stores/user.ts` 已消费邀请码、邀请统计与资格展示

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java` 当前仅注入服务，没有演员端公开接口映射
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java` 已具备记录、风险、策略、资格发放等后台治理接口
- 后台服务层已接入风控与资格相关操作日志，但未形成演员端统一消费契约

### 3.3 后台治理

- `kaipai-admin/src/views/referral/RiskView.vue` 已具备异常邀请筛选、详情、通过 / 作废 / 复核完成等治理入口
- 后台侧接口覆盖邀请记录、风险复核、资格发放和日志回看能力

### 3.4 联调现状

- 当前能确认“前台邀请展示能力”和“后台治理能力”分别存在
- 当前不能确认“邀请 -> 注册绑定 -> 记录生成 -> 风险复核 / 资格发放 -> 前台同步”的真实链路

## 4. 联调结论

- 当前是否具备三端联调条件：`不具备`
- 已确认走通的链路：登录页邀请码承接、小程序邀请页展示、后台异常邀请治理入口
- 当前不能宣告闭环的原因：演员端邀请接口未落地，且前端 `/api/invite/*` 与服务端 `/referral` 命名未统一

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已为邀请裂变补齐切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 后台治理侧清楚，演员端公开契约仍为空 |
| 后台治理入口可操作 | 已满足 | 风控、策略、资格发放等治理接口和页面已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 邀请页和登录页已落地，但真实后端接口未闭环 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和治理动作已接入，前台资格消费未与同一后端事实数据对齐 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立邀请切片的状态回填文档 |

## 6. 当前阻塞项

- `/api/invite/*` 与 `/referral` 的接口命名断层未收口
- 演员端邀请码、统计、记录、小程序码接口缺失
- 注册绑定邀请关系、风险命中和资格生效三类测试数据尚未建立统一联调样本

## 7. 下一轮最小动作

1. 先冻结邀请演员端契约，决定是兼容 `/api/invite/*` 还是前后端同步改名
2. 在演员端补齐邀请码、统计、记录、小程序码公开接口
3. 跑通一次“邀请 -> 注册 -> 记录生成 -> 风险复核 / 资格发放 -> 前台更新”联调，并回填结论

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先把“前台邀请页存在”和“后台治理存在”拆开记录，避免把两端各自完成误判成邀请闭环完成
