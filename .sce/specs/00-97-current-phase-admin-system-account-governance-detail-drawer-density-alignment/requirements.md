# 00-97 当前阶段后台账号治理详情抽屉密度对齐（Current Phase Admin System Account Governance Detail Drawer Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-96 current-phase-admin-system-account-governance-table-density-alignment
> 记录目的：在 `00-96` 完成 `system/admin-users` 主表密度收口后，继续把详情抽屉的宽度、header、hero 与字段块密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-95` 已完成 `system/admin-users` 首屏结构收口
- `00-96` 已完成 `system/admin-users` 主表密度收口
- 当前页剩余最明显的视觉残差已收窄到详情抽屉
- 当前页没有 direct reference 子页；因此本轮目标不是伪造新的 reference 页面，而是把详情抽屉继续收口为更轻的治理详情面板

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-97\admin-users-drawer-before-open.png`

当前差异：

1. 抽屉宽度仍为 `620px`
2. 抽屉 header 高度约 `77px`
3. hero 高度约 `85px`
4. 每个 `detail-block` 仍约 `92px`
5. 整个详情网格高度约 `827px`

### 当前量化

- 抽屉宽度：`620px`
- header 高度：`77px`
- body 高度：`1021px`
- hero：`566 × 85`
- detail grid：`566 × 827`
- `detail-block`：`92px`
- 角色 `tag-list`：`532 × 34`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-97`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue` 的详情抽屉：
  - drawer width / header / body
  - hero
  - detail grid / detail block
  - 角色绑定区 tag list
- 用真实浏览器复核 `http://127.0.0.1:5100/system/admin-users`

### 2.2 本轮不处理

- 不改首屏 shell card
- 不改 FilterPanel
- 不改主表字段与主表交互
- 不改创建 / 编辑 / 绑定 / 重置密码 / 启停用弹窗
- 不改真实接口与账号角色模型

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `AdminUsersView.vue` 详情抽屉密度，不扩到首屏 shell、主表和其它弹窗。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台账号、角色绑定、密码处置与启停用，不扩展新的组织或权限模型。

### 3.2 抽屉密度合同

- **R4** 抽屉宽度必须明显收窄，不再维持当前 `620px` 的厚重观感。
- **R5** 抽屉 header / body / hero 必须明显收紧。
- **R6** `detail-block` 的高度、padding、字号与 gap 必须收口，不再维持当前约 `92px` 的字段卡高度。
- **R7** 角色绑定区 tag list 必须更轻，但仍保持角色可读与状态语义。

### 3.3 治理要求

- **R8** 本轮必须保持字段语义、详情数据与 `查看详情` 交互链不变。
- **R9** 本轮必须通过独立 `00-97` 承接，不继续混入 `00-96`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-97` Spec，并明确它只处理 `system/admin-users` 详情抽屉密度
- [ ] 已完成抽屉宽度、header/body、hero、detail block 与 role tag list 的局部收口
- [ ] 已通过真实浏览器复核 `system/admin-users`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
