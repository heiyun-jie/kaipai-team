# 00-75 当前阶段后台参考稿壳层密度对齐（Current Phase Admin Reference Shell Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-71 admin-console-reference-ui-implementation，00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `00-74` 已完成 reference 8 页信息架构回接后，把当前后台剩余的桌面壳层偏差收口成一条更窄的后续 Spec，避免继续把“主标题换行 / 顶控换行 / 壳层密度偏松”混在 `00-74` 的架构主线里。

## 1. 背景

截至 `2026-04-22`，`00-74` 已完成：

- 正式导航恢复为 reference 的 8 页结构
- 8 个正式页面都进入真实运行态
- `AdminLayout / AdminSidebar` 已完成最新壳层尺寸收紧并通过浏览器复核

但在最新桌面运行态下，又核实出一组更窄、但跨页面重复出现的壳层问题：

1. 主线页标题在桌面宽度下仍会发生换行
   例如：
   - `数据分析`
   - `用户管理`
   - `风格模板`
2. 顶部控制区在桌面宽度下会拆成两行
   例如：
   - 搜索框在第一行
   - 通知 / 导出 / 账号入口落到第二行
3. 当前问题已经不再是信息架构错误，也不是事实源缺失，而是：
   - 桌面壳层密度
   - 标题与顶控的单行对齐
   - reference 控制台首屏的空间分配

因此，继续把这些残余问题写在 `00-74` 里会稀释主线边界；更合理的方式是新增一个只处理壳层密度的后续 Spec。

## 2. 范围

### 2.1 本轮必须处理

- 固化当前桌面主线页的剩余壳层偏差为独立 `00-75`
- 让 `AdminTopbar.vue` 在桌面主线页下恢复更接近 reference 的：
  - 主标题单行表达
  - 顶控单行表达
  - 更紧的首屏密度
- 基于真实浏览器重新验证至少以下页面的当前顶控表现：
  - `/dashboard/index`
  - `/dashboard/analytics`
  - `/users/index`
  - `/content/templates`

### 2.2 本轮不处理

- 不再改后台正式信息架构；8 页结构继续以 `00-74` 为准
- 不新增页面、路由、接口或权限码
- 不重写单页业务模块，只处理共享壳层密度
- 不为了贴图去伪造搜索、导出或通知能力

## 3. 需求

### 3.1 证据与适用范围

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin` 登录后主线页的共享顶控与壳层密度，不覆盖登录页、不覆盖前台。
- **R2** 本轮判断必须优先服从真实桌面浏览器运行态，而不是历史截图；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-74\dashboard-index-shell-verify.png`
  - `D:\XM\kaipai-team\output\playwright\00-74\dashboard-analytics-current-shell.png`
  - `D:\XM\kaipai-team\output\playwright\00-74\users-index-current-shell.png`
  - `D:\XM\kaipai-team\output\playwright\00-74\content-templates-current-shell.png`
- **R3** 本 Spec 只针对桌面主线页首屏；移动端和窄屏继续允许走已有断点堆叠逻辑。

### 3.2 桌面顶控与主标题合同

- **R4** 在桌面宽度下，主线页标题不得因为右侧顶控密度问题而被动断成两行；至少以下标题需保持单行：
  - 仪表盘
  - 数据分析
  - 用户管理
  - 风格模板
- **R5** 在桌面宽度下，顶控右侧主控制区不得再因为 shrink-to-fit 或 flex wrap 逻辑被拆成两行；主线页需要尽量保持 reference 的单行控制条语义。
- **R6** 搜索框、窗口按钮、通知按钮、导出按钮、账号入口的现有功能边界必须保持不变；本轮只允许调整：
  - 宽度分配
  - gap
  - nowrap / shrink 策略
  - 主标题字号与行高
  - 按钮与搜索框尺寸密度

### 3.3 共享壳层密度边界

- **R7** `AdminTopbar.vue` 的桌面主线样式必须比当前更紧，但不能因为过度压缩导致：
  - 搜索占位文案被严重截断
  - 顶控按钮不可读
  - 主标题被压扁或溢出
- **R8** 当前 `AdminLayout.vue / AdminSidebar.vue` 已完成复核，本轮不得再无证据地继续改侧栏和主内容 shell；除非新浏览器证据证明仍存在结构问题。

### 3.4 治理要求

- **R9** 本轮必须以独立 `00-75` Spec 承接，不继续把残余视觉精修附着到 `00-74` 的架构主线里。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的浏览器证据写入 `execution.md`，明确说明当前问题是“桌面壳层密度与顶控单行对齐”，而不是再次发生 IA 偏航。

## 4. 验收标准

- [ ] 已新增独立 `00-75` Spec，并明确其是 `00-74` 之后的桌面壳层密度后续线
- [ ] 已确认当前问题是主标题与顶控换行，而不是新的信息架构缺口
- [ ] 已完成 `AdminTopbar.vue` 的桌面主线页单行对齐修复
- [ ] 已通过真实浏览器复核 `/dashboard/index`、`/dashboard/analytics`、`/users/index`、`/content/templates`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
