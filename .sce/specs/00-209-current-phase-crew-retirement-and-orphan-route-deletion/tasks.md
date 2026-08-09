# 00-209 任务：剧组能力退场与孤立路由删除

> 执行顺序即依赖顺序。每项完成后回填真实输出，不写预期值。

## 状态表

| 任务 | 内容 | 状态 |
|---|---|---|
| T1 | 建立双仓库回滚点 | 核销 |
| T2 | 计算 KEEP 反向闭包与删除清单 | 核销 |
| T3 | 产物新鲜度校验 | 核销 |
| T4 | 组件存活性编译产物交叉验证 | 核销 |
| T5 | 账目缺口核查（77+83 vs 161） | 核销 |
| T6 | 摘除 `pages.json` 23 条路由 | 核销 |
| T7 | 删除 23 个页面文件 | 核销 |
| T8 | 删除 60 个附带模块（含 FORCE KEEP 白名单校验） | 核销 |
| T9 | 切除 `UserRole.Crew` 运行态分支 | 核销 |
| T10 | `vue-tsc --noEmit` 类型门禁 | 核销 |
| T11 | `build:mp-weixin` + 双侧产物 grep 核对 + 体积记录 | 核销 |
| T12 | 注册 00-209 + `audit:steering` | 核销 |
| T13 | 悬空 import 全量扫描（T7/T8 后新增闸门） | 核销 |

## T1 回滚点（核销）

用户前置条件「删除之前需要提交 git，方便找回」。

- `kaipai-frontend` 独立仓库，分支 `V3.0`，commit **`2e2d048`**（5 个文件），提交后 tree clean。
- 根仓库分支 `V3.0`，commit **`3c001b4`**（`00-207/`、`00-208/`、`README.md`、`spec-code-mapping.md`）。
- 刻意排除 9 个非本人改动的既有修改文件（`00-190` ×5、`00-192` ×2、`03-05` ×2），保持未提交。

## T2 删除清单（核销）

```
registered_pages=43  delete_pages=23  keep_pages=20
roots=22  keep_closure=77  all_code=161
dead_code=83  dead_pages=23  dead_collateral=60
bytes: pages=471970  collateral=181869  TOTAL=653839
CONFLICT: components in delete list but compiler-LIVE (MUST BE []) = []
FORCE_KEEP honored: env.d.ts=kept, shime-uni.d.ts=kept
```

最大单页：`pkg-card/ai-profile-card-detail/index.vue` 72,870 B；最大附带模块：`pkg-card/ai-profile-card-detail/layout-presets.ts` 10,765 B、`utils/actor-card.ts` 11,244 B。

## T3 产物新鲜度（核销）

```
newest src   : 2026-08-07 20:37:26  src/pages/mine/index.vue
newest build : 2026-08-09 16:00:27  dist/build/mp-weixin/common/vendor.js
src files newer than newest build artifact = 0
BUILD_IS_NEWER_THAN_SRC = True
```

结论：产物未滞后，`usingComponents` 交叉验证成立。

## T4 组件交叉验证（核销）

```
SUMMARY components: total=37 compiler_live=7 compiler_dead=30
compiler_live = [KpButton, KpCapsuleSpacer, KpConfirmDialog,
                 KpFloatingBackButton, KpFormItem, KpIdentityStatusCard, KpInput]
components COMPILER-LIVE but appearing in regex closure text = 0
COMPONENTS_MENTIONED_BY_KEEP_PAGE (must be 0) = 0
KEEP pages with no compiled .json = 0
easycom: components total=37 nested=0 flat=37 -> 显式 import 必需
```

推翻的前序担忧：`KpMineIcon` / `KpMineMenuItem` / `KpEmpty` 确认未被 `pages/mine/index` 使用，该页只用 `KpCapsuleSpacer` + `KpConfirmDialog`。

## T5 账目缺口（核销）

```
force_keep = ['env.d.ts', 'shime-uni.d.ts']  (p=2)
keep + dead + force_keep = 161
UNACCOUNTED FILES = 0
IN KEEP BUT NOT IN all_code = 0
delete_page_files_resolved = 23   delete pages with no .vue = 0
```

缺口成因：`env.d.ts` / `shime-uni.d.ts` 被 FORCE KEEP 单列，未计入 `keep_closure` 的 77，属归类重叠而非漏算。161 已完全闭合。

## T6 摘除 `pages.json` 路由（核销）

```
main_pages 17 -> 6      (remove 11)
pkg-actor-card  9 -> 9  (remove 0)
pkg-card       10 -> 1  (remove 9)
pkg-tools       3 -> 2  (remove 1)
pkg-profile     4 -> 2  (remove 2)
registered_total 43 -> 20   tabBar_entries=4（未改动）
REGISTERED PAGES WITH NO .vue = 0
TABBAR TARGETS NOT REGISTERED = 0
```

## T7 + T8 删除页面与附带模块（核销）

