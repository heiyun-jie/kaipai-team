# 00-209 设计：剧组能力退场与孤立路由删除

> 上游基线：`00-208`（可达性事实）、`00-110`（删除门禁）。
> 本 Spec 只处理**前端**退场。后端 `/api/crew`、`/api/project`、`/api/role`、`/api/apply` 及其表结构**不在本次范围**，需单独授权。

## 1. 事实基线（全部来自可复现脚本输出，非估算）

| 项 | 值 | 来源 |
|---|---|---|
| `pages.json` 登记页总数 | 43 | `manifest.py` |
| 可达（KEEP）页 | 20 | `00-208` T4 四类边闭合 |
| 不可达（DELETE）页 | 23 | 同上 |
| KEEP 闭包代码文件 | 77 | `manifest.py` 从 22 个根做传递闭包 |
| `src` 代码文件总数 | 161 | 同上 |
| 死代码文件 | 83（23 页 + 60 附带模块） | 同上 |
| 删除字节数 | 653,839 B（页 471,970 + 附带 181,869） | `stat` 真实字节 |

回滚点（删除前已建立，用户前置条件）：

- `kaipai-frontend`（独立仓库）：`2e2d048`
- 根仓库：`3c001b4`

## 2. 关键设计决策

### 2.1 用「反向闭包」而非「正向孤儿扩散」

从根集（`App.vue`、`main.ts`、20 个 KEEP 页，共 22 个根）沿 import 边求传递闭包得到 KEEP 集，`src` 内闭包之外的一切即死代码。

理由：正向从孤儿页扩散删除集，容易漏掉「只被孤儿引用但看起来像公共模块」的文件；反向闭包对这类文件天然正确。`00-208` 阶段两次误判（`utils/upload.ts`、`KpBottomActionBar.vue` 先被判活后判死）正是正向法的失效案例。

### 2.2 组件存活性以**编译产物**为准，不以正则 import 图为准

`src/pages.json` 开启了 `easycom.autoscan`，理论上组件可以零 import 行被使用，会使 import 图失效。

实测排除该风险：

- `src/components/` 共 37 个文件，**全部扁平**（`components/KpX.vue`），嵌套式 `components/<name>/<name>.vue` 数量为 `0`；
- uni-app 默认 autoscan 模式要求嵌套式布局，扁平文件不匹配 → 必须显式 import。

在此之上仍做一道权威交叉验证：读取每个 KEEP 页编译产物 `dist/dev/mp-weixin/<page>.json` 的 `usingComponents`，这是 uni-app 编译器自己的解析结果，优先级高于我的正则。

结果：编译器判定 7 个组件 LIVE，30 个未被任何 KEEP 页使用；**删除清单与编译器 LIVE 集的交集为空**。

编译器 LIVE 集（禁止删除）：`KpButton`、`KpCapsuleSpacer`、`KpConfirmDialog`、`KpFloatingBackButton`、`KpFormItem`、`KpIdentityStatusCard`、`KpInput`。

正则 KEEP=8 与编译器 LIVE=7 存在 1 个差额，方向为「正则多留一个」，属保守偏差，不会造成误删，故取并集保守处理。

### 2.3 产物新鲜度前置校验

交叉验证依赖产物，产物滞后则结论失效。执行前实测：

- 最新 `src` 文件：`2026-08-07 20:37:26`（`pages/mine/index.vue`）
- 最新 build 产物：`2026-08-09 16:00:27`
- **晚于产物的 src 文件数 = 0**

故产物可信。此校验必须在任何组件删除前重跑一次。

### 2.4 强制保留项（import 图必然误判）

`env.d.ts`、`shime-uni.d.ts` 是 tsconfig 加载的 ambient 声明文件，从不被 import，在任何 import 图里都是假阳性死代码 → **FORCE KEEP**。

### 2.5 样式文件只列不删

7 个 `.scss`（`styles/*`、`uni.scss`）通过构建配置与 `uni.scss` 约定注入，不走 import 图 → 本次**只列清单，不删除**。

### 2.6 `UserRole.Crew` 枚举成员保留

删除剧组运行态分支，但**保留枚举成员本身**。后端仍会返回该字段，删除成员会引发跨 `types/*` 的连带类型改动，超出本次退场范围且无收益。

### 2.7 类型链保留

`utils/format.ts` 被可达页 `pages/mine/index.vue` 引用，它 import `types/apply`、`types/project`（**类型，不是 api**），因此 `types/apply.ts → types/role.ts → types/crew.ts / types/project.ts` 整条链必须保留。`types/crew.ts` 名字含 crew 但属 KEEP。

## 3. 改动面

### 3.1 `src/pages.json` 路由摘除

| 桶 | 前 | 后 | 摘除 |
|---|---|---|---|
| 主包 `pages` | 17 | 6 | 11 |
| `pkg-card` | 10 | 1 | 9 |
| `pkg-profile` | 4 | 2 | 2 |
| `pkg-tools` | 3 | 2 | 1 |
| `pkg-actor-card` | 9 | 9 | 0 |

`tabBar` 4 项全部落在 KEEP 集内，不动。

### 3.2 `UserRole.Crew` 运行态切除点

| 文件 | 位置 | 动作 |
|---|---|---|
| `src/api/auth.ts` | 98 | `registerUser` 入参联合类型收为 `UserRole.Actor` |
| `src/pages/login/index.vue` | 120、255 | `registerRole` 类型收窄；`navigateAfterLogin` 去掉 Crew 分支 |
| `src/stores/user.ts` | 78、356 | 删 `isCrew` computed 与 return 导出 |
| `src/utils/navigation.ts` | 26、56 | `ensureUserSession` / `ensureUserSessionReady` 的双身份判定收为 Actor |
| `src/pkg-card/ai-profile-card/index.vue` | 387 | 随该页删除自然消失 |

## 4. 验证策略

1. `npx vue-tsc --noEmit` —— 类型闭合，捕获遗漏引用；
2. `npm run build:mp-weixin` —— postbuild 自动 `robocopy /MIR` 同步 `dist/build` → `dist/dev`；
3. grep 核对 `dist/build` 与 `dist/dev` 双侧：23 个页面无残留、7 个 LIVE 组件仍在；
4. 记录主包与各分包体积变化，对齐 2 MB 约束；
5. `npm run audit:steering`。

已知阻塞：`npm run audit:mp-package` 因 `api/actor-asset.js` 内 `http://127.0.0.1:8010` 前置失败（`00-204`/`00-205` 已建档），非本次引入；该脚本 fail-fast，首个之后的 URL 可能未被发现。本次不修，只记录。

## 5. 风险与对策

| 风险 | 对策 |
|---|---|
| 正则漏读导致误删组件 | 编译产物 `usingComponents` 交叉验证，交集为空；产物新鲜度前置校验 |
| ambient 声明被误删 | FORCE KEEP 白名单 |
| 删除后类型不闭合 | `vue-tsc --noEmit` 作为硬门禁 |
| `dist/dev` 手写内容被覆盖 | 已知 `robocopy /MIR` 语义；23 条编译条件属一次性调试产物，允许被覆盖 |
| 外部仍在调用剧组接口 | 后端不动，前端退场不影响既有接口可用性 |
| 回滚需求 | 双仓库回滚点 `2e2d048` / `3c001b4` |
