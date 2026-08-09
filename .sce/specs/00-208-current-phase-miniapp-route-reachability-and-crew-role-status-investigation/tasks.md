# 00-208 任务拆解 — 路由可达性与剧组身份状态调查

> 本 Spec 为**只读调查**。未经用户书面授权，不含删除、`pages.json` 改动、剧组代码改动或任何 git 写操作。

---

## T1. 建立 Spec 与方法论约束

- [x] 写入调查范围、身份边界、四类边模型与"未决边不判不可达"原则。
- [x] 显式记录上一轮 7 处错误及其根因，作为方法论约束来源。
- [x] 确立三条硬约束：写文件后 Read 复核、apparent size 计量、排除 `.orig`/`.bak`/`.rej`。

**Validates: Requirements 4, 6**

---

## T2. 登记基线核实

- [x] 从 `pages.json` 解析全量登记页：**43 页**（主包 16 + `pkg-actor-card` 9 + `pkg-card` 10 + `pkg-tools` 3 + `pkg-profile` 4，另含 `pages/login/index`）。
- [x] 解析 tabBar 入口：**4 个** —— `pages/home/index`、`pages/card-list/index`、`pages/assets/index`、`pages/mine/index`。
- [x] 核实登记页源文件缺失数：**`MISSING_SOURCE_FILE=0`**。
- [x] 核实工作树状态：`kaipai-frontend` 仅 5 个已修改文件，**零删除**；`src/pkg-card/card-list/index.vue` 存在（40,061 B）。

**Validates: Requirements 3.1**

### 验证记录

- `pages.json` 登记 `43`，tabBar `4`，缺失源文件 `0`。
- `pkg-card/card-list/index` **在 `pages.json` 中已登记**，推翻上一轮"被跟踪但未登记"的说法。
- `pkg-card/share-card-detail/index.vue` 在磁盘上不存在，且 git 无删除记录 —— 该路径在本仓从未被跟踪。

---

## T3. 第一版可达性推导（页面级边，已知不完整）

- [x] 以 4 个 tabBar 入口做 BFS，仅解析字面页面路径边。
- [x] 结果：可达 `20`，不可达 `23`。
- [x] 报告写入磁盘并用 Read 复核，未走管道目测。

**Validates: Requirements 3.1**

### 验证记录

不可达 `23` 页，覆盖范围远超 `pkg-card`：

| 区域 | 不可达页 |
|---|---|
| 剧组侧 | `project/create`、`project/role-create`、`role-detail`、`apply-confirm`、`apply-detail`、`apply-manage`、`my-applies`、`crew-profile/edit`、`contacts`、`history` |
| `pkg-card` | `actor-card`、`card-list`、`ai-profile-card`、`ai-profile-card-detail`、`portfolio`、`style-detail`、`favorites`、`invite`、`capability` |
| 其他 | `pkg-tools/settings`、`pkg-profile/works`、`pkg-profile/work-edit`、`pages/actor-profile/detail` |

发现互相引用成环、无外部入口的结构：
- `apply-confirm ↔ my-applies ↔ apply-detail ↔ role-detail`
- `pkg-card/card-list ↔ portfolio ↔ style-detail ↔ actor-card`

**本结果已知不完整**，反证如下：
- `pages/assets/index` 是 tabBar 入口却显示 `in=0` —— 直接证明入边被漏算。
- 4 个不可达页带有来自 `utils/share-artifact.ts` / `utils/share-card-mvp.ts` 的入边，属页面级图无法解析的活代码路径。

因此 T3 结论**不得作为退场依据**，必须由 T4 补齐边模型。

---

## T4. 补齐四类边并重算可达性

- [x] 已定位四类边的全部锚点（见 design §4）。
- [x] 实现能同时解析四类边的推导器，重算可达 / 不可达集合。
- [x] 输出未决边清单及其潜在目标，逐条人工判读。
- [x] 与 T3 结果做差集，明确哪些页因边模型补齐而由"不可达"翻转为"可达"。
- [x] 核实"未决边支点"：未决边是否可能让任一孤儿页翻转为可达。

**Validates: Requirements 3.2**

### 重算结果

```
REGISTERED_TOTAL=43
TABBAR_TOTAL=4
HELPERS_WITH_PAGE_TARGETS=29
REACHABLE_FROM_TABBAR=20
UNREACHABLE_FROM_TABBAR=23
REACHABLE_INCL_LOGIN_SEED=20
UNRESOLVED_DYNAMIC_NAV=9
```

**关键结论：补齐路径工厂边、组件 props 边并额外播种 `pages/login/index` 后，可达集合与 T3 完全一致 —— 仍是可达 20 / 不可达 23，翻转数为 0。**

补齐的边只提升了孤儿页的入度，未新增任何可达页。最清楚的例子是 `pages/actor-profile/detail`：入度由 `0` 升到 `6`（来自 `apply-manage`、`contacts`、`history`、`pkg-card/actor-card`、`ai-profile-card-detail`、`portfolio`），但这 6 个来源本身全部不可达，因此该页仍不可达。

