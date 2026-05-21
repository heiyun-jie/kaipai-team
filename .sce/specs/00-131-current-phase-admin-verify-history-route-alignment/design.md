# 00-131 设计说明

## 1. 设计目标

`00-131` 只做一件事：

1. 为已有 verify history 权限合同补齐隐藏治理路由 `/verify/history`。

## 2. 已核实事实

### 2.1 当前能力已经存在

当前已有：

- 前端组件：
  - `VerificationBoard.vue`
  - 支持 `mode='history'`
- 前端权限登记：
  - `page.verify.history`
- 后端列表接口权限：
  - `hasAnyAuthority('page.verify.pending','page.verify.history')`
- 当前 dev 角色数据：
  - 已携带 `page.verify.history`

因此：

- `/verify/history` 不是新增业务能力
- 只是把已有能力补成可访问 hidden tooling 路由

### 2.2 当前缺口只在 router

当前 router 中：

- `/verify/pending` 已存在
- `/verify/history` 不存在

因此本轮只需要改 `router/index.ts`。

## 3. 设计策略

### 3.1 直接复用组件

新增 route record：

- path: `verify/history`
- name: `verify-history`
- component: `VerificationBoard.vue`
- props: `{ mode: 'history' }`

### 3.2 保持 hidden tooling 口径

route meta：

- `architectureLayer = 'tooling'`
- `architectureArea = 'tooling'`

不加入：

- `adminSidebarMenus`

### 3.3 不改 pending 路由

`/verify/pending` 已在 `00-129` 收口，不再动它。

## 4. 风险与边界

### 4.1 已确认

- `VerificationBoard.vue` 已有 history mode 分支
- 后端列表接口已允许 `page.verify.history`

### 4.2 验证重点

本轮重点看：

1. `/verify/history` 是否能正常打开
2. 页面首屏是否显示 history 回看语义
3. 不出现 pending 待办语义误用
4. 前端构建是否通过
