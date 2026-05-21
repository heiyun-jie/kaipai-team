# 00-159 执行记录

## 开头先回答三个问题

1. 当前状态是什么：已建立规格，准备按模板页、表格层级、联系方式审批、用户抽屉四条线执行。
2. 执行边界是什么：只改当前后台治理可用性问题，不扩大到小程序页面、不新增资金业务。
3. 完成后怎么验收：以本地类型检查、后台构建、后端编译和代码命中点为本轮验收依据，线上发布另按发布流程执行。

## 2026-05-09 任务建立

触发原因：

- 用户反馈 `http://kplyyk.com/content/templates` 编辑模板时报 `shareCard 缺失或格式错误`。
- 后台多张表格鼠标 hover 时右侧固定操作列层级/透层不正确。
- 联系方式申请待处理记录只有查看详情，没有同意和拒绝按钮。
- 用户管理详情抽屉展示资金概览，但当前系统没有资金等相关信息需要展示。

执行原则：

- 模板历史数据兼容只在编辑入口做默认补齐，保存仍写完整当前合同。
- 表格层级修复放到全局表格样式，避免逐页重复。
- 联系方式审批必须由后台接口承接，不借用持卡人用户端接口。
- 资金信息只从当前用户详情抽屉展示层退场，不做后端字段物理删除。

## 本轮实施

- `TemplatesView.vue` 模板编辑读取 `miniProgramCard`，兼容旧 `shareCard`，节点缺失时用可视化编辑器默认值补齐；保存时写回 `miniProgramCard`。
- `src/styles/index.scss` 统一把表格固定右侧操作列改为不透明独立层，并同步修正用户表、后台账号表和分享内容表的局部覆盖样式。
- 后端新增后台联系方式申请同意 / 拒绝接口，Service 层新增后台审批方法。
- 后台联系方式申请列表对 `pending` 行展示同意 / 拒绝按钮，并用确认弹窗收集处理备注。
- 用户管理详情抽屉移除“资金概览”卡片。

## 本地验证

- `kaipai-admin npm run type-check`：通过。
- `kaipai-admin npm run build`：通过；仅有现有 Sass legacy API 与大 chunk 警告。
- `kaipaile-server mvn -q -DskipTests compile`：通过。

## 线上发布

- 数据库迁移：
  - `20260509-082412-backend-schema-admin-contact-request-action-permissions`：已执行 `V20260509_032__admin_contact_request_action_permissions.sql`，为 `ADMIN` 角色补充 `action.content.contact-request.approve/reject`。
  - `20260509-082539-backend-schema-seed-current-share-card-templates`：后端发布门禁发现前置 `V20260508_031__seed_current_share_card_templates.sql` 未入库，已补执行；该脚本为幂等模板种子数据。
- 后端发布：
  - `20260509-082612-backend-only-admin-contact-request-actions`
  - 发布方式：`git_head_snapshot_with_overlay`，overlay `pom.xml` + `src`。
  - 公网 smoke：`https://api.kplyyk.com` 登录、文档、未登录业务接口检查通过。
- 后台发布：
  - 首次按默认 `https://kplyyk.com` smoke 时因根域名证书不覆盖 `kplyyk.com` 被证书校验拦截，远端静态发布已完成但未生成通过记录。
  - 按实际入口 `http://kplyyk.com` 重新执行标准 `admin-only` 发布并通过：`20260509-082839-admin-only-admin-content-governance-ui-fix-http`。

## 线上验证

- `https://api.kplyyk.com/api/admin/auth/login`：`admin/<KAIPAI_ADMIN_SMOKE_PASSWORD>` 登录返回 `code=200`，权限中包含 `action.content.contact-request.approve` 与 `action.content.contact-request.reject`。
- `https://api.kplyyk.com/api/admin/content/templates?pageNo=1&pageSize=10`：返回 `code=200`，线上模板总数为 3。
- `https://api.kplyyk.com/api/admin/content/contact-requests?pageNo=1&pageSize=10`：返回 `code=200`，线上联系方式申请总数为 6，存在 `pending` 数据。
- `https://api.kplyyk.com/api/v3/api-docs`：已包含 `/admin/content/contact-requests/{requestId}/approve` 与 `/admin/content/contact-requests/{requestId}/reject`。
- 浏览器自动化检查：
  - `http://kplyyk.com/content/templates` 可加载线上模板；点击“基础编辑”后不再出现 `shareCard 缺失或格式错误`，编辑面板可打开。
  - `http://kplyyk.com/content/contact-requests` 待处理行可见 `同意` 与 `拒绝`。
  - `http://kplyyk.com/users/index` 打开用户详情抽屉后未出现“资金概览”等资金展示。
  - 联系方式申请表、用户表固定右侧列 computed style 为非透明背景、`position: sticky`、`z-index: 11`。
  - 页面检查未捕获 console error / page error。
- 浏览器截图留档：`.sce/runtime/admin-content-governance-ui-fix-smoke/`。

## 2026-05-09 追补：联系方式审批按钮置灰

触发原因：

- 用户反馈联系方式申请列表里的 `同意` / `拒绝` 按钮被置灰。

根因：

- 后端权限与接口已经生效，但后台前端启动时如果 localStorage 中已有旧 `kaipai-admin-session`，路由守卫只在 `session` 缺失时才调用 `authStore.bootstrap()`。
- 新增的 `action.content.contact-request.approve/reject` 权限不在旧 session 快照中，`PermissionButton` 因前端权限集合过旧而禁用按钮。

修复：

- `kaipai-admin/src/router/index.ts`：路由守卫改为只要当前有 token 且 `authStore.initialized=false`，就执行 `authStore.bootstrap()`，避免旧 session 快照直接沿用。
- `kaipai-admin/src/stores/auth.ts`：`bootstrap()` 重新拉取后端 session 后同步写回 localStorage，避免旧权限快照长期滞留。

验证：

- `kaipai-admin npm run type-check`：通过。
- `kaipai-admin npm run build`：通过；仅有现有 Sass legacy API 与大 chunk 警告。
- 线上发布：
  - `20260509-084423-admin-only-admin-session-refresh-permission-fix`
  - `20260509-084612-admin-only-admin-session-refresh-permission-fix-persist`
- 线上浏览器自动化模拟旧 session：
  - 初始 localStorage session 不包含 `action.content.contact-request.approve/reject`。
  - 页面加载 `http://kplyyk.com/content/contact-requests` 后，localStorage session 已包含上述两个权限。
  - `同意` / `拒绝` 按钮均为 `disabled=false`。
  - 未捕获 console error / page error。
- 截图留档：`.sce/runtime/admin-session-refresh-permission-fix/contact-requests-stale-session-refresh-persisted.png`。
