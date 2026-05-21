# 00-120 当前阶段后台 operation-logs 运行态刷新与浏览器复核（Current Phase Admin Operation Logs Runtime Refresh and Browser Revalidation）

> 状态：已完成 | 优先级：中高 | 依赖：00-118 current-phase-admin-operation-logs-fact-source-recovery-audit、00-119 current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup
> 记录目的：在 `00-118 / 00-119` 已完成代码级修复后，确认当前 `8010 / 5100` 运行态是否已吃到最新代码；若未吃到，则刷新运行态并用真实浏览器复核 operation-logs 与系统设置页。

## 1. 背景

截至 `2026-04-23`：

- 仓内代码已完成：
  - `00-118`：operation-logs 列表事实源恢复
  - `00-119`：系统设置页 operation-logs 摘要三态清理
- 但当前运行态核查已确认：
  - `http://127.0.0.1:8010/api/admin/system/operation-logs?pageNo=1&pageSize=1` 仍返回 `code=500`
  - `http://127.0.0.1:8010/api/admin/system/roles/ai-governance-matrix` 仍返回旧 schema 字段 `fallbackRoleCount`
  - `http://127.0.0.1:8010/api/admin/system/roles/recruit-governance-matrix` 仍返回旧 schema 字段 `fallbackRoleCount / pageFallbackRoleCount / actionFallbackRoleCount`

刷新前判断：

- 代码仓最新状态与 `8010` 运行态不一致
- 当前主问题已经不是“继续改代码”，而是“刷新运行态并做浏览器复核”

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-120`
- 停掉当前占用 `8010` 的旧后端实例
- 用当前仓代码重新启动后台到 `8010`
- 重新验证：
  - `/admin/system/operation-logs?pageNo=1&pageSize=1`
  - `/admin/system/roles/ai-governance-matrix`
  - `/admin/system/roles/recruit-governance-matrix`
- 用真实浏览器复核：
  - `/system/settings`
  - `/system/operation-logs`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不新增业务代码功能
- 不继续修改 operation-logs 后端实现
- 不做发布到其它环境

## 3. 需求

### 3.1 运行态合同

- **R1** 必须明确区分“仓内代码已修复”和“运行态仍是旧实例”。
- **R2** 本轮若发现 `8010` 仍是旧实例，必须先刷新运行态，再做浏览器验收。
- **R3** 刷新后必须重新核查 API 是否已返回当前新 schema / 新结果。

### 3.2 浏览器验证合同

- **R4** 必须基于真实浏览器复核系统设置页与 operation-logs 页面，不得只靠接口结果推断 UI 已恢复。
- **R5** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-120\`

## 4. 验收标准

- [x] 已新增独立 `00-120`
- [x] 当前 `8010` 已切到最新后端实例
- [x] operation-logs 列表接口已在 `8010` 返回 `code=200`
- [x] 浏览器截图已复核 `/system/settings` 与 `/system/operation-logs`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
