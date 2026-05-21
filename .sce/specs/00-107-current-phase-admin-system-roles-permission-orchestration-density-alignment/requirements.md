# 00-107 当前阶段后台角色治理权限编排区密度对齐（Current Phase Admin System Roles Permission Orchestration Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-106 current-phase-admin-system-roles-status-confirm-dialog-alignment
> 记录目的：在 `00-106` 完成 `system/roles` 状态确认弹窗收口后，继续把新建 / 编辑角色弹窗中的权限编排区内部密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-105` 已把 `system/roles` 新建 / 编辑 / 复制弹窗收成有限高度 dialog + body 内滚动
- 当前剩余厚度已收窄到创建 / 编辑弹窗中的 `权限编排` form item

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-107\roles-permission-tree-before.png`

当前差异：

1. 创建角色弹窗的 `权限编排` form item 仍约 `1000px`
2. `permission-editor` 仍约 `782 × 424`
3. toolbar 仍约 `782 × 86`
4. 两个 alert 均约 `782 × 84`
5. 四张权限包卡片均约 `386 × 172`
6. tree node content 仍约 `756 × 34`

### 当前量化

- dialog：`860 × 1064`
- body：`826 × 910`
- `权限编排` form item：`782 × 1000`
- permission editor：`782 × 424`
- toolbar：`782 × 86`
- alerts：`84 / 84`
- bundle cards：`172 / 172 / 172 / 172`
- tree：`782 × 328`
- first node：`756 × 34`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-107`
- 只处理 `system/roles` 新建 / 编辑弹窗里的权限编排区：
  - `RolesView.vue` 中权限包与 alert
  - `PermissionTreeEditor.vue` 内部 toolbar / unknown-list / tree / tree node
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改首屏与三张主卡
- 不改角色清单表格
- 不改详情抽屉
- 不改复制弹窗
- 不改状态确认弹窗
- 不改权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `system/roles` 创建 / 编辑弹窗中的权限编排区，不扩到其它页面和其它弹层。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 权限编排区密度合同

- **R4** `权限编排` form item 高度必须继续明显下降。
- **R5** toolbar、alert 和权限包卡片必须更轻。
- **R6** 权限树 node content 与 code 展示必须更紧，但仍可读、可点击。
- **R7** 权限包 tag 与 toolbar tags 可继续使用紧凑文案，但必须保留完整权限语义可追溯。

### 3.3 治理要求

- **R8** 本轮必须保持权限树勾选、过滤、展开/收起和未知权限保留逻辑不变。
- **R9** 本轮必须通过独立 `00-107` 承接，不继续混入 `00-105`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-107` Spec，并明确它只处理创建 / 编辑弹窗中的权限编排区密度
- [ ] 已完成权限包、toolbar、alert、permission tree 和 tree node 的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
