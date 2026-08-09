# 00-208 当前阶段小程序路由可达性与剧组身份状态重新调查

> 状态：调查中。本 Spec 只做只读调查与事实建档，**不包含任何删除、`pages.json` 改动、git stage / commit / push 或分支操作**。
>
> 立项原因：上一轮口头审计的数字与结论已被证伪（详见 §6），必须以可复现脚本重建事实基线后才允许进入任何退场切片。

## 1. 概述

`00-206` 把小程序主链重写为 v2 演员卡创建向导（`home-v2` + 名片夹 + 个人），底部导航收为 4 个 Tab。改版后 `pages.json` 中出现大量无法从真实入口进入的登记页，其中包含整条剧组（`role === 2`）主链。

本 Spec 要回答两个彼此耦合的问题：

1. **可达性事实**：从真实入口出发，`pages.json` 登记的页面里哪些真正可达、哪些不可达，且推导必须能覆盖动态跳转、路径工厂函数与组件 props 跳转这三类非字面边。
2. **剧组身份状态**：剧组是"已下线的历史能力"还是"仍可注册但入口缺失的休眠能力"。这个答案直接决定剧组侧页面属于死代码还是待修复功能。

本 Spec 只产出经核实的事实与分级退场建议。**是否退场、退场范围与执行顺序，必须由用户在看到本 Spec 结论后书面确认。**

## 2. 用户故事

作为项目接手方，我需要一份可复现、可复核的可达性事实，而不是一次性的口头结论，这样后续任何退场决策都能追溯到具体脚本与输出。

作为产品决策方，我需要明确剧组身份当前到底处于什么状态，因为"删掉 10 个剧组页"和"补回剧组首页入口"是两个完全相反的动作。

## 3. 功能需求

### 3.1 可达性推导的事实口径

- WHEN 推导可达性 THEN 入口只能取自 `pages.json` 的 `tabBar.list`，当前为 4 项：`pages/home/index`、`pages/card-list/index`、`pages/assets/index`、`pages/mine/index`。
- WHEN 收集节点 THEN 必须取 `pages.json` 的 `pages` 数组与全部 `subPackages[].root + pages[]`，当前登记总数为 `43`。
- WHEN 搜索引用 THEN 必须显式排除 `.orig`、`.bak`、`.rej` 及任何非构建参与文件；`src/pages/home/index.vue.orig` 与 `src/pages/mine/index.vue.orig` 已被证实会造成假入边。
- WHEN 报告任何体积数字 THEN 必须使用真实字节（`du --apparent-size` 或 `stat`），禁止使用 `du` 默认块大小口径。

**验收标准**：WHEN 门禁脚本执行完毕 THEN 输出登记总数、入口数、可达数、不可达数，且每个不可达页附带其入边来源分类。

### 3.2 必须覆盖的四类跳转边

上一轮只匹配字面页面路径，已确认漏判以下三类。本轮推导必须全部覆盖：

- **字面路径边**：`uni.navigateTo({ url: '/pages/xxx/index' })` 与模板字符串形式 `` `/pkg-actor-card/create/index?cardId=${id}` ``。
- **路径工厂边**：由 utils 返回路径再跳转，已确认存在 `buildShareCardDetailPath(...)`、`buildCreatorPreviewPath(...)`、`getHomePath(...)`、`utils/invite.ts` 的登录路径与 `utils/request.ts` 的 401 重定向。
- **组件 props 边**：`components/KpNavBar.vue` 的 `uni.reLaunch({ url: props.returnUrl })`，目标由调用方传入。
- **全动态边**：`pkg-tools/settings/index.vue` 的 `uni.navigateTo({ url: item.path })`，目标来自数据集合。

**验收标准**：WHEN 某页仅通过上述后三类边可达 THEN 不得判为不可达；WHEN 某类边无法静态解析 THEN 必须显式列为"未决边"，不得默认判为不可达。

### 3.3 剧组身份状态核实

已核实的事实：

- `src/utils/navigation.ts` 的 `getHomePath(_role?: UserRole)` **无条件返回 `/pages/home/index`**，`_role` 带下划线前缀且函数体未使用。
- `src/pages/home/index.vue`（`00-206` 的 `home-v2`）**完全没有 role 引用**，探针结果为 `NO_ROLE_REF_IN_HOME`。
- `src/pages/login/index.vue` 仍持有 `registerRole = ref<UserRole.Actor | UserRole.Crew>(UserRole.Actor)`。
- `navigateAfterLogin(user)` 仍显式接受剧组：`if (user.role === UserRole.Actor || user.role === UserRole.Crew) { goHome(user.role); }`。
- 剧组侧页面自身仍在消费剧组身份门禁，`ensureUserSessionReady(UserRole.Crew)` 出现在 `pages/apply-manage/index.vue`、`pages/crew-profile/edit.vue`、`pages/project/create.vue`、`pages/project/role-create.vue`。
- `stores/user.ts` 仍保留 `isCrew` computed。

