# 素材库游客态与错误边界收口 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 视觉合同

- 路由：`pages/assets/index`。
- 问题块：素材列表区直接显示底层 `request:fail ...` 与“重新加载”。
- 目标块：素材列表区显示“未登录 / 登录后即可上传、管理并复用你的照片、视频和 PDF / 去登录”。
- 保持不变：导航、照片/视频/PDF Tab、已登录三列照片网格和素材管理操作。

## 2. 状态模型

```ts
const userStore = useUserStore();
const isGuest = computed(() => !userStore.hasStoredSession);
```

`hasStoredSession` 内部会先从 storage hydrate token，适合 `onShow` 首次判定。游客视图优先级高于照片网格、列表、空态、loading 和 error。

## 3. 请求边界

`onShow`：

```text
pageActive=true
  -> guest: resetGuestState(), return
  -> authenticated: load(true)
```

`load()` 自身再保留游客早退，覆盖 Tab 切换、重试或未来调用点。`chooseUpload()` 在打开系统 picker 前调用 `requireLogin()`。

`resetGuestState()`：

- 递增请求 revision，使已发出的旧会话响应不能回写。
- 停止轮询并清理预览 pending/URL/error。
- 清空三类素材列表、页码、总数、错误和重试状态。
- 清空上传/PDF 反馈并结束 loading/uploading。

## 4. 错误文案边界

素材列表 `load()` 的 catch 不再读取 `(error as Error).message` 写入模板，统一使用“素材读取失败，请稍后重试”。业务删除保护等已经明确设计的可行动错误继续由原有对话框处理，不在本 Spec 扩大。

## 5. 验证

新增 `verify-00258-asset-guest-state.mjs`，断言：

1. `useUserStore` 与 `hasStoredSession` 游客事实源存在。
2. 模板存在“未登录 / 去登录”并对游客优先渲染。
3. `load()` 在 `getActorAssets` 前有游客返回。
4. `onShow` 游客只 reset，不调用 load。
5. `chooseUpload` 在 picker 前有登录门禁。
6. 加载 catch 不再把 `error.message` 写入 `pageState.error`。
7. 唯一运行产物 `dist/dev/mp-weixin/pages/assets/index.{wxml,js,wxss}` 包含对应合同。

验证命令：

```text
npm run type-check
npm run verify:asset-guest-state
npm run build:mp-weixin
npm run verify:tdesign-migration
npm run verify:asset-photo-grid
npm run verify:single-runtime-entry
npm run audit:mp-package
```

## 6. 回滚

回滚只恢复 `pages/assets/index.vue`、专项门禁及登记文档，不涉及后端或数据库。证据中的 `ROLLBACK.sh` 默认只恢复到独立副本，实际工作区保持修复态。

## 7. Candidate 与体验版

本轮分配 Candidate ID `20260902-174419-v3-draft`。隔离构建完成后只消费其中的 `mini-program-test`：完整替换唯一 `dist/dev/mp-weixin`，执行项目级 compile 缓存清理，再通过不抬起窗口的内部 MCP 验证游客页面。若门禁通过，CLI 上传版本使用 `3.0.0.20260902.174419`；不提交审核、不发布正式版本。
