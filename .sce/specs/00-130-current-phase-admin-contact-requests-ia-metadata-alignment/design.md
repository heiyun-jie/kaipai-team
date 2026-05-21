# 00-130 设计说明

## 1. 设计目标

`00-130` 只处理一个问题：

1. 把 `/content/contact-requests` 的 route meta 与 IA 文案收回 hidden tooling 口径。

## 2. 已核实事实

### 2.1 当前存在“壳层与说明分裂”

已确认：

- `admin-information-architecture.ts`
  - 把 `/content/contact-requests` 识别为 tooling
- `router/index.ts`
  - 却把它标成 `mainline`
- `AdminTopbar.vue`
  - 用 `route.meta.architectureLayer` 决定是否套 mainline 壳层
  - 用 `admin-information-architecture.ts` 产出 eyebrow / description

因此当前实际会出现：

- description 方向是 tooling
- 壳层样式却按 mainline 页处理

这是典型 IA 元数据失真，而不是业务逻辑问题。

### 2.2 当前页仍是 hidden tooling

依据：

- `00-110 legacy-inventory-matrix.md`
- `adminSidebarMenus` 不包含该页
- `menus.ts` 里该页仍在 full capability inventory 中，而非正式 8 页投影

因此本轮目标不是把它升为 mainline，而是把 route meta 拉回 tooling。

## 3. 设计策略

### 3.1 route meta 收正

在 `router/index.ts` 中仅调整：

- `architectureLayer: 'mainline'` -> `architectureLayer: 'tooling'`
- `architectureArea: 'user-center'` -> `architectureArea: 'tooling'`

### 3.2 tooling 描述显式化

在 `admin-information-architecture.ts` 中为 `/content/contact-requests` 增加明确描述，避免继续走过于泛化的默认 fallback 文案。

目标语义：

- 当前页面属于联系方式授权链路治理工具
- 继续承接申请记录、处理结果与双方身份回看
- 不属于正式主导航

## 4. 风险与边界

### 4.1 已确认

- 本轮只改前端元数据和文案
- 不改 API / 权限 / 路由路径

### 4.2 验证重点

本轮重点看：

1. 编译是否通过
2. `/content/contact-requests` 是否仍正常打开
3. topbar 是否按 tooling 页显示 summary / meta chips
4. 文案是否不再伪装为 mainline
