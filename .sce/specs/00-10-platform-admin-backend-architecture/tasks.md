# 并行执行总则

- `00-10` 允许按“数据 / 后端 / 集成”三条工作流并行推进
- 各工作流应避免修改同一份交付物，减少合并冲突
- 以本 Spec 为统一基线，`00-11` 的后台页面与权限拆分需与本 Spec 保持一致

## Workstream A — 数据与 DDL

- [x] T1 盘点本轮对话形成的平台后台、数据库、会员、订单、退款、资格与模板配置结论
- [x] T2 新建 `00-10 platform-admin-backend-architecture` Spec，沉淀统一架构基线
- [x] T3 基于本 Spec 输出首版 MySQL DDL
- [x] T4 评估并补齐现有 `user`、`actor_profile`、`cooperation_order` 的字段扩展方案
- [x] T5 细化各表唯一约束、索引策略、状态枚举和字段命名规范

## Workstream B — 服务端模块与接口

- [x] T6 更新 Spec 索引，登记 00-10 为全局架构治理 Spec
- [x] T7 细化服务端模块目录、Entity / Mapper / Service / Controller 清单
- [x] T8 建立实名认证、邀请裂变、会员、支付、退款、模板配置的接口清单
- [x] T9 定义 `/api/**` 与 `/api/admin/**` 的边界和聚合 Facade 清单

## Workstream C — 后台协同与集成

- [x] T10 细化后台 Web 信息架构、菜单与权限矩阵
- [x] T11 对齐 `00-11` 的后台页面能力与 `00-10` 的表结构/接口模型
- [x] T12 输出后台优先级实施计划与里程碑
- [x] T13 形成跨工作流的最终收口文档：DDL + 接口 + 后台页面映射

## Runtime Backfill — 2026-03-31

- [x] R1 使用当前代码重新打包并重启后端，确认最新服务运行在 `http://127.0.0.1:8010/api`
- [x] R2 运行态校验：`/api/v3/api-docs` 返回 `200`
- [x] R3 OpenAPI 校验通过的后台接口：`/admin/dashboard/overview`、`/admin/referral/eligibility`、`/admin/referral/eligibility/{grantId}`、`/admin/membership/benefits`、`/admin/membership/benefits/{id}`、`/admin/membership/benefits/{id}/enable`、`/admin/payment/orders`、`/admin/payment/transactions/{id}`、`/admin/refund/orders/{id}`、`/admin/refund/logs`、`/admin/content/templates/{id}`、`/admin/system/admin-users`
- [x] R4 鉴权链路校验：关键后台路由匿名访问返回 `401`，说明接口已连通且接入后台安全链
- [x] R5 本次回填用于收口“代码已落地但 Spec 未登记”的差异，后续接口批次必须同步更新 Spec
- [x] R6 开发库冒烟账号已建立：补充 `ADMIN` 角色与 `smoke_admin` 账号，用于后台接口联调与运行态验证
- [x] R7 带 Token 冒烟结果：`/api/admin/auth/me`、工作台、用户中心、实名认证、邀请裂变、会员中心、订单中心、退款中心、页面配置、系统管理列表接口均返回 `200`
- [x] R8 空库详情受控验证：无业务数据时，详情接口返回业务失败包体而非 `404` 路由缺失，证明 controller / service / 鉴权链路连通
