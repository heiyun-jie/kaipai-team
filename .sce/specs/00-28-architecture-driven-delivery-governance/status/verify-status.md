# 实名认证闭环状态回填

## 1. 归属切片

- `../slices/verify-capability-slice.md`
- `../execution/verify/README.md`

## 2. 当前判定

- 回填日期：`2026-04-01`
- 当前判定：`局部完成`
- 一句话结论：小程序认证页和后台审核页都已具备，但演员端公开接口还没暴露，无法确认“提交 -> 审核 -> 回写 -> 前台统一放行”的真实闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/verify/index.vue` 已提供认证资料填写、档案完成度校验和提交入口
- `kaipai-frontend/src/api/verify.ts` 约定前端消费 `/api/verify/status`、`/api/verify/submit`
- `kaipai-frontend/src/stores/user.ts`、`src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue` 已统一消费 `realAuthStatus` / `isCertified`

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java` 当前只有 `/verify` 控制器壳，未暴露 `status / submit` 等演员端接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java` 已具备列表、详情、通过、拒绝等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java` 已接入后台操作日志

### 3.3 后台治理

- `kaipai-admin/src/views/verify/VerificationBoard.vue` 已具备待审核 / 历史记录、详情抽屉、通过 / 拒绝动作
- 后台侧已覆盖权限码与审核操作按钮，具备治理入口基础

### 3.4 联调现状

- 当前能确认“后台治理页存在”和“小程序消费实名状态”的局部链路
- 当前不能确认小程序提交的真实接口是否能落库，也不能确认后台审核后的状态回写是否已被演员端接口消费

## 4. 联调结论

- 当前是否具备三端联调条件：`不具备`
- 已确认走通的链路：后台审核治理侧能力、前台认证状态消费侧能力分别已落位
- 当前不能宣告闭环的原因：演员端 `/api/verify/status`、`/api/verify/submit` 契约尚未在公开控制器层落地，端到端链路缺少真实接口锚点

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 切片卡、执行卡已齐备 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 后台审核链路存在，但演员端公开接口未闭合 |
| 后台治理入口可操作 | 已满足 | 后台列表、详情、通过 / 拒绝已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 页面和状态消费已落地，但真实接口未验证 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台权限与操作日志已接入，整体回写和加密口径仍待联调确认 |
| 文档、映射表、验证记录已回填 | 已满足 | `00-28` 已补齐切片、执行卡和当前状态基线 |

## 6. 当前阻塞项

- 演员端实名认证公开接口缺失，前后端无法按真实契约联调
- `档案完成度 >= 70%` 的权威口径仍需要在前后端之间收口
- 审核通过 / 拒绝后的 `user` 与 `actor_profile` 回写结果未完成端到端确认

## 7. 下一轮最小动作

1. 在演员端补齐 `/verify/status`、`/verify/submit` 公开接口，并与小程序现有契约对齐
2. 准备一组真实测试数据，跑通“提交 -> 后台通过 / 拒绝 -> 小程序刷新状态”
3. 回填一次真实联调结果，确认是否仍为局部完成

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先建立状态基线，结论以当前仓内代码现实为准，不把后台自证完成误判为实名认证闭环完成
