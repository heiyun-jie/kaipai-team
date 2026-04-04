# 00-53 当前阶段剧组招募链路前端 Mock 退场（Current Phase Crew Recruit Mock Retirement）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-27 mini-program-frontend-architecture，00-29 backend-admin-release-governance
> 记录目的：把 `company / project / role / apply` 这条已完成真实后端接通的剧组招募链路，从“前端仍保留 mock 分支”推进到“前端只认真实接口”，避免当前阶段继续把显式 mock 演示分支误当成真实联通兜底。

## 1. 背景

`00-28` 已经把剧组档案、项目、角色、投递以及后台最小治理推进到真实接口和真实发布链路，但前端源码里仍残留一批并行 mock 分支：

- `kaipai-frontend/src/api/company.ts`
- `kaipai-frontend/src/api/project.ts`
- `kaipai-frontend/src/api/role.ts`
- `kaipai-frontend/src/api/apply.ts`
- `kaipai-frontend/src/mock/service.ts`

这会带来两个问题：

- 当前阶段已经有真实接口和真实状态卡，前端却仍保留“同一链路可退回 mock”的双轨事实源
- 后续读代码或排查问题时，容易把 `company / project / role / apply` 误判成“仍未真实接通，只是局部演示”

因此这轮需要用独立 Spec 把“前端残余 mock 退场”单独固化，而不是继续只在状态卡里口头说明。

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-53` Spec，记录当前阶段剧组招募链路前端 mock 退场边界
- 移除 `company / project / role / apply` API 模块中的 `useApiMock(...)` 分支
- 清理 `src/mock/service.ts` 中已无运行时入口的剧组招募 mock 服务函数
- 清理 `src/utils/runtime.ts` 中已无使用方的招募能力 mock capability 定义
- 回填 `00-28` 状态文档、路线图 / 任务或总体评估中的当前判定
- 更新 Spec 索引与映射

### 2.2 本轮不处理

- 删除全仓所有 mock 数据或全局 mock 总闸
- 删除与 invite、verify、membership、AI 等其他能力域有关的 mock 服务
- 重做剧组招募的产品边界、项目域建模或二期“平台创建通告”方案
- 直接把 `project` 兼容层升级成独立数据模型

## 3. 需求

### 3.1 当前阶段前端事实源

- **R1** 当前阶段 `company / project / role / apply` 前端 API 不得继续保留 `useApiMock(...) ? mock : real` 双轨分支。
- **R2** 当前阶段这四条链路必须直接调用真实接口：
  - `/api/company`
  - `/api/project`
  - `/api/role`
  - `/api/apply`
- **R3** 当前阶段如果接口、环境或鉴权有问题，页面必须直接暴露真实错误，不得再由前端局部 mock 演示分支掩盖。

### 3.2 Mock 代码退场边界

- **R4** `src/mock/service.ts` 中已无运行时入口的剧组招募 mock 服务必须删除，避免仓内继续存在“死而未退”的假事实源。
- **R5** `src/utils/runtime.ts` 中已无使用方的 `company / project / role / roleRead / apply` mock capability 必须同步清理，避免运行时能力表继续暗示这些链路支持 mock 兜底。
- **R6** 其他能力域若仍处于显式 mock 演示态，不在本轮顺手改写，防止范围失控。

### 3.3 治理回填

- **R7** 必须通过独立 Spec 固化这次 mock 退场，不得只改代码。
- **R8** 必须同步回填 `00-28` 状态页 / 总体评估，让后续读文档的人能直接看出：剧组招募链路的前端 mock 已退场，剩余问题已转向真实运行时与长期兼容层治理。

## 4. 验收标准

- [x] 已新增独立 `00-53` Spec 并登记索引与映射
- [x] `company.ts / project.ts / role.ts / apply.ts` 已不再保留 `useApiMock(...)` 分支
- [x] `src/mock/service.ts` 已删除对应剧组招募 mock 服务与废弃辅助函数
- [x] `src/utils/runtime.ts` 已删除无使用方的招募 capability mock 定义
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 至少一张状态页和总体评估已明确回填“前端 mock 已退场”的当前判定
