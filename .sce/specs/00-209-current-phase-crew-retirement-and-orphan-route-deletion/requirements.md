# 00-209 当前阶段剧组能力退场与不可达路由删除

> 状态：执行中。本 Spec 包含**实际删除动作**，前置回滚点已按用户要求先行落地（见 §5）。
>
> 立项依据：用户书面指令「一起删除，删除之前需要提交 git，方便找回，创建 specs 开始执行吧。」
> 产品裁决依据：用户书面结论「剧组下线了」——这一句把 `00-208` 挂起的唯一待裁决问题（剧组是下线还是休眠）关闭为**下线**。

## 1. 概述

`00-208` 已用可复现脚本建立事实基线：`pages.json` 登记 43 页，从 4 个 tabBar 入口出发可达 20 页、不可达 23 页；四类跳转边（字面路径、路径工厂、组件 props、全动态）全部覆盖后结论不变；9 处无法静态解析的动态跳转，其宿主页本身全部落在不可达集合内，因此无法反向救活任何孤儿页。

本 Spec 执行该基线对应的退场动作，范围三块：

1. **23 个不可达页**的登记与文件删除（含整条剧组主链、`pkg-card` 旧演员卡链、`pkg-profile` 作品链、`pkg-tools` 设置页）。
2. **60 个连带死模块**的删除（api / components / utils / types / constants / composables / stores / 页面级子模块）。
3. **`UserRole.Crew` 运行态路径的切除**（注册入口、store computed、导航门禁），但**保留枚举成员本身**。

本 Spec **不包含后端退场**。`/api/crew`、`/api/project`、`/api/role`、`/api/apply` 及其数据表一律不动，需单独授权。

## 2. 用户故事

作为项目接手方，我需要把已下线的剧组能力与不可达路由从运行态中真正移除，而不是继续以"登记着但进不去"的状态留在包体里，这样包体、类型检查与后续治理才有干净基线。

作为决策方，我需要删除动作有明确回滚点与可复核清单，任何一条删除都能追溯到脚本输出，删错能一条命令找回。

## 3. 功能需求

### 3.1 删除范围以落盘清单为唯一真源

- WHEN 执行任何删除 THEN 删除对象必须逐条出自 `00-208` 闭包脚本产出的清单，禁止凭记忆或凭文件名语义增删。
- WHEN 清单与代码现状冲突 THEN 以重跑脚本的结果为准，不以本 Spec 正文的历史数字为准。
- WHEN 报告体积 THEN 使用真实字节（`stat` / `du --apparent-size`），禁用 `du` 默认块大小口径。

**已核实基线数字**：登记 43 页 → 删 23 页 / 留 20 页；死代码 83 个文件 = 23 页 + 60 连带模块；总计 `653839` 字节（页面 `471970` + 连带 `181869`）。

**验收标准**：WHEN 删除完成 THEN 清单内每一项在磁盘上均不存在，且清单外的 `src` 文件数量不减少。

### 3.2 组件删除必须以编译器解析为准，不以正则 import 图为准

正则 import 图曾把 `KpEmpty` / `KpMineIcon` / `KpMineMenuItem` 报成"有 importers 但无活 importer"，存在漏读多行 import 块的风险。因此组件一律以 uni-app 编译产物的 `usingComponents` 字段做权威判定。

- WHEN 判定某组件可删 THEN 必须确认它未出现在任何 KEEP 页的编译产物 `dist/dev/mp-weixin/<page>.json` 的 `usingComponents` 中。
- WHEN 编译产物旧于 `src` THEN 该判定无效，必须先重新打包再判定。
- WHEN 正则结论与编译器结论冲突 THEN 取两者交集的保守侧（即"任一方说活就留"）。

**已核实结果**：产物新于全部源文件（build `2026-08-09 16:00:27` vs 最新 src `2026-08-07 20:37:26`，0 个源文件晚于产物），判定有效。组件总数 `37`，编译器判定 LIVE `7` 个（`KpButton` / `KpCapsuleSpacer` / `KpConfirmDialog` / `KpFloatingBackButton` / `KpFormItem` / `KpIdentityStatusCard` / `KpInput`），进入删除清单 `29` 个。冲突检查 `CONFLICT = []`，源码层复查 `COMPONENTS_MENTIONED_BY_KEEP_PAGE = 0`。

**验收标准**：WHEN 删除完成 THEN 上述 7 个 LIVE 组件全部存在；WHEN 重新打包 THEN 无 "component not found" 类报错。

### 3.3 环境声明文件强制保留

`env.d.ts`、`shime-uni.d.ts` 由 tsconfig 加载而非被 import，在任何 import 图里必然呈现为假死。

- WHEN 生成删除清单 THEN 这两个文件必须被强制移出删除集合。

**验收标准**：WHEN 删除完成 THEN 两文件均存在，且 `vue-tsc --noEmit` 不报缺失全局类型。

### 3.4 样式文件只列不删

