# 00-111 设计说明

## 1. 设计目标

`00-111` 只完成第一批低风险历史 wrapper 退场：

1. 删除 `DashboardView.vue`
2. 删除 `ReferralRiskView.vue`
3. 不触碰 `PlaceholderView.vue`

## 2. 已核实事实

### 2.1 两个目标文件都是薄包装

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardView.vue`
  - 当前仅渲染 `OverviewView`
- `D:\XM\kaipai-team\kaipai-admin\src\views\referral\ReferralRiskView.vue`
  - 当前仅渲染 `RiskView`

### 2.2 当前代码侧未发现引用

已核实：

- 在 `kaipai-admin/src` 内搜索：
  - `DashboardView`
  - `ReferralRiskView`
  - 未命中引用
- 在全仓内做精确路径搜索，排除 `.sce/`、`output/`、reference html 后：
  - `DashboardView.vue`
  - `ReferralRiskView.vue`
  - 未命中代码侧引用

因此这两个对象符合：

- 无运行路由依赖
- 无菜单依赖
- 无源码 import 依赖
- 文件本身只是历史 wrapper

## 3. 设计策略

### 3.1 删除策略

直接删除：

- `DashboardView.vue`
- `ReferralRiskView.vue`

### 3.2 为什么不删 PlaceholderView

`PlaceholderView.vue` 当前虽然在 `src` 搜索未命中，但它不是“薄包装”：

- 它仍是一个可复用的占位容器
- 后续可能承担隐藏治理页或临时占位入口

因此当前仍应放在 `verify-before-delete`，不纳入第一批。

## 4. 风险与边界

### 4.1 已确认

- 两个目标文件删除后不应影响 router / menu / runtime
- 风险低、可逆

### 4.2 待验证

- 是否存在极少见的文档外动态引用
- 删除后构建是否仍完全通过

因此本轮以代码搜索 + `type-check/build` 作为主验证手段。
