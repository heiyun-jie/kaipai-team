# 00-80 当前阶段后台用户管理表格密度对齐（Current Phase Admin User Management Table Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-79 current-phase-admin-user-management-first-screen-density-alignment
> 记录目的：在 `00-79` 已完成 `users/index` 首屏收口后，把剩余差异继续收窄到表格区本身，只处理行高、单元格密度与固定操作列观感。

## 1. 背景

截至 `2026-04-22`：

- `00-79` 已完成 `users/index` 的首屏 KPI、segment/快筛与筛选区收口

但当前表格区仍存在一组更窄的差异：

1. 当前表格行高仍偏厚
2. 用户单元格头像、文本间距与层级仍偏松
3. 固定右侧操作列宽度和观感仍略重

同时已通过真实浏览器核实：

- 当前首行高度约为 `81px`
- 当前固定操作列单元格宽度约为 `120px`

这说明当前差异已经不是首屏布局，而是表格区密度问题。

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-80`
- 只处理 `users/index` 主表区域：
  - 表头
  - 表格行
  - 用户单元格
  - 固定操作列
  - 分页区密度
- 用真实浏览器重新验证 `users/index` 表格区

### 2.2 本轮不处理

- 不再改 KPI 区
- 不再改 segment / 快筛
- 不再改高级筛选区
- 不改详情抽屉
- 不改表格字段语义或排序逻辑
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue` 的主表区域。
- **R2** 本轮判断必须优先服从真实运行态；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-79\users-index-after.png`
- **R3** 本轮不改变真实字段、筛选条件和详情动作，只处理视觉密度与交互壳层。

### 3.2 表格密度合同

- **R4** 表头 padding、表格行 padding 与单元格间距应明显收紧，使业务用户表更接近 reference 的高密度后台列表表达。
- **R5** 用户单元格中的头像、昵称、辅助信息层级应更紧，但仍保持可读。
- **R6** `身份`、`资格 / 会员` 两列的 stacked 文本应补齐局部样式，避免默认文本堆叠松散。

### 3.3 固定操作列合同

- **R7** 固定右侧操作列宽度应收紧，避免当前视觉占用偏重。
- **R8** 在收紧固定列后，`查看详情` 仍必须保持可点击、可读，不得因为过度压缩导致可用性下降。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-80` 承接，不继续把表格区精修混入 `00-79`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的 `users/index` 浏览器证据与运行态量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-80` Spec，并明确它只处理用户管理表格区
- [ ] 已完成表格行高、单元格密度与固定操作列收口
- [ ] 已通过真实浏览器复核 `users/index`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
