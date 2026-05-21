# 00-128 设计说明

## 1. 设计目标

`00-128` 只处理一个问题：

1. 把前端 permission registry 中最后剩余的 `menu.recruit` 历史登记退场。

## 2. 已核实事实

### 2.1 当前本机 runtime 已不再返回 `menu.recruit`

已确认：

- `GET /admin/auth/me`
- `GET /admin/system/roles/1`

当前返回的 `menuPermissions` 都只包含：

- `menu.dashboard`
- `menu.verify`
- `menu.referral`
- `menu.content`
- `menu.system`
- `menu.users`

不再包含：

- `menu.recruit`

因此：

- 在当前本机 dev 运行态下，角色编辑弹窗已经不需要依赖 registry 历史登记来解释这条菜单。

### 2.2 当前代码里只剩 registry 残留

当前代码搜索已确认：

- `menu.recruit`
- `招募治理菜单（历史登记）`

只剩 `permission-registry.ts` 一处。

因此：

- 本轮改动可限定为单文件最小删除，不必再扩大到后端或页面合同。

## 3. 设计策略

### 3.1 直接删除历史登记

从 `permission-registry.ts` 中删除：

- `historicalMenuRegistry`
- `menu.recruit`
- `招募治理菜单（历史登记）`

并把 `permissionRegistry` 的组装恢复为：

- `menuRegistry`
- `pageRegistryFromMenus`
- `extraPageRegistry`
- `ACTION_META`

### 3.2 不改 moduleOrder

`moduleOrder` 继续保留 `recruit`。

原因：

- recruit 模块本身仍有真实页面 / 动作权限
- 删除历史菜单登记并不影响 recruit 模块的 page/action 树

## 4. 风险与边界

### 4.1 已确认

- 当前本机 runtime 不再返回 `menu.recruit`
- 当前代码无其它消费者

### 4.2 不确定边界

- 本轮只覆盖本机 dev 运行态
- 其它环境若仍有旧角色数据，本轮不主张替它们做兼容

因此本轮结论是：

- 对当前工作主线和本机运行态来说，删除该历史登记是安全且可逆的最小收口

## 5. 验证策略

本轮验证分两层：

1. 前端静态验证
   - `npm run type-check`
   - `npm run build`
2. 真实浏览器验证
   - `/system/roles`
   - 编辑角色弹窗 unknown list 仍为 `0`
   - recruit 模块页面 / 动作权限树仍正常显示
