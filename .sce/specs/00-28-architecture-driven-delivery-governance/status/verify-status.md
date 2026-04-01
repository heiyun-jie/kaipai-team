# 实名认证闭环状态回填

## 1. 归属切片

- `../slices/verify-capability-slice.md`
- `../execution/verify/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：小程序认证页、后台审核页和演员端公开接口都已具备，但还没有完成一次真实“提交 -> 审核 -> 回写 -> 前台统一放行”联调，所以仍不能宣告闭环完成。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/verify/index.vue` 已提供认证资料填写、档案完成度校验和提交入口
- `kaipai-frontend/src/api/verify.ts` 约定前端消费 `/api/verify/status`、`/api/verify/submit`
- `kaipai-frontend/src/api/actor.ts`、`src/utils/runtime.ts` 已支持 `actor` 真接口分支，认证页计算档案完成度时不再只能依赖 mock actor 档案
- `kaipai-frontend/src/stores/user.ts`、`src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue` 已统一消费 `realAuthStatus` / `isCertified`

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java` 已暴露 `/verify/status`、`/verify/submit` 两个演员端公开接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/IdentityVerificationService.java`、`impl/IdentityVerificationServiceImpl.java` 已补齐演员端实名状态查询、提交、重复提交拦截、档案完成度校验和后台审核回写复用逻辑
- `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`、`ActorController.java` 已补齐认证页所需的 `/actor/profile/mine`、`/actor/profile/{userId}`、`/actor/{userId}` 最小 actor 输出
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java` 已具备列表、详情、通过、拒绝等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java` 已接入后台操作日志

### 3.3 后台治理

- `kaipai-admin/src/views/verify/VerificationBoard.vue` 已具备待审核 / 历史记录、详情抽屉、通过 / 拒绝动作
- 后台侧已覆盖权限码与审核操作按钮，具备治理入口基础

### 3.4 联调现状

- 当前能确认“前端提交接口 -> actorside verify service -> 后台审核 service”的源码链路已打通
- 当前还没有完成一轮真实环境联调，尚不能确认小程序请求、后台审核动作和前台刷新状态是否全部按预期工作

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：前台契约、演员端公开接口、后台审核治理侧能力都已落位
- 当前不能宣告闭环的原因：缺少真实环境下的一次提交 / 通过 / 拒绝 / 重提联调和回归验证

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 切片卡、执行卡已齐备 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端接口已补齐，并已在 JDK 21 环境下编译通过，但还缺真实联调 |
| 后台治理入口可操作 | 已满足 | 后台列表、详情、通过 / 拒绝已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 页面、状态消费和演员端接口均已落地，但真实请求未验证 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台权限与操作日志已接入，整体回写和加密口径仍待联调确认 |
| 文档、映射表、验证记录已回填 | 已满足 | `00-28` 已补齐切片、执行卡和当前状态基线 |

## 6. 当前阻塞项

- 真实环境下还没有完成一轮实名认证端到端联调
- `档案完成度 >= 70%` 的权威口径刚在服务端补齐，还需要和前台页面做一次对口验证

## 7. 下一轮最小动作

1. 准备一组真实测试数据，跑通“提交 -> 后台通过 / 拒绝 -> 小程序刷新状态”
2. 校验 `档案完成度 >= 70%`、重复提交拦截和审核回写口径
3. 回填一次真实联调结果，确认是否仍为局部完成

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先建立状态基线，结论以当前仓内代码现实为准，不把后台自证完成误判为实名认证闭环完成

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐演员端实名接口，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍未完成真实联调

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐认证页所需的 `actor/profile` 最小输出，`kaipai-frontend` 运行时也已放开 `actor` 真接口分支；`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺真实环境下“提交 -> 审核 -> 回写 -> 前台放行”的联调验证