### 未决边支点核实（决定性）

9 处未决动态跳转分布在 6 个源页：`pages/contacts/index`、`pages/history/index`、`pkg-card/card-list/index`、`pkg-card/portfolio/index`、`pkg-card/style-detail/index`、`pkg-tools/settings/index`。

**这 6 个源页与 20 页可达集合的交集为空。** 不可达页的出边不影响任何页的可达性，因此这 9 处未决边在数学上不可能让孤儿页翻转。

反向核实：逐一扫描 20 个可达页的全部动态跳转（共 `23` 处），目标全部落在已发现的可达集合内。唯一的裸变量跳转是 `pages/mine/index:141` `uni.navigateTo({ url })`，其 5 个调用点（`:150`、`:157`、`:164`、`:173`、`:190`）全为字面量，目标为 `/pages/actor-profile/edit`（含 `?tab=` 变体）与 `/pkg-card/verify/index`，均已在可达集内。

**因此可达性图已闭合。** 20/23 的划分不再受未决边限制 —— 这是本 Spec 相对上一轮审计的实质进展。

### 已知口径缺陷

helper 抽取正则过宽，helper 表混入非路径工厂项：`hideLoading`、`showLoading`、`entries`、`params`、`normalized`、`artifact`、`INVITE_CODE_CHARSET`。

该缺陷**只会高估边数、不会低估**，因此不影响"23 页不可达"这一方向的结论；但 helper 表的逐条明细不可直接引用。待 T7 门禁脚本收窄正则后再固化。

### 已定位锚点

**路径工厂**（4.2）：
- `utils/navigation.ts:4` `getHomePath(_role?)` → 恒 `/pages/home/index`
- `utils/navigation.ts:12` `goLogin()` → `/pages/login/index`
- `utils/share-card-mvp.ts` `buildShareCardDetailPath(...)`
- `utils/share-artifact.ts` `buildCreatorPreviewPath(...)`
- `utils/invite.ts:11` → `/pages/login/index?inviteCode=`
- `utils/request.ts:94` 401 重定向 → `/pages/login/index`

**组件 props**（4.3）：
- `components/KpNavBar.vue:74` `uni.reLaunch({ url: props.returnUrl })`

**全动态**（4.4）：
- `pkg-tools/settings/index.vue:56` `uni.navigateTo({ url: item.path })`
- `pages/apply-confirm/index.vue:229` `returnUrl.value || '/pages/home/index'`

**模板字面量边**：已采集 `28` 条 `navigateTo` 模板字面量跳转，覆盖 `pkg-actor-card` 全部 7 个 step 链、`pkg-profile`、`pkg-tools` 与 `pkg-card` 内部跳转。

---

## T5. 剧组身份三链核实

- [x] 注册链：`login/index.vue:22` 保留 `registerRole`（`UserRole.Actor | UserRole.Crew`）；`navigateAfterLogin` 接受 `UserRole.Crew` 并调 `goHome(user.role)`。
- [x] 落地链：`getHomePath` 忽略 `_role` 参数，恒返回 `/pages/home/index`；`home-v2` 探针结果 **`NO_ROLE_REF_IN_HOME`**，首页完全无 role 引用。
- [x] 页面链：`apply-manage`、`crew-profile/edit`、`project/create`、`project/role-create` 均消费 `ensureUserSessionReady(UserRole.Crew)`；`stores/user.ts:78` 保留 `isCrew`。
- [x] 形成"可注册、页面完整、入口缺失"的断链结论，并给出解释 A / B 两种相容假设。
- [ ] **待用户裁决**：剧组是已下线（解释 A）还是休眠（解释 B）。

**Validates: Requirements 3.3**

### 验证记录

`UserRole.Crew` 在源码中共 `21` 处命中，分布于 `utils/navigation.ts`、`stores/user.ts`、`constants/options.ts`、`api/auth.ts`、`login/index.vue` 及 4 个剧组页。

三链事实相互矛盾，源码无法自证：
- 若剧组已下线，则注册入口与 `api/auth.ts` 的剧组分支属漏删残留。
- 若剧组只是休眠，则 `home-v2` 缺 role 分支属 `00-206` 的回归缺陷。

**两种解释都与全部已核实事实相容，因此本项必须由用户裁决，不能由我推定。**

---

## T6. 体积基线与 minify 成本

- [x] `dist/build/mp-weixin/pkg-card` = `271,239` 字节 / `26` 文件（三法交叉验证）。
- [x] `pkg-card` 单点主因：`ai-profile-card-detail` 约 `87 KB`，占 `33%`；源码 `2510` 行，其中 style 段 `1368` 行。
- [x] minify 成本：`pkg-card` JS `176,270 → 120,833` 字节，省 `54 KB`（降幅 `31%`）。
- [x] 纠正上一轮 `1.2M` 错误 —— 根因是 `du` 默认块大小口径。
- [x] T4 已闭合：不可达集合稳定为 `23` 页，可退场体积上界因此可算，但**不等于可删**。
- [ ] 待剧组裁决后才能把不可达集合折算为真实可退场体积 —— 23 页中约 10 页属剧组主链，裁决前口径未定。

