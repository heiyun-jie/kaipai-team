# 00-109 当前阶段后台操作留痕审计降级态对齐（Current Phase Admin System Operation Logs Degraded State Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-108 current-phase-admin-system-ai-resume-failure-table-density-alignment
> 记录目的：在 `00-108` 完成 AI 简历治理失败双表收口后，把 `system/operation-logs` 当前“接口失败却伪装成空表”的运行态问题收口为显式降级视图，并顺带整理首屏空态表达。

## 1. 背景

截至 `2026-04-22`：

- 当前后台 `system/operation-logs` 仍是隐藏治理入口之一
- 当前页没有独立 spec，且运行态已经出现明确异常
- 当前系统设置页已把该事实源状态降级为“事实源异常”，但 `OperationLogsView.vue` 自身仍未承接同一边界

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-109\operation-logs-before.png`

真实浏览器 console 已确认：

- `Unhandled error during execution of mounted hook`
- `Error: 操作失败`
- 来源：`OperationLogsView.vue -> loadLogs -> fetchAdminOperationLogs`

当前差异：

1. 页面首屏显示 `0 条操作记录`，但真实原因是接口失败，不是“真实空数据”
2. 表格区域只剩默认 `No Data`，没有显式说明这是事实源异常
3. mounted hook 抛错导致页面运行态边界不清晰，容易误判为 UI 空态
4. 该页当前更缺的是**降级态与空态语义**，不是单纯 CSS 密度

### 当前量化

- overview：`1134 × 161`
- filterPanel：`1134 × 244`
- tableCard：`1134 × 302`
- tableHeader：`1084 × 53`
- emptyBlock：`1084 × 60`
- pager：`1084 × 49`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-109`
- 只处理 `system/operation-logs` 首屏列表区的运行态降级与空态承接：
  - `OperationLogsView.vue` 的 `loadLogs`
  - 首屏 overview 卡中的事实源状态文案
  - 表格区 empty / degraded state
  - mounted hook 异常的前端降级承接
- 用真实浏览器复核 `http://127.0.0.1:5100/system/operation-logs`

### 2.2 本轮不处理

- 不修后端 `operation-logs` 接口
- 不新增操作日志真实样本
- 不扩展新的审计模型、筛选字段或导出能力
- 不强行改详情抽屉结构；若没有真实样本，不做无依据视觉精修
- 不把该页重新放回正式 reference 导航

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `system/operation-logs` 的列表首屏降级态，不扩到其它治理页。
- **R2** 本轮判断必须优先服从真实运行态；修复前后截图、console 与量化都必须来自真实浏览器。
- **R3** 本轮必须显式承认当前事实源异常，不得继续把接口失败伪装成“正常空数据”。

### 3.2 降级态合同

- **R4** 当 `fetchAdminOperationLogs` 失败时，页面不得继续抛 mounted hook 未处理异常。
- **R5** 页面 overview 区必须把“事实源异常”和“真实空数据”区分开。
- **R6** 表格 empty 区必须显式说明当前是接口异常降级，而不是默认 `No Data`。
- **R7** 如果未来事实源恢复且返回空列表，页面仍应保留正常空态文案，不得把两种状态混淆。

### 3.3 治理要求

- **R8** 本轮不改筛选字段、API 查询参数、分页结构与详情接口签名。
- **R9** 本轮必须通过独立 `00-109` 承接，不继续混入 `00-108`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的截图、console 对比与量化结果写入 `execution.md`。

## 4. 验收标准

- [x] 已新增独立 `00-109` Spec，并明确它只处理操作留痕审计页降级态
- [x] `OperationLogsView.vue` 已显式承接接口失败，不再抛 mounted hook 未处理异常
- [x] 页面已区分“事实源异常”和“真实空数据”
- [x] 已通过真实浏览器复核 `system/operation-logs`
- [x] 已回填 README / mapping / CURRENT_CONTEXT / execution
