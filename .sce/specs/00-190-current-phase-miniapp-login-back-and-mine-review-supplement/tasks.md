# 00-190 当前阶段小程序登录返回与个人中心复核补充 - 任务拆解

## T1 Spec 与计划

- [x] 新增 `00-190` requirements / design / tasks / execution。
- [x] 明确本轮只补登录页返回按钮和个人中心复核记录。

## T2 红灯验收脚本

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 新增 `scripts/verify-miniapp-login-back-and-mine-supplement.mjs`。
- [x] 在实现前运行脚本，确认因登录页缺少返回按钮失败。

## T3 登录页返回按钮实现

**Validates: Requirements 3.1**

- [x] 修改 `kaipai-frontend/src/pages/login/index.vue`，新增顶部返回按钮模板。
- [x] 新增 `handleBack()`，优先 `navigateBack`，无历史或失败时 `reLaunch` 首页。
- [x] 新增登录页本地返回按钮样式，不遮挡胶囊和表单。

## T4 个人中心复核回填

**Validates: Requirements 3.2**

- [x] 在 `execution.md` 明确记录 `pages/mine/index` 复核范围。
- [x] 确认 `00-189` flow matrix 存在 `mine` 流程。
- [x] 确认 `00-189` 截图目录存在 `11-pages-mine-index-default.png`。

## T5 构建与验收

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 执行 `npm run type-check`。
- [x] 执行 `npm run build:mp-weixin`。
- [x] 执行 00-190 验收脚本并通过。
- [x] 执行 00-187 登录门禁脚本并通过。
- [x] 执行 00-188 复审合规脚本并通过。
- [x] 执行 `npm run audit:mp-package` 并通过。
- [x] 检查 `dist/dev/mp-weixin/pages/login/index.wxml` 包含 `login-page__back`。
- [x] 更新 `.sce/specs/README.md` 与 `.sce/specs/spec-code-mapping.md`。

## T6 `mine-v2` 游客账号入口导航竞态回归修复

**Validates: Requirements 3.2, 3.3**

- [x] 复现 `.mine-v2__profile-card -> pages/actor-profile/edit -> pages/login/index` 重叠导航，并确认 `navigateTo / reLaunch timeout` 根因。
- [x] 将 00-190 / 00-192 验收脚本从已退场的 `mine-page__*` 结构更新为当前 `mine-v2` 等价行为。
- [x] 使用 `hasStoredSession / currentUser` 派生 Mine 游客态和账号头部，保留脱敏手机号 fallback。
- [x] 为资料卡、继续完善、个人资料、演艺经历、自我介绍和实名认证统一增加入口级登录门禁。
- [x] 确认游客点击只执行一次 `navigateTo('/pages/login/index')`，不先创建受保护页。
- [x] 执行 type-check、构建、专项门禁、包体审计与微信开发者工具页面栈回归；既有环境门禁红灯按 execution 保留。
- [x] 核对 `src / dist/build / dist/dev` 三层产物并回填 execution / mapping。