由此推出的**待用户裁决问题**：剧组账号登录后会被 `goHome` 送到零剧组入口的 `home-v2`，形成可注册但无法使用的状态。

**验收标准**：WHEN 本 Spec 结论提交 THEN 必须明确列出上述事实，并把"剧组是下线还是休眠"标注为需用户书面确认项，不得由实现方自行假定。

### 3.4 不可达页分组与风险分级

- WHEN 输出不可达清单 THEN 必须按功能域分组，至少区分：剧组侧主链、`pkg-card` 旧演员卡链、`pkg-profile` 作品链、`pkg-tools` 独立页。
- WHEN 某组不可达页之间互相引用成环且无外部入边 THEN 必须显式标注为自闭环。
- WHEN 某页带有来自非页面 utils 的入边 THEN 必须单列，因为这类入边代表可能的活代码路径。

**验收标准**：WHEN 分组完成 THEN 每组标注 `建议退场 / 需产品裁决 / 禁止退场` 三档之一，并写明依据。

### 3.5 删除门禁继承

- 本 Spec 继承 `00-110` 的删除前口径：前端搜不到引用 **不等于** 可删。
- WHEN 任何退场建议涉及后端端点、数据库列或公开访问路径 THEN 必须独立评估，不得与前端页面退场绑定在同一切片。
- `GET /card/public/{shareCardId}` 已知为公开端点，小程序侧无可达消费者，但**是否存在小程序外调用方（H5 分享页 / 外部 webview / 二维码落地页）无法从源码判定**，必须由用户查网关日志或直接确认。

## 4. 非功能需求

- 全程只读。本 Spec 不删文件、不改 `pages.json`、不碰后端、不执行 git 写操作。
- 所有结论必须由写入磁盘的脚本输出支撑，并通过 Read 复核；禁止依赖管道 stdout 直接下结论。
- 每个数字在汇报前至少两种独立口径交叉验证。
- 明确区分"已核实"与"未核实"，未核实项必须显式标注而非省略。

## 5. 约束条件

- 不得在本 Spec 内执行 git stage、commit、push 或创建 / 切换分支。
- 不得修改 `pages.json` 的登记集合。
- 不得删除任何页面、组件、API 函数或后端代码。
- 不得把剧组侧页面按"死代码"处理，直到用户确认剧组已下线。
- 当前四个仓库均在 `V3.0` 分支，与 `CLAUDE.md` 的 `main` 约定不一致，本 Spec 不做分支变更。

## 6. 本 Spec 立项所纠正的错误

上一轮口头审计已被直接核实证伪，记录如下以防重复：

| 上一轮口头结论 | 核实后事实 |
|---|---|
| `pages.json` 登记 22 页 | `43` 页 |
| tabBar 3 个 Tab | `4` 个 |
| 8 页不可达 | 未定，需按 §3.2 四类边重推；仅按字面边推导为 `23` |
| 已删除 2 个残留页面文件 | 从未发生，`git status` 零删除 |
| `pkg-card/card-list/index.vue` 未登记 | 已登记于 `pages.json`，文件仍在（`40,061` 字节） |
| 已建 `00-208` Spec | 本文件才是首次真实建档 |
| `pkg-card` 体积 `1.2M` | `265 KB`（`du` 默认块大小口径虚高约 4 倍） |

根因：多轮 shell 管道输出被截断与串行，且未复核即汇报。本 Spec 的方法论约束（§4）即为针对此根因。

## 7. 验收清单

- [ ] 已按 §3.1 口径重建可达性基线，输出写入磁盘并经 Read 复核。
- [ ] 已按 §3.2 覆盖四类跳转边，未决边显式列出。
- [ ] 已按 §3.3 完整列出剧组身份事实，并标注需用户裁决。
- [ ] 已按 §3.4 完成不可达页分组与三档风险分级。
- [ ] 已明确 `/card/public` 外部调用方仍未核实。
- [ ] 全程未删代码、未改 `pages.json`、未执行 git 写操作。
- [ ] 已把结论回填至 `.sce/specs/README.md`、`spec-code-mapping.md` 与 `CURRENT_CONTEXT.md`。
