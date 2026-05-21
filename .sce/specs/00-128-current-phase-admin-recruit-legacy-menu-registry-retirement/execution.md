# 00-128 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-127`
- 已先对当前本机 live session / 角色详情与代码命中点做删除前复核

## 2. 删除前证据

### 2.1 当前本机 live runtime 已不再返回 `menu.recruit`

使用后台账号：

- `account = admin`
- `password = <REDACTED>`

删除前已确认：

- `GET /admin/auth/me`
- `GET /admin/system/roles/1`

两者 `menuPermissions` 都为：

- `menu.dashboard`
- `menu.verify`
- `menu.referral`
- `menu.content`
- `menu.system`
- `menu.users`

都不再包含：

- `menu.recruit`

依据：

- 本机 `127.0.0.1:8010` 登录态接口直接返回

置信度：

- 高

不确定边界：

- 只覆盖本机 dev 运行态，不直接外推到其它环境。

### 2.2 当前代码只剩单点 registry 残留

删除前 `rg` 已确认业务代码命中只剩：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`
  - `historicalMenuRegistry`
  - `menu.recruit`
  - `招募治理菜单（历史登记）`

当前判断：

- 下一步可做单文件最小退场，不需要继续触碰后端。

## 3. 本轮实施

### 3.1 删除 registry 历史登记残留

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`

本轮已删除：

- `historicalMenuRegistry`
- `menu.recruit`
- `招募治理菜单（历史登记）`

同时将 `permissionRegistry` 组装恢复为：

- `menuRegistry`
- `pageRegistryFromMenus`
- `extraPageRegistry`
- `ACTION_META`

### 3.2 删除后复核

删除后 `rg` 已确认：

- `kaipai-admin/src`
  内已不再命中：
  - `menu.recruit`
  - `historicalMenuRegistry`
  - `招募治理菜单（历史登记）`

当前判断：

- 当前主线中 `menu.recruit` 已不再残留于运行时代码
- 当前只在 `.sce` 文档与执行证据中保留历史追溯记录

### 3.3 构建验证

已通过：

- `D:\XM\kaipai-team\kaipai-admin`
  - `npm run type-check`
  - `npm run build`

补充说明：

- 本轮 `build` 仍输出既有 chunk size warning 与 Sass legacy JS API warning
- 当前未新增新的构建报错

## 4. 验证结果

### 4.1 真实浏览器复核

已使用 Playwright CLI 登录：

- `http://127.0.0.1:5100/login`

并复核：

- `http://127.0.0.1:5100/system/roles`
- `编辑角色` 弹窗

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-128\roles-edit-dialog-recruit-tree-after.png`

当前已确认：

- 当前角色编辑弹窗中未出现 unknown list
- 当前 recruit 模块已只保留：
  - `页面权限`
  - `操作权限`
- 当前 recruit 模块下已不再出现历史菜单节点
- 浏览器 console `error` 当前为 `0`

依据：

- 真实浏览器页面快照与截图

置信度：

- 高

不确定边界：

- 该结论只覆盖本机 `5100 / 8010` 当前运行态

### 4.2 当前运行态兼容性结论

结合删除前 API 复核与删除后浏览器复核，当前可确认：

- 本机 live session 与角色详情已不再返回 `menu.recruit`
- 删除前端 registry 历史登记后，当前本机角色编辑弹窗 unknown 仍保持 `0`
- recruit 模块的真实页面 / 动作权限树未被破坏

## 5. 结论

`00-128` 已完成本轮目标：

- 前端 permission registry 中最后一条 `menu.recruit` 历史登记残留已退场
- 当前本机运行态下，角色编辑弹窗 unknown 继续保持 `0`
- recruit 模块权限树已完全收口到真实 `page.recruit.* / action.recruit.*` 口径
