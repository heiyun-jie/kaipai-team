# 00-225 当前阶段个人中心资料入口独立承载 - 技术设计

## 1. 路由配置

`pages.json` 在 `pkg-profile` 分包中新增：

- `works/index`：演艺经历管理。
- `intro/index`：自我介绍编辑。

`pages/mine/index` 的资料入口调整为：

| 入口 | 目标 |
|---|---|
| 个人资料 | `/pages/actor-profile/edit` |
| 演艺经历 | `/pkg-profile/works/index` |
| 自我介绍 | `/pkg-profile/intro/index` |

## 2. 依赖清单

前端：

- `src/pages/mine/index.vue`
- `src/pages/actor-profile/edit.vue`
- `src/pkg-profile/works/index.vue`
- `src/pkg-profile/intro/index.vue`
- `src/api/actor-work.ts`
- `src/api/actor.ts`
- `src/types/profile.ts`
- `src/pages.json`
- `scripts/verify-v3-mine.mjs`

后端：

- `ActorProfileController`
- `ActorProfileWriteService`
- `ActorProfileWriteServiceImpl`
- 新增 `ActorProfileIntroUpdateDTO`

## 3. 页面状态定义

### 3.1 `pkg-profile/works/index`

- `works`: 当前真实演艺经历列表。
- `loading / saving / deletingId / loadError`: 请求状态。
- `formVisible / editingId`: 新增与编辑弹窗状态。
- `form`: `ActorWorkSave` 草稿。
- `formSnapshot`: 弹窗打开时的草稿快照，用于取消 / 返回时识别未保存修改。

页面只消费 `/api/actor/works`，不从个人资料页字段或演员卡步骤页复制占位数据。

### 3.2 `pkg-profile/intro/index`

- `profileVersion`: 保存版本。
- `intro`: 当前编辑文本。
- `baseline`: 脏状态对比。
- `loading / saving / loadError`: 请求状态。

保存调用 `PUT /api/actor/profile/mine/intro`，payload 为 `{ expectedProfileVersion, intro }`。

## 4. 模板结构

两个新增页均使用模式 B：

```text
root
  nav
    KpFloatingBackButton
    居中标题
  scroll/body
    真实内容卡片 / 空态 / 经历列表
  modal
    mask
    bottom sheet
      title + cancel
      scrollable form
      fixed save button
  fixed footer（需要时）
```

导航分割线使用 `::after`，按钮显式清理原生 `button` 的 margin/padding/after。

`pkg-profile/works/index` 的新增 / 编辑表单属于临时编辑任务，必须使用页面内弹窗 / 底部抽屉承载；不得把长表单作为普通卡片插入主滚动列表，避免列表页被改造成表单页。

## 5. 交互逻辑

### 5.1 演艺经历

- 首次进入加载第一页真实列表。
- 「新增经历」打开底部抽屉表单，主列表保持在背景层。
- 点击已有经历的「编辑」把该项映射进底部抽屉表单。
- 保存时：
  - 无 `editingId` → `POST /api/actor/works`
  - 有 `editingId` → `PUT /api/actor/works/{id}`
- 点击遮罩、取消或系统返回时，如表单有未保存变更，先提示「放弃修改 / 继续编辑」；保存成功后关闭抽屉并刷新列表。
- 删除时弹确认，确认后 `DELETE /api/actor/works/{id}`。
- `PROFILE_WORK_IN_USE` 等后端保护错误直接显示后端错误文案。

### 5.2 自我介绍

- 首次进入读 `GET /api/actor/profile/mine`。
- 编辑 textarea 后，底部按钮保存。
- 保存只更新 intro，不要求核心资料完整。
- 有未保存变更时返回需操作表确认。

## 6. 生命周期

- `onLoad`：检查演员登录态并加载页面数据。
- `onBackPress`：如有未保存草稿或正在编辑表单，拦截并提示。
- 不在生命周期里做桌面级 DevTools 操作。

## 7. 页面跳转关系

```text
pages/mine/index
  ├─ 个人资料 -> pages/actor-profile/edit
  ├─ 演艺经历 -> pkg-profile/works/index
  └─ 自我介绍 -> pkg-profile/intro/index
```

## 8. 发版兼容

- 后端仅新增 `PUT /api/actor/profile/mine/intro`，旧接口不变。
- 不新增表/列，不需要数据库迁移。
- 前端新增分包页面，旧版本小程序不消费该新接口，不破坏旧版本。