**Validates: Requirements 3.4**

---

## T7. 门禁脚本

- [ ] 编写 `scripts/verify-route-reachability` 固化基线：登记总数 `43`、tabBar 入口 `4`、四类边可达 `20` / 不可达 `23`、未决边清单 `9`、剧组三链锚点。
- [ ] 脚本目的为**锁定基线防漂移**，不作可删判定。
- [ ] 不纳入 `.orig` 残留项 —— T8 已证实该类文件不存在。

**Validates: Requirements 3.5, 4**

---

## T8. 残留文件清点

- [x] 清点 `src` 下 `.orig` / `.bak` / `.rej` 残留：**实测为零**。
- [x] 推翻上一轮"`src/pages/home/index.vue.orig` 与 `src/pages/mine/index.vue.orig` 存在"的说法 —— 该说法为**错误陈述**，两文件均不存在。
- [x] 该项无待办事项，已闭环。

**Validates: Requirements 3.6**

### 验证记录

双法交叉验证，结论一致为空：

| 方法 | 结果 |
|---|---|
| `find src -name '*.orig' -o -name '*.bak' -o -name '*.rej'` | 零命中 |
| Glob `kaipai-frontend/src/**/*.{orig,bak,rej}` | `No files found` |

补充事实：`.orig` **未被 `.gitignore` 忽略**（`NOT_IGNORED`）。因此若此类文件曾存在，必然会出现在 `git status` 中；而 `git status --porcelain` 全量输出只有 5 个已修改文件、零新增零删除。三项证据互证：**这两个 `.orig` 从未存在过**，是我上一轮的凭空陈述，而非已消失的历史残留。

**方法论后果**：此前把 `.orig` 列为"上一轮可达性误判的干扰源"的归因同样无效 —— 真实根因只有一个，即读管道截断输出而未回读文件。

---

## T9. 结论交付

- [x] 汇总四类边补齐后的可达性事实、未决边清单、剧组三链结论。
- [x] 明确区分"已核实"与"未核实"两类结论。
- [x] 已登记 `.sce/specs/README.md`（列表 + 索引表）与 `spec-code-mapping.md`；`npm run audit:steering` = `steering audit passed`。
- [ ] 提交用户裁决剧组去留；在裁决前**不产出任何退场范围**。

**Validates: Requirements 3.3, 5**

### 已核实（可作后续决策依据）

| 事实 | 值 | 证据强度 |
|---|---|---|
| `pages.json` 登记页 | `43` | 硬 |
| tabBar 入口 | `4` | 硬 |
| 四类边下可达 | `20` | 硬（图已闭合） |
| 四类边下不可达 | `23` | 硬（图已闭合） |
| 可达页的动态跳转 | 全部可解析，目标均已在可达集内 | 硬 |
| 9 处未决动态边的宿主页 | 6 页，**全部本身不可达** | 硬 |
| `src` 残留 `.orig/.bak/.rej` | `0` | 硬（三证） |
| `pkg-card` 产物 | `271,239` B / `26` 文件 | 硬（三法） |
| 治理审计 | `steering audit passed` | 硬 |

### 未核实（不得作决策依据）

| 缺口 | 原因 |
|---|---|
| 剧组（`role === 2`）是下线还是休眠 | 源码两解相容，需用户裁决 |
| 23 页是否真可退场 | 受 `00-110` 门禁约束：无前端引用 ≠ 可删 |
| `/card/public/{shareCardId}` 站外调用 | 需网关日志，代码不可证 |
| `audit:mp-package` 全量结论 | 脚本 fail-fast 停在 `actor-asset.js` 本地 URL，其后未扫 |

---

## 当前状态

| 任务 | 状态 |
|---|---|
| T1 建 Spec 与方法论 | 已核销 |
| T2 登记基线 | 已核销 |
| T3 第一版可达性（已知不完整） | 已核销，不得作退场依据 |
| T4 补齐四类边 | 已核销，图已闭合，20/23 不变 |
| T5 剧组三链 | 事实已核实，**待用户裁决** |
| T6 体积基线 | 已核销，可退场体积待剧组裁决 |
| T7 门禁脚本 | 待办（待剧组裁决后固化，避免锁错基线） |
| T8 残留清点 | 已核销，零命中，并纠正上一轮凭空陈述 |
| T9 结论交付 | 已核销事实交付与登记，**剧组裁决待用户** |

**代码改动：零。**本轮未删除任何文件、未改 `pages.json`、未碰剧组代码、未执行 git 写操作。`kaipai-frontend` 工作树仍为 5 个已修改文件（`vite.config.ts`、`home/index.vue`、`card-list/index.vue`、`mine/index.vue`、`scripts/start-miniapp.py`），全部属 `00-207` 范围。
