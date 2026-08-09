# 00-208 技术设计 — 路由可达性与剧组身份状态调查方法

> 本设计只描述**如何取得可复现事实**，不描述任何删除动作。

## 1. 为什么不能沿用上一轮方法

上一轮用"grep 页面路径 + 目测输出"得出结论，产生了 7 处错误（见 requirements §6）。三个根因：

1. **管道输出不可信**：本环境 shell 输出多次被截断、循环少打、数字串行。
2. **边模型过窄**：只匹配字面页面路径，漏掉路径工厂、组件 props、全动态三类边。
3. **体积口径错误**：`du` 默认按磁盘块计，本项目"多页面 + 每页 4 小文件"结构下虚高约 4 倍。

本设计针对这三点分别设约束。

## 2. 事实获取管线

```
pages.json ──► 节点集合（43 页）
                    │
源码扫描 ──► 四类边 ──► 有向图
（排除 .orig/.bak/.rej）  │
                    ▼
tabBar 4 入口 ──► BFS ──► 可达集 / 不可达集
                    │
                    ▼
            写入磁盘报告 ──► Read 复核 ──► 汇报
```

**硬约束**：管线末端必须"写文件 → Read 读回"，禁止 `python ... | tail` 之后直接下结论。

## 3. 节点模型

节点 = `pages.json` 登记的页面路径（不含前导 `/`）。

- 主包：`pages[]` 直接取值。
- 分包：`subPackages[].root` + `/` + `subPackages[].pages[]`。
- 源文件解析：节点路径 + `.vue`，若缺失则尝试同名目录下 `index.vue`。
- 已核实当前 `MISSING_SOURCE_FILE=0`，即 43 个登记页在 `src` 下都有对应源文件。

## 4. 边模型 — 四类

### 4.1 字面路径边

正则匹配源码中出现的 `'/<node>'` 或 `` `/<node>?...` ``。对每个节点路径做全字边界匹配，避免 `pages/card-list/index` 误命中 `pkg-card/card-list/index`。

### 4.2 路径工厂边

已确认的工厂函数：

| 工厂 | 位置 | 产出目标 |
|---|---|---|
| `getHomePath(_role?)` | `utils/navigation.ts:4` | 恒为 `/pages/home/index` |
| `goLogin()` | `utils/navigation.ts:12` | `/pages/login/index` |
| `buildShareCardDetailPath(...)` | `utils/share-card-mvp.ts` | 分享详情页 |
| `buildCreatorPreviewPath(...)` | `utils/share-artifact.ts` | 创作者预览页 |
| `buildLoginPathWithInvite(...)` | `utils/invite.ts:11` | `/pages/login/index?inviteCode=` |
| 401 重定向 | `utils/request.ts:94` | `/pages/login/index` |

处理方式：先解析工厂函数体内的字面目标路径，再把"调用该工厂的文件"连边到"该工厂产出的目标节点"。

### 4.3 组件 props 边

`components/KpNavBar.vue:74` 执行 `uni.reLaunch({ url: props.returnUrl })`。目标由调用方模板传入，静态不可解析。

处理方式：列为**未决边**，同时记录所有向 `KpNavBar` 传 `returnUrl` 的调用点，人工判读其字面值。

### 4.4 全动态边

`pkg-tools/settings/index.vue:56` 执行 `uni.navigateTo({ url: item.path })`，`item` 来自本地数据集合。

处理方式：解析该集合内的字面 `path` 值成边；若集合来自接口则列为未决边。

## 5. 未决边处理原则

**未决边一律不判为不可达。** 任何无法静态解析的跳转，其潜在目标必须进入"待人工判读"清单，而不是默认落进不可达集。这是防止误删的核心约束。

## 6. 剧组身份判读模型

剧组状态由三条链共同决定，缺一不可判：

| 链 | 当前已核实事实 | 含义 |
|---|---|---|
| **注册链** | `login/index.vue` 保留 `registerRole`，`navigateAfterLogin` 接受 `UserRole.Crew` | 剧组账号仍可产生 |
| **落地链** | `getHomePath` 忽略 role，恒返回演员首页；`home-v2` 探针 `NO_ROLE_REF_IN_HOME` | 剧组登录后无处可去 |
| **页面链** | 4 个剧组页仍消费 `ensureUserSessionReady(UserRole.Crew)`，`stores/user.ts` 保留 `isCrew` | 剧组页面自身仍完整 |

三链组合结论：**剧组处于"可注册、页面完整、但入口缺失"的断链状态**。

这不是源码能裁决的问题，因为两种相反解释都与事实相容：

- **解释 A（已下线）**：`00-206` 有意收敛为纯演员产品，剧组注册入口是漏删的残留 → 应退场剧组页 + 注册入口。
- **解释 B（休眠）**：剧组是暂时隐藏的既有能力，`home-v2` 漏做 role 分支 → 应修复入口，禁止退场。

因此本 Spec 只呈现事实，把裁决交回用户。

## 7. 体积口径

- 统一使用真实字节：`du --apparent-size -b` 或 Python `os.stat().st_size` 累加。
- 每个数字至少两种独立口径交叉验证。
- 已交叉验证成立的基线：`dist/build/mp-weixin/pkg-card` = `271,239` 字节 / `26` 文件（`du --apparent-size`、`os.walk`、`find` 三法一致）。
- 已知 minify 成本：`pkg-card` JS `176,270 → 120,833` 字节，省 `54 KB`（降幅 `31%`）。

## 8. 门禁脚本设计

`scripts/verify-route-reachability.mjs`（或 `.py`）需固化：

1. `pages.json` 登记总数与 tabBar 入口集合 —— 变化即告警，强制复审。
2. 四类边的解析结果与可达 / 不可达集合。
3. 未决边清单 —— 数量变化即告警。
4. 剧组三链的关键锚点（`getHomePath` 忽略 role、`home-v2` 无 role 引用、`registerRole` 存在、4 个剧组页的身份门禁）。
5. `.orig` / `.bak` 残留文件清单。

脚本目的是**锁定基线防漂移**，不是判定可删。

## 9. 明确不做的事

- 不删任何页面、组件、API 函数、后端代码。
- 不改 `pages.json`。
- 不改剧组相关任何代码。
- 不执行 git 写操作。
- 不对 `/card/public` 外部调用方下结论 —— 该项只能由用户查网关日志确认。

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4_
