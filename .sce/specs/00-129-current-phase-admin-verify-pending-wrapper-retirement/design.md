# 00-129 设计说明

## 1. 设计目标

`00-129` 只做一件事：

1. 删除 `/verify/pending` 当前的薄包装路由壳 `PendingView.vue`

## 2. 已核实事实

### 2.1 `PendingView.vue` 只是 8 行薄包装

当前文件内容只有：

- 渲染 `VerificationBoard`
- 固定传 `mode="pending"`

它不承担：

- 权限判断
- 数据装配
- 页面逻辑
- 额外状态管理

因此它不是业务页，只是历史路由壳层。

### 2.2 router 已具备直接承接条件

`VerificationBoard.vue` 当前直接声明：

- `mode: 'pending' | 'history'`

因此 router 可以直接切为：

- `component: () => import('@/views/verify/VerificationBoard.vue')`
- `props: { mode: 'pending' }`

这不会改变：

- route path
- route name
- route meta
- pagePermission

## 3. 设计策略

### 3.1 路由直连

只在 `router/index.ts` 做最小改动：

- 保持 `/verify/pending` route record 不变
- 只替换 component import
- 增加 `props: { mode: 'pending' }`

### 3.2 删除单文件

删除：

- `D:\XM\kaipai-team\kaipai-admin\src\views\verify\PendingView.vue`

### 3.3 为什么不继续处理 verify 其它页面

当前 verify 域中最小对象就是 `PendingView.vue`。

相比扩展到：

- `VerificationBoard.vue` 结构拆分
- verify/history 独立化

本轮只删 wrapper：

- 证据最充分
- 风险最低
- 变更最小

## 4. 风险与边界

### 4.1 已确认

- `PendingView.vue` 只被 router 引用
- 删除后唯一关键风险是 router props 传递是否正确

### 4.2 验证重点

本轮验证重点只看：

1. 编译是否通过
2. `/verify/pending` 是否仍正常打开
3. 页面语义是否仍是 pending 队列，而非 history 回看
