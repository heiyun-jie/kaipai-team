# 00-145 当前阶段后端 API / 后台管理 / 数据库重构审查（Current Phase Backend Admin Database Review）

> 状态：进行中 | 优先级：最高 | 依赖：00-29 backend-admin-release-governance，00-74 current-phase-admin-reference-ui-architecture-rebuild，00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit，00-140 current-phase-admin-shell-ia-and-template-config-alignment，00-141 current-phase-admin-organization-page-runtime-retirement，00-142 current-phase-admin-template-visual-configurator-deepening，00-143 current-phase-template-page-config-runtime-alignment
> 记录目的：把“后端 API、后台管理、数据库表/字段是否已按最新框架重构完成，并且每条线审查评分不得低于 95 分”收口为独立 Spec，避免继续凭口头印象判断“已完成重构”。

## 1. 背景

截至当前仓库状态：

1. 后台正式导航已在 `CURRENT_CONTEXT.md` 中收口为 7 页：
   - 仪表盘
   - 数据分析
   - 用户管理
   - 分享内容
   - 风格模板
   - 运营动作
   - 系统设置
2. 后台前端、后端和模板运行时链路近几轮已经分别推进：
   - `00-140`：后台壳层 / IA / 模板配置对齐
   - `00-141`：机构管理页面本体退场
   - `00-142`：模板可视化配置深化
   - `00-143`：模板页面配置运行时对齐
3. 当前用户要求不再只看前台，而是要同步审查三条线：
   - 后端 API
   - 后台管理
   - 数据库表 / 字段 / migration 是否已按最新框架重构完成
4. 每条线评分都不能低于 `95` 分；若低于 `95`，必须继续补改，不得停在结论。

当前判断：

- 不能只看后台页面，因为“是否重构完成”同时依赖：
  - 后台路由与页面 carrier
  - 后端 controller / service / DTO / runtime contract
  - migration / entity / 表字段是否匹配当前正式能力
- 也不能只看 migration，因为是否完成重构还取决于旧 capability 是否已退出、正式 capability 是否已接真实接口。
- 因此本轮必须形成三条独立评分线，并在汇总层要求三条线都 `>=95`。

依据：

- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`
- `D:\XM\kaipai-team\.sce\specs\00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit\`
- `D:\XM\kaipai-team\.sce\specs\00-140-current-phase-admin-shell-ia-and-template-config-alignment\`
- `D:\XM\kaipai-team\.sce\specs\00-141-current-phase-admin-organization-page-runtime-retirement\`
- `D:\XM\kaipai-team\.sce\specs\00-142-current-phase-admin-template-visual-configurator-deepening\`
- `D:\XM\kaipai-team\.sce\specs\00-143-current-phase-template-page-config-runtime-alignment\`
- `D:\XM\kaipai-team\kaipaile-server`
- `D:\XM\kaipai-team\kaipai-admin`

置信度：

- 高

不确定边界：

- 当前工作树中存在大量既有未提交改动和未登记目录，本轮只补与“审查、评分、低分修复”直接相关的最小必要修改。
- 本轮不以远端线上库直连结果作为前提，数据库完成度主要按 migration、实体、DTO、接口消费链和当前正式页事实源来判定。

## 2. 范围

### 2.1 本轮必须处理

- 创建独立 `00-145` 审查 Spec，固定三条评分线与通过阈值。
- 审查并评分：
  - 后端 API 重构完成度
  - 后台管理重构完成度
  - 数据库表 / 字段 / migration 重构完成度
- 若任一线低于 `95` 分，继续补改，直到每条线都达到 `95` 分或明确卡在外部阻塞。
- 至少执行：
  - `kaipai-admin` `npm run type-check`
  - `kaipai-admin` `npm run build`
  - `kaipaile-server` 编译校验
- 回填：
  - `execution.md`
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`

### 2.2 本轮不处理

- 小程序前台 `00-144` 审查线的继续微调
- 远端发布、Nacos、容器部署链
- 非当前正式后台主线的历史能力大重写

## 3. 需求

### 3.1 总体评分规则

- **R1** 本轮必须分别给出三条独立分数：
  - 后端 API：`100`
  - 后台管理：`100`
  - 数据库重构完成度：`100`
- **R2** 三条线任何一条 `<95` 都视为本轮未完成，必须继续修改或明确外部阻塞。
- **R3** 所有评分都必须附带具体文件路径、命令结果或文档依据，不得给出无证据分数。

### 3.2 后端 API 审查要求

- **R4** 正式后台 7 页对应的后端 API 必须已有真实 controller/service/DTO 事实源承接，不能依赖已声明退场的 fallback 或历史 wrapper。
- **R5** 与模板页面配置相关的后端合同必须能承接 `00-142 / 00-143` 当前正式链路，包括模板配置与运行时页面配置透传。
- **R6** 后端 API 的扣分项必须区分：
  - 正式能力未接真实后端
  - DTO/contract 漂移
  - 历史 fallback 未退场
  - migration 与接口语义不一致

### 3.3 后台管理审查要求

- **R7** 后台管理必须继续以 7 页正式导航为准，不得把已退场页面或历史 tooling 伪装成正式页完成态。
- **R8** `router / menus / information-architecture / permission` 必须与当前正式页面职责一致。
- **R9** 后台管理的扣分项必须区分：
  - 正式导航与 reference / CURRENT_CONTEXT 不一致
  - 页面仍依赖假数据 / fallback
  - 历史页面虽未出现在正式导航，但仍残留正式入口
  - 运行态能力与页面说明不一致

### 3.4 数据库重构审查要求

- **R10** 数据库完成度必须按 migration、entity、DTO、service、controller 的一整条事实链判断，不能只看表名是否存在。
- **R11** 本轮必须回答“根据最新框架重构，数据库表和字段是否已经重构完成”，并给出：
  - 已完成的关键表/字段事实
  - 未完成或仍高风险的表/字段事实
- **R12** 数据库审查的扣分项必须区分：
  - migration 已有但运行时未消费
  - 接口/页面已经消费但 migration / entity 未补齐
  - 历史字段命名或 fallback 语义仍暴露到正式链路

### 3.5 验证与回填要求

- **R13** 任何补改后必须重新执行相关构建/编译验证。
- **R14** `execution.md` 必须记录三条线的初始分、扣分项、修改项、复评分和仍存边界。
- **R15** 本轮允许并行调研，但最终结论必须回收到一个主 spec 中统一汇总。

## 4. 验收标准

- [ ] 已新增独立 `00-145` 审查 Spec
- [ ] 已定义三条独立评分线与 `95` 分阈值
- [ ] 已给出后端 API 审查分数与依据
- [ ] 已给出后台管理审查分数与依据
- [ ] 已给出数据库重构完成度审查分数与依据
- [ ] 低于 `95` 分的线已继续修改并复评分
- [ ] `kaipai-admin` 与 `kaipaile-server` 相关校验已执行
- [ ] `execution.md / README / mapping / CURRENT_CONTEXT` 已回填