- WHEN 闭包判定 `styles/*.scss` 与 `uni.scss` 为死 THEN 只登记不删除，因为它们经 `vite` / `uni.scss` 全局注入而非 import 链引用。

**验收标准**：WHEN 删除完成 THEN 7 个样式文件（`styles/_inject.scss`、`_mixins.scss`、`_page-layout.scss`、`_reset.scss`、`_tokens.scss`、`index.scss`、`uni.scss`）全部保留。

### 3.5 `pages.json` 登记收口

- WHEN 移除页面登记 THEN 主包 `pages` 由 `17` 收至 `6`；`pkg-card` 由 `10` 收至 `1`（仅留 `verify/index`）；`pkg-tools` 由 `3` 收至 `2`；`pkg-profile` 由 `4` 收至 `2`；`pkg-actor-card` `9` 页与 4 个 tabBar 项一律不动。
- WHEN 收口完成 THEN `pages.json` 登记总数为 `20`，与可达集合完全一致。

**验收标准**：WHEN 重新打包 THEN 编译产物 `app.json` 的页面列表长度为 `20`，且不含任何已删页路径。

### 3.6 `UserRole.Crew` 运行态切除口径

- WHEN 切除剧组运行态 THEN 覆盖 `api/auth.ts:98`、`pages/login/index.vue:120` 与 `:255`、`stores/user.ts:78` 与 `:356`、`utils/navigation.ts:26` 与 `:56`。
- WHEN 处理 `UserRole` 枚举 THEN **保留 `Crew` 成员本身**，因为后端仍返回该字段，删成员会引发跨文件类型连锁改动，超出本次范围。
- WHEN 注册入口收敛 THEN 注册角色固定为 `UserRole.Actor`，不再提供剧组选项。

**验收标准**：WHEN 切除完成 THEN `src` 内除 `types/user.ts` 的枚举定义外，不再出现 `UserRole.Crew` 的运行态分支；`vue-tsc --noEmit` 通过。

### 3.7 删除门禁继承 `00-110`

`00-110` 既有门禁："前端无引用 ≠ 可安全删除"。

- WHEN 删除任一 api 模块 THEN 必须确认它不是外部可调用契约的唯一前端见证；本次 10 个 api 模块（`actor-work` / `ai-profile-card` / `ai` / `apply` / `crew` / `history` / `personalization` / `project` / `role` / `share-card-favorite`）仅删前端调用层，后端端点保持存活。
- WHEN 存在无法从代码侧证伪的外部调用方 THEN 必须显式标注为未核实项而非判定安全。**已标注**：`/card/public/{shareCardId}` 的外部调用方无法从代码侧核实。

**验收标准**：WHEN 本 Spec 收口 THEN 后端四组端点确认未改动，并记录需单独授权。

## 4. 非功能需求

- WHEN 删除完成 THEN 微信单包仍需 ≤ `2 MB`，并记录包体前后差值。
- WHEN 改动 `src` THEN 必须执行 `cd kaipai-frontend && npm run build:mp-weixin` 重新打包，并 grep 核对产物，禁止只改源码即宣称完成。
- WHEN 打包完成 THEN `dist/dev` 由 postbuild 的 `robocopy /MIR` 自动镜像，落在 `dist/dev` 的手工改动（含本轮 23 条调试编译条件）会被清除，属预期。

## 5. 回滚点（前置条件，已满足）

用户要求"删除之前需要提交 git，方便找回"。已落地：

| 仓库 | 分支 | 提交 | 内容 |
|------|------|------|------|
| `kaipai-frontend`（独立仓库） | `V3.0` | `2e2d048` | 5 个已改文件，提交后 tree clean |
| 根仓库 `kaipai-team` | `V3.0` | `3c001b4` | `00-207/`、`00-208/`、`README.md`、`spec-code-mapping.md` |

刻意未提交：9 个非本人改动的既有 spec 文件（`00-190` ×5、`00-192` ×2、`03-05` ×2），保持未提交状态。

**回滚方式**：`cd kaipai-frontend && git reset --hard 2e2d048`（该命令属破坏性操作，需用户明确指令后才执行）。

## 6. 范围外

- 后端 `/api/crew`、`/api/project`、`/api/role`、`/api/apply` 及数据表退场——需单独授权。
- `UserRole` 枚举成员删除。
- `00-201` / `00-205` 门禁（19 项）的正式降级为历史件。
- `CURRENT_CONTEXT.md` 由 V7.7 刷新至 00-207/00-208/00-209 基线。
- `audit:mp-package` 既有阻塞项：`dist/build/mp-weixin/api/actor-asset.js` 含 `http://127.0.0.1:8010`（`00-204`/`00-205` 已记录）。该脚本 fail-fast，首个命中之后的其它 URL 可能尚未暴露。本 Spec 不修该项。
- `pkg-card/ai-profile-card-detail` 的拆分重构：该页已进入删除集合，重构目标随之消失。
