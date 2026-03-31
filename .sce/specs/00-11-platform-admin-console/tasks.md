# 并行执行总则

- `00-11` 允许按“框架壳层 / 业务页面 / 权限联调”三条工作流并行推进
- 页面设计不得脱离 `00-10` 的数据边界与接口分组
- 后台前端工程、权限矩阵、业务页面可并行，但最终必须统一收口

## Workstream A — 后台框架壳层

- [x] T1 基于当前对话补齐平台后台管理端的独立 Spec
- [x] T2 明确后台一级模块、二级菜单和页面职责边界
- [x] T3 输出后台前端工程初始化方案
- [x] T4 建立主框架 Layout、路由骨架、登录态与菜单装配方案

## Workstream B — 业务页面与信息架构

- [x] T5 明确后台角色与权限最小集合
- [x] T6 更新 Spec 索引，登记 `00-11 platform-admin-console`
- [x] T7 细化后台页面原型与字段清单
- [x] T8 建立后台查询接口与写操作接口清单
- [x] T9 细化后台 UI 设计规范与组件复用约束

## Workstream C — 权限与联调收口

- [x] T10 细化后台路由表、菜单权限码与操作权限码
- [x] T11 对齐各页面的查询 / 写入权限与高风险操作日志要求
- [x] T12 对齐 `00-10` 的表结构、接口清单与 `00-11` 的页面动作
- [x] T13 形成后台 Web 最终交付清单：页面、权限、接口、路由、阶段计划

## Implementation Backfill — 2026-03-31

- [x] B1 回填后台已实现接口状态：工作台、用户中心、实名认证、邀请裂变、会员中心、订单中心、退款中心、页面配置、系统管理
- [x] B2 回填新增后台接口：`/admin/referral/eligibility/{grantId}`、`/admin/membership/benefits` 及其写接口、`/admin/payment/orders`、`/admin/payment/transactions/{id}`、`/admin/refund/orders/{id}`、`/admin/refund/logs`
- [x] B3 运行态校验：`http://127.0.0.1:8010/api/v3/api-docs` 返回 `200`
- [x] B4 鉴权链路校验：`/api/admin/dashboard/overview`、`/api/admin/referral/eligibility`、`/api/admin/membership/benefits`、`/api/admin/payment/orders`、`/api/admin/refund/orders` 匿名访问返回 `401`，说明路由已挂载且被后台鉴权接管
- [x] B5 说明文档回填原因：此前优先闭环代码与接口实现，未同步把实现验收结果写回 Spec；本次已补齐
- [x] B6 带登录态接口冒烟：使用开发库临时后台账号 `smoke_admin` 登录成功，`/api/admin/auth/me` 与各后台列表接口返回 `200`
- [x] B7 空库详情接口受控冒烟：在无业务数据条件下，`/api/admin/referral/eligibility/{id}`、`/api/admin/payment/orders/{id}`、`/api/admin/payment/transactions/{id}`、`/api/admin/refund/orders/{id}`、`/api/admin/content/templates/{id}` 等详情接口进入 handler 并返回业务失败包体
- [x] B6 前端静态校验：`D:\XM\kaipai-team\kaipai-admin` 执行 `npm run type-check`、`npm run build` 通过
- [x] B7 当前交付页面回填：工作台、实名认证、异常邀请、会员产品、会员账户、支付订单、支付流水、退款单、退款日志、模板管理、后台账号、角色、操作日志
- [x] B8 当前已知残余项回填：角色权限编辑仍为多选模式；生产构建主 chunk 超过 `500 kB` 预警；尚缺真实后台账号的完整人工走查
