# 并行执行总则

- `00-28` 允许按“基础治理 / 平台核心域 / 小程序主线 / AI 增强”四条工作流推进
- 所有工作流必须以能力切片为最小推进单元，不得回退到按零散页面推进
- 后续项目排期、里程碑和验收应以本 Spec 为统一治理入口

## Workstream A — 治理入口与映射

- [x] T1 盘点当前整体架构入口：`00-10`、`00-11`、`00-27`、`05-11`
- [x] T2 新建 `00-28 architecture-driven-delivery-governance` Spec，补齐 requirements.md
- [x] T3 新建 `00-28 architecture-driven-delivery-governance` Spec，补齐 design.md
- [x] T4 将 00-28 登记到 Spec 索引、映射表和相关治理文档

## Workstream B — 推进模型与优先级

- [x] T5 定义当前阶段四组工作流和能力切片模板
- [x] T6 明确当前阶段优先级：平台基础能力 -> 演员增强主线 -> AI 增强
- [x] T7 给出一个可复用的切片示例：实名认证闭环
- [x] T8 补充 `slices/verify-capability-slice.md`
- [x] T9 补充 `slices/invite-referral-capability-slice.md`
- [x] T10 补充 `slices/membership-template-capability-slice.md`
- [x] T11 补充 `slices/ai-resume-polish-capability-slice.md`
- [x] T11-A 补充 `slices/crew-company-project-recruit-capability-slice.md`
- [x] T11-B 补充 `slices/login-auth-capability-slice.md`

## Workstream C — 项目推进收口

- [ ] T12 后续推动具体项目时，按 00-28 为每项能力建立“切片卡”
- [x] T12-A 已为“实名认证闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [x] T12-B 已为“邀请裂变与邀请资格闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [x] T12-B1 已为“邀请裂变与邀请资格闭环”补齐“微信官方小程序码收口”独立执行卡
- [x] T12-C 已为“会员能力与模板配置闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [x] T12-D 已为“AI 简历润色闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [x] T12-E 已为“剧组档案、项目、角色与投递最小连通闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [x] T12-F 已为“登录鉴权与前台会话闭环”补齐前端 / 后端 / 后台 / 联调四张执行卡
- [ ] T13 每轮实现完成后，回填该能力切片的联调结论和验收状态
- [x] T13-A 新建 `status` 目录与状态回填模板
- [x] T13-B 回填“实名认证闭环”当前联调结论与验收状态
- [x] T13-C 回填“邀请裂变与邀请资格闭环”当前联调结论与验收状态
- [x] T13-D 回填“会员能力与模板配置闭环”当前联调结论与验收状态
- [x] T13-E 回填“AI 简历润色闭环”当前联调结论与验收状态
- [x] T13-F 回填“剧组档案、项目与角色管理链路”当前联调结论与验收状态
- [x] T13-G 回填“招募角色与投递链路”当前联调结论与验收状态
- [x] T13-H 回填“登录鉴权与前台会话闭环”当前联调结论与验收状态
- [x] T13-I 补充 `status/project-structure-map.md`，沉淀整个项目结构与快速定位入口
- [x] T13-J 已把 invite / login-auth 的微信配置阻塞从“缺输入位”继续收口为“缺合法 secret 来源”，并回填到 `status/invite-status.md`、`status/login-auth-status.md`、`status/overall-architecture-assessment.md`
- [x] T13-K 已把 `00-29` 微信门禁单页 runbook 与“合法 secret 门禁”同步回填到 `phase-01-roadmap.md`、`execution/login-auth/real-env-validation-checklist.md`、`execution/invite/wxacode-execution-card.md`
- [x] T13-L 已把 membership `preview overlay` 的事实源边界固化为 `00-49` 独立 Spec，并同步回填路线图、状态卡与总体评估
- [x] T14 若主线优先级变化，优先更新 00-28，再调整局部业务 Spec
  - 2026-04-03：已通过 `00-48 current-phase-wechat-capability-deferral` 将 invite/login-auth 的微信能力降级为后续批次，并同步回写路线图与状态页
