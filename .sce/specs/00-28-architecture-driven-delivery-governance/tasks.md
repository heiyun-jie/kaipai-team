# 并行执行总则

- `00-28` 允许按“基础治理 / 平台核心域 / 小程序主线 / AI 增强”四条工作流推进
- 所有工作流必须以能力切片为最小推进单元，不得回退到按零散页面推进
- 后续项目排期、里程碑和验收应以本 Spec 为统一治理入口

## Workstream A — 治理入口与映射

- [x] T1 盘点当前整体架构入口：`00-10`、`00-11`、`00-27`；旧 fortune / 命理域退场由 `00-149` 接管
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
- [x] T13-M 已把 AI 简历治理协同升级入口固化为 `00-50` 独立 Spec，并同步回填路线图、状态卡、执行入口与总体评估
- [x] T13-N 已把 verify 页面级证据入口固化为标准脚本，并通过真实小程序 / 后台页面样本将 verify 从“局部完成”回填为“闭环完成”
- [x] T13-O 已把 invite 前端未再使用的二维码 / share-state 旧兜底导出清理并回填状态卡，当前 invite 本地补链路已进一步收口到 mock 分支
- [x] T13-P 已把 login-auth 当前阶段的手机号登录 / 会话恢复样本固化为标准脚本，并用真实环境样本回填状态卡与总体评估
- [x] T13-Q 已把 login-auth 当前阶段的手机号注册 + `inviteCode` 样本固化为标准脚本，并用真实环境样本回填状态卡与总体评估
- [x] T13-R 已把 login-auth 当前阶段的小程序页面证据固化为标准脚本，并用真实页面样本回填状态卡与总体评估
- [x] T13-S 已把 login-auth 的开发态 `sendCode` 口径固化为 `00-51` 独立 Spec，并将 login-auth 当前阶段状态从“局部完成”推进为“当前阶段闭环完成”
- [x] T13-T 已把 invite 当前阶段页面边界固化为 `00-52` 独立 Spec，并同步回写路线图、invite 状态卡、总体评估与 `05-12` 历史口径
- [x] T13-U 已把 recruit 当前阶段前端 mock 退场固化为 `00-53` 独立 Spec，并同步回写剧组 / 招募状态卡、总体评估与映射
- [x] T13-V 已把 actor 当前阶段前端 mock 退场固化为 `00-54` 独立 Spec，并同步回写演员主线相关状态与总体评估
- [x] T13-W 已把 invite / verify / fortune 当前阶段前端 mock 退场固化为 `00-55` 独立 Spec，并同步回写对应状态页、总体评估与映射
- [x] T13-X 已把 level / card / ai 当前阶段前端运行时 mock 退场固化为 `00-56` 独立 Spec，并同步回写 membership / AI 状态页、总体评估与映射
- [x] T13-Y 已把 session / upload 当前阶段运行时边界对齐固化为 `00-57` 独立 Spec，并同步回写 login-auth / upload 相关状态页、总体评估与映射
- [x] T13-Z 已把 auth 当前阶段 runtime capability 表退场固化为 `00-58` 独立 Spec，并同步回写 login-auth / membership 状态页、总体评估与映射
- [x] T13-AA 已把 AI 当前阶段手动 `governance-sweep` 升级为 `00-59` 独立 Spec，并同步回写路线图、AI 状态卡、总体评估、执行入口与映射
- [x] T13-AB 已按 `00-29` 标准发布链完成 `00-59` 的目标环境发布、Nacos 启用、运行时重建与首轮定时样本回填，并同步更新路线图、AI 状态卡、执行入口与总体评估
- [x] T13-AC 已把 AI 当前剩余“真实通知基础设施 / 回执事实源”阻塞固化为 `00-60` 独立 Spec，并同步回写路线图、AI 状态卡、总体评估、执行入口与映射
- [x] T13-AD 已把 auth 当前阶段显式 mock 主链退场固化为 `00-61` 独立 Spec，并同步回写 login-auth 执行入口、状态页、总体评估与映射
- [x] T13-AE 已把用户定义的最小分享名片 MVP 边界固化为 `00-62` 独立 Spec，并同步回写路线图、总体评估、结构图与映射
- [x] T13-AF 已把 `00-62` 当前阶段真实代码结构回填为独立状态卡与最小治理样本，并同步修正 `00-28` 对其的总体评估口径
- [x] T13-AG 已把 `00-62` 默认普通卡初始化 / 补偿策略补成独立后台治理入口，并同步回写状态卡、任务与执行记录
- [x] T13-AH 已把 `00-62` 历史 / 已联系 / 后台联系方式的场景展示文案进一步收口为单一来源，并同步回写状态卡、任务与执行记录
- [x] T13-AI 已把 `00-62` 的真实持卡实例补成后台“分享卡治理”入口，并同步回写状态卡、任务与执行记录
- [x] T13-AJ 已把 share-card 的发布后总控结构固化为统一模板，并同步回写 runbook、状态卡、执行索引与 `00-62` 历史
- [x] T13-AK 已把 login-auth / `00-51 formal-sms` 的 future batch 发布后总控读法对齐到统一模板，并同步回写执行卡、状态卡与 spec 历史
- [x] T13-AL 已盘点 membership / invite / verify 对统一发布后控制卡模板的接入成熟度，并同步回写 00-28 总览层推荐顺序
- [x] T13-AM 已给 membership 补齐第一版发布后总包索引与检查清单，并把其状态推进到“可按标准入口接控制卡”
- [x] T13-AN 已给 membership 落第一版手工 `releaseGoNoGoCard / operatorRunCard`，并固定当前人工 Go/No-Go 结论
- [x] T13-AO 已把“档案编辑 / 分享卡编辑 / 公开分享页”之间的最新态遗漏固化为 `00-63` 独立 Spec，并将前端读取主链收口为共享 latest snapshot loader
- [x] T13-AP 已把 actor-card 编辑页边界噪音与编辑能力补齐问题固化为 `00-64` 独立 Spec，并与多实例模型重构边界拆开
- [x] T13-AQ 已把“新增分享卡片必须新增实例存储”的模型重构问题固化为 `00-65` 独立 Spec，明确模板资格与卡片实例解耦
- [x] T13-AR 已把“分享链演员档案断裂 + 分享海报门禁不一致”的线上问题固化为 `00-68` 独立 Spec，并同步回写 share-card 状态卡与总体评估
- [x] T13-AS 已把“当前分享 + 记录 + 我的 + 渠道分析”架构与旧代码删除计划固化为 `00-69` 独立 Spec，并同步回写总体评估入口
- [x] T13-AT 已把 `_-_.html` 的 7 页参考原型固化为 `00-70` 独立 Spec，并记录首轮 5 个 active 页面 UI 落地结果与剩余 2 个预览页待办
- [x] T14 若主线优先级变化，优先更新 00-28，再调整局部业务 Spec
  - 2026-04-03：已通过 `00-48 current-phase-wechat-capability-deferral` 将 invite/login-auth 的微信能力降级为后续批次，并同步回写路线图与状态页
  - 2026-04-04：已通过 `00-52 current-phase-invite-record-page-boundary-alignment` 将 invite 当前阶段边界收口为“记录页 + 登录承接邀请码 + 分享入口分散在 actor-card/membership”
  - 2026-04-04：已通过 `00-53 current-phase-crew-recruit-mock-retirement` 将已真实接通的 `company / project / role / apply` 前端 mock 分支收口为只认真实接口
  - 2026-04-04：已通过 `00-54 current-phase-actor-mainline-mock-retirement` 将已真实接通的 `actor search / detail / mine / update` 前端 mock 分支收口为只认真实接口
  - 2026-04-04：已通过 `00-55 current-phase-invite-verify-fortune-mock-retirement` 将已稳定接通的 `invite / verify / fortune` 前端 mock 分支收口为只认真实接口
  - 2026-04-04：已通过 `00-56 current-phase-level-card-ai-runtime-mock-retirement` 将已稳定接通的 `level / card / ai` 前端运行时双轨与 personalization 本地 fallback 收口为只认真实接口
  - 2026-04-04：已通过 `00-57 current-phase-session-upload-runtime-boundary-alignment` 将 `userInfo / roleSwitch / upload` 从独立 runtime capability 收口为“显式 mock 演示态或真实接口”
  - 2026-04-04：已通过 `00-59 current-phase-ai-governance-scheduled-sweep` 将 AI 当前阶段手动 `governance-sweep` 收口为服务端内建、可配置、可禁用、可审计的定时任务入口
  - 2026-04-04：已通过 `00-60 current-phase-ai-governance-real-notification-foundation` 将 AI 当前剩余主阻塞进一步收口为“真实通知基础设施 / 回执事实源”
  - 2026-04-04：已通过 `00-58 current-phase-auth-runtime-boundary-alignment` 删除前端 runtime capability 表，并将 `auth / wechatAuth` 收口为“显式 mock 演示态总闸 + 微信独立配置门禁”
  - 2026-04-04：已通过 `00-61 current-phase-auth-explicit-mock-retirement` 删除前端 auth 显式 mock 主链、本地 mock 会话恢复与 auth mock 文件，当前 `VITE_USE_MOCK=true` 也不能再伪装登录域可用
  - 2026-04-04：已通过 `00-62 current-phase-minimal-share-card-mvp-alignment` 将当前阶段产品主线改写为“可分享卡片 / 查看历史 / 个人中心”三 Tab MVP，并把首页公开列表、profile/card 混用、默认普通卡、邀请解锁风格与联系方式申请/同意闭环统一收口到新主架构
  - 2026-04-06：已把 share-card 的发布后总控结构抽取为统一模板 `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`，并将 login-auth / `00-51 formal-sms` future batch 默认读法统一到 `releaseGoNoGoCard / operatorRunCard`
  - 2026-04-06：已继续盘点 `membership / invite / verify` 的模板接入成熟度，并将“membership 优先接入、verify 维护态可后补、invite 先完成边界治理”回写到 00-28 总览层
  - 2026-04-06：已通过 `00-63 current-phase-share-card-latest-state-alignment` 将“档案编辑 / 分享卡编辑后公开分享页未稳定读取最新后端状态”的问题提升为独立 Spec，并把 `detail / actor-card` 的 latest-state 读链收口到共享 loader
  - 2026-04-06：已通过 `00-64 current-phase-actor-card-editor-boundary-alignment` 将 actor-card 页旧会员/命理/audience 残留与代表照片/配色/预览名片缺口提升为独立 Spec
  - 2026-04-06：已通过 `00-65 current-phase-share-card-multi-instance-refactor` 将“新增分享卡片却复用同模板单实例”的模型问题提升为独立 Spec，明确模板资格与卡片实例解耦
  - 2026-04-13：已通过 `00-68 current-phase-share-runtime-and-poster-capability-alignment` 将“分享链 `shareCard -> actor detail` 断裂”和“分享海报能力/按钮与当前产品要求不一致”的线上问题提升为独立 Spec
  - 2026-04-19：已通过 `00-69 current-phase-share-analytics-architecture-refactor` 将“当前分享 + 记录 + 我的 + 控制台/用户中心 + 统计主链”架构与旧代码删除计划提升为独立 Spec
  - 2026-04-20：已通过 `00-70 current-phase-share-prototype-ui-implementation` 将 `_-_.html` 的 7 页参考原型提升为当前前端可见层独立 Spec，并记录首轮 `login / home / history / mine / card-list` 的 UI 落地与 `detail / actor-card` 两个预览页待办
  - 2026-04-04：已通过 `00-59 current-phase-ai-governance-scheduled-sweep` 将 AI 当前阶段手动 `governance-sweep` 收口为服务端内建、可配置、可禁用、可审计的定时任务入口
