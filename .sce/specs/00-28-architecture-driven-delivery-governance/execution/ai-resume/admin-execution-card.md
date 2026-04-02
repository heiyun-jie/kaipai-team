# AI 简历润色闭环后台执行卡

## 1. 执行卡名称

AI 简历润色闭环 - 后台管理端执行卡

## 2. 归属切片

- `../../slices/ai-resume-polish-capability-slice.md`

## 3. 负责范围

- AI 配额策略、失败样本、敏感内容命中、调用日志的治理入口规划
- 后台菜单、权限和占位治理入口
- 先期 AI 运维能力与现有系统日志能力的衔接
- 规则变更与前台文案 / gating 的同步治理

## 4. 不负责范围

- 小程序编辑页 AI 面板与 patch 交互
- 大模型调用、配额扣减、patch 生成的后端实现
- 真实成本结算与财务对账
- 没有后端数据支撑的假运营页

## 5. 关键输入

- 上位 Spec：
  - `00-11 platform-admin-console`
  - `05-04 ai-resume-polish`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-admin/src/router/index.ts`
  - `kaipai-admin/src/constants/menus.ts`
  - `kaipai-admin/src/constants/permission.ts`
  - `kaipai-admin/src/constants/permission-registry.ts`
  - `kaipai-admin/src/views/system/RolesView.vue`
  - `kaipai-admin/src/views/system/AiResumeGovernanceView.vue`
  - `kaipai-admin/src/views/system/OperationLogsView.vue`
  - `role-authorization-closure.md`
  - 备注：当前后台已存在独立 AI 治理页、治理动作审计、角色页授权矩阵与建议授权包，并已补责任人目录 / 升级目标目录与失败样本分派处理人；剩余缺口主要是目标环境角色绑定、fallback 下线验证和更完整协同流转

## 6. 目标交付物

- 平台侧已存在可用的 AI 治理入口，而不是完全无后台承接
- 能回看 AI 配额摘要、失败样本、敏感内容命中、调用结果和治理动作审计
- 失败样本的责任人分派与升级目标目录必须有独立治理接口，不得继续依赖 `admin-users / roles` 页面权限临时兜底
- 即使本轮不上完整 AI 运维页，也要明确目标环境角色绑定、权限迁移和 fallback 下线口径
- 角色管理页要能低成本完成 AI 治理权限分配，而不是要求操作者手工背权限码
- AI 规则变更时，后台能同步推动前台 gating 与文案更新
- 后台不再对 AI 能力“完全不可见”

## 7. 关键任务

1. 明确 AI 治理入口落点
   - 当前已挂到系统治理入口 `/system/ai-resume-governance`
   - 需要继续收口它与 `/system/operation-logs` 的职责边界
2. 规划配额策略入口
   - 不同等级 / 会员态配额策略
   - 是否允许人工补发或调整
   - 配额策略变更的审计要求
3. 规划失败样本与敏感内容回看入口
   - 超时样本
   - 敏感词命中
   - 不可解析 patch
   - 失败重试或人工处理建议
   - 责任人分派与升级目标目录
4. 对齐权限与菜单
   - 先定义页面权限、动作权限和菜单权限
   - 没有权限的账号不能回看 AI 样本或调整策略
   - 角色管理页要有可复用的建议授权口径，避免真实授权继续依赖口头约定
5. 与现有系统日志衔接
   - 当前已通过治理页直接回看 AI 相关操作日志
   - 需要避免继续把操作日志页当成 AI 治理主入口
6. 收口角色矩阵与 fallback 退场条件
   - 明确“AI 治理只读 / AI 治理处置”两类建议角色包
   - 明确何时允许下线 `page.system.operation-logs` 对 AI 治理入口的兼容兜底

## 8. 依赖项

- 后端必须先产出 AI 配额、调用日志、失败原因、历史回滚等数据
- 若后台只做页面壳而没有后端数据，将无法形成真实治理入口
- 目标环境需要真实角色绑定与重新登录验证，否则无法判断 fallback 是否还能下线

## 9. 验证方式

- 后台存在明确的 AI 治理入口
- 可回看失败样本、敏感内容命中、调用日志和治理动作审计
- 无权限账号看不到 AI 治理入口或相关动作
- 角色管理页可以直接完成 AI 新权限分配，并能区分只读与处置角色
- 规则变更后，前台文案和 gating 更新有明确同步流程

## 10. 完成定义

- 后台不再对 AI 能力完全失明
- AI 配额与异常治理至少有第一版承接入口
- 菜单、权限、日志、样本回看有明确路径
- AI 新权限已有明确角色矩阵和分配入口
- 已明确何时允许下线 `page.system.operation-logs` 对 AI 治理入口的兼容兜底
- 可支撑 AI 简历能力上线后的基本运营与风控
- 即使本轮不上完整运维页，也已完成治理面的最小闭环设计

## 11. 风险与备注

- 当前若只保留 `operation-logs` 兼容兜底而不做真实角色绑定，AI 治理入口会长期挂靠旧权限，无法判断哪些账号真正具备 AI 处置资格
- 若责任人分派继续直接复用 `admin-users / roles` 页面权限，AI 治理页会出现“看得到失败样本但拿不到协同目录”的隐性 403 假闭环
- 若只做前台 AI 功能不做后台治理，配额投诉、异常 patch、敏感内容命中都无处处理
- 若本轮只停留在“权限码已定义”而不做真实角色分配与账号验证，仍属于治理假闭环