```
PAGES_LISTED=23  COLLATERAL_LISTED=60  TOTAL=83
DUPLICATES = []      FORBIDDEN HITS = []      MISSING BEFORE DELETE = []
DELETED_FILES=83     FREED_BYTES=653839
STILL PRESENT AFTER DELETE = []
REMOVED_EMPTY_DIRS=24
components_remaining=8   REMAINING_CODE_FILES=78
FORCE_KEEP env.d.ts / shime-uni.d.ts / pages.json / App.vue / main.ts  全部 exists=True
```

存活组件 8 个 = 编译器 LIVE 7 个 + `KpStatusTag.vue`。`KpStatusTag` 属编译器判死但正则判活的那 1 个差额，按保守偏差保留，不删。`styles/*.scss` 与 `uni.scss` 共 7 个文件按 design.md 只列不删。

## T9 切除 `UserRole.Crew` 运行态（核销）

改动 6 处，`types/user.ts:6` 的枚举成员 `Crew = 2` 与 `types/crew.ts`、`types/role.ts` 按 design.md 保留（后端仍返回该字段）。

| 文件 | 位置 | 处理 |
|---|---|---|
| `utils/navigation.ts` | 26 | 守卫收窄为 `!== UserRole.Actor` |
| `utils/navigation.ts` | 56 | 同上（含 `userStore.logout()` 分支） |
| `api/auth.ts` | 98 | 形参类型收窄为 `UserRole.Actor` |
| `stores/user.ts` | 78 | 删除 `isCrew` computed |
| `stores/user.ts` | 356 | 删除 return 中的 `isCrew` |
| `pages/login/index.vue` | 120 | `registerRole` 类型收窄为 `UserRole.Actor` |
| `pages/login/index.vue` | 255 | `navigateAfterLogin` 去掉 Crew 分支 |

`registerRole` 变量本体保留：141 / 295 / 298 三处仍在消费，且 `registerByPhone` 仍需 role 实参。

悬空 import 全量扫描（存活 78 个代码文件、228 条 import 说明符）：

```
DANGLING IMPORTS = 0
crew_runtime_hits in surviving src = 0
```

## T10 类型门禁（核销）

```
cwd = /d/XM/kaipai-team/kaipai-frontend   (tsconfig.json 就位)
vue-tsc --noEmit  TSC_EXIT=0   输出行数=0
```

## T11 构建与双侧产物核对（核销）

```
BUILD_EXIT=0   DONE Build complete.
postbuild: synced mp-weixin build to dev + set urlCheck=false
```

| 项 | dist/build | dist/dev |
|---|---|---|
| app.json 登记总数 | 20 | 20 |
| tabBar 条目 | 4 | 4 |
| 已删页残留产物 | 0 | 0 |
| 已删页仍在 app.json | 0 | 0 |
| 守卫组件缺失 | 0 | 0 |
| 主包 apparent | 450,118 B（439.6 KB） | 451,072 B（440.5 KB） |
| 整包 apparent | 688,501 B（672.4 KB） | 689,455 B（673.3 KB） |

```
BUILD vs DEV page-set identical = True   (only in BUILD: []  only in DEV: [])
BUILD .js files containing 'isCrew' = 0
分包：pkg-actor-card 83,226 B / pkg-card 32,398 B / pkg-tools 40,151 B / pkg-profile 82,608 B
src apparent bytes now = 499875
```

主包 439.6 KB，距 2,048 KB 上限余量充足。`dist/dev` 比 `dist/build` 多 954 B，来自 postbuild 改写 `project.config.json`（`urlCheck=false`），非页面差异。

**副作用记录**：本轮 `robocopy /MIR` 已按预期清除我此前写入 `dist/dev/mp-weixin/project.config.json` 的 23 条自定义编译条件。那些条件指向的页面已删除，无需恢复。

## T12 登记与治理审计（核销）

```
README bullet 命中 = 1     README 索引表行 = 1     spec-code-mapping 行 = 3
spec files = requirements.md, design.md, tasks.md
npm run audit:steering -> steering audit passed   AUDIT_EXIT=0
```

## 未纳入本 Spec 的遗留项

- 后端 `/api/crew`、`/api/project`、`/api/role`、`/api/apply` 及其数据表**未改动**，需单独授权。
- `npm run audit:mp-package` 仍被既有 `api/actor-asset.js` 内 `http://127.0.0.1:8010` 阻塞（`00-204` / `00-205` 既有问题，fail-fast 脚本，首个之后的 URL 未探明）。
- `00-201` / `00-205` 门禁自 `00-206 T7` 换首页后长红（19 项），尚未在盘上正式降级为历史。
- `CURRENT_CONTEXT.md` 仍为 V7.7，停留在 00-199 / 00-200，需刷新到 00-207 / 00-208 / 00-209 基线。
- `/card/public/{shareCardId}` 的外部调用方无法从代码侧证实。
