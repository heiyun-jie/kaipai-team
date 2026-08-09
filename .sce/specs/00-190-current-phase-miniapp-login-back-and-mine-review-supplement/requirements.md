# 00-190 当前阶段小程序登录返回与个人中心复核补充

## 1. 概述

`00-189` 已完成小程序全页面 E2E 截图、业务流程矩阵和旧文档整理。本轮作为 `00-189` 的补充，只处理两个复审前细节：

1. 登录页需要增加一个明确的返回按钮。
2. 个人中心需要明确记录已查看和复核，不只隐含在“我的页”流程中。
3. 用户点击底部“我的”Tab 时，应先看到个人中心完整页面内容，不应被页面 onShow 直接重定向到登录页。
4. `mine-v2` 改版后，游客点击资料卡等账号入口必须直接进入登录页，不得先创建受保护页面再由页面守卫重定向登录。

本轮不扩大登录能力、不改注册/验证码/手机号快捷登录流程，不重做 00-189 全量截图。

## 2. 用户故事

作为小程序审核准备人员，我希望用户进入登录页后可以明确返回上一页或首页，避免登录页成为无返回路径的强登录体验。

作为产品负责人，我希望个人中心页面被明确查看并记录证据，便于复审前确认账号页、数据区、设置项和退出入口都在当前运行态内。

作为未登录用户，我希望点击底部“我的”后先看到个人中心页面的账号、数据、快捷入口和设置项，再在我主动点击账号功能时进入登录，而不是刚进入页面就被要求授权登录。

作为未登录用户，我希望点击个人中心资料卡时直接看到可用的登录页，不出现受保护页面与登录页重叠导航导致的白屏。

作为开发者，我希望本轮补充有独立验收脚本，确保后续构建产物中仍保留登录返回按钮和个人中心复核证据。

## 3. 功能需求

### 3.1 登录页增加返回按钮

**描述**：`pages/login/index` 顶部应显示一个自有样式返回按钮，用户点击后优先返回上一页；无上一页时返回首页。

**验收标准**：

- WHEN 用户进入 `pages/login/index` THEN 页面顶部可见“返回”按钮。
- WHEN 渲染登录页顶部导航层 THEN “返回”按钮与右侧微信胶囊按钮处于同一横向行，不出现在胶囊按钮下方。
- WHEN 页面栈长度大于 1 AND 用户点击返回 THEN 调用 `uni.navigateBack()`。
- WHEN 页面栈长度不大于 1 OR `navigateBack` 失败 THEN 回退到 `uni.reLaunch({ url: '/pages/home/index' })`。
- WHEN 构建 `mp-weixin` THEN `dist/build/mp-weixin/pages/login/index.wxml` 与 `dist/dev/mp-weixin/pages/login/index.wxml` 都包含登录页返回按钮节点。
- WHEN 执行 00-190 验收脚本 THEN 源码和构建产物必须保留 `login-page__topbar`，并确保返回按钮位于 stage 内容之前的顶部导航层。
- WHEN 执行复审文案检查 THEN 返回按钮不得引入“微信 / WECHAT / 朋友圈 / 微信分享面板”等平台品牌混淆文案。

### 3.2 个人中心明确复核

**描述**：基于 `00-189` E2E 结果，补充记录 `pages/mine/index` 的复核范围，明确个人中心已查看；同时确保未登录用户点击底部“我的”Tab 时可先停留在个人中心，并看到当前 `mine-v2` 页面主要内容。游客主动点击账号能力后，由 Mine 入口完成一次直接登录导航，受保护页面的深链守卫继续保留。

**验收标准**：

- WHEN 未登录用户点击底部“我的”Tab THEN 小程序应停留在 `pages/mine/index`，不得在 `onShow` 阶段直接跳转 `pages/login/index`。
- WHEN 未登录用户进入 `pages/mine/index` THEN `.mine-v2__profile-card` 展示“未登录用户”，页面仍展示资料完整度、统计区、演员资料和账户与服务，不得只显示登录入口和空白内容。
- WHEN 未登录用户点击 `.mine-v2__profile-card` 或“继续完善” THEN Mine 入口直接 `navigateTo('/pages/login/index')`，不得先 `navigateTo('/pages/actor-profile/edit')`。
- WHEN 未登录用户点击“个人资料 / 演艺经历 / 自我介绍 / 实名认证” THEN 统一先经过全局 Session 门禁，游客直接进入 `pages/login/index`。
- WHEN Mine 入口判定游客需要登录 THEN 单次点击只能发起一次 `navigateTo('/pages/login/index')`，不得同时触发受保护页 `navigateTo` 与页面守卫 `reLaunch`。
- WHEN 游客从 Mine 触发登录 THEN 页面栈不得出现 `pages/actor-profile/edit` 或 `pkg-card/verify/index`，控制台不得出现 `navigateTo:fail timeout` / `reLaunch:fail timeout`。
- WHEN 用户已经登录 THEN 上述六个入口继续进入各自目标页；受保护页面仍保留 `ensureUserSessionReady()` 处理直接深链访问。
- WHEN 读取 `00-189` flow matrix THEN 存在 `mine` 流程行。
- WHEN 检查 `00-189` 截图目录 THEN 存在 `11-pages-mine-index-default.png`。
- WHEN 回填 `00-190 execution.md` THEN 明确列出个人中心复核区域：个人资料、我的数据、快捷入口、设置项、退出登录。

### 3.3 独立验收脚本

**描述**：新增脚本验证登录返回按钮和个人中心复核证据，便于复审包构建后重复执行。

**验收标准**：

- WHEN 登录页源码未实现返回按钮 THEN 脚本失败。
- WHEN 登录页源码、build 产物和 dev 产物都包含返回按钮 AND 个人中心证据存在 THEN 脚本通过。
- WHEN 个人中心截图或流程矩阵缺失 THEN 脚本失败并输出具体缺失项。
- WHEN `pages/mine/index` 重新引入 `ensureUserSessionReady` 并在页面展示阶段强制登录 THEN 脚本失败。
- WHEN `pages/mine/index` 不再消费 `hasStoredSession / currentUser`，或 `.mine-v2__profile-card` 绕过入口门禁直接进入受保护页 THEN 脚本失败。
- WHEN `pages/mine/index` 游客态不再显示资料完整度、统计区、演员资料和账户与服务 THEN 脚本失败。
- WHEN `dist/build` 或 `dist/dev` 未同步 Mine 的直接登录门禁语义 THEN 产物层检查失败。

## 4. 非功能需求

- 返回按钮为自有 UI，不使用微信官方 logo、不使用平台品牌化登录文案。
- 返回按钮点击区域不遮挡微信胶囊按钮、输入框、验证码按钮、登录按钮和协议勾选区。
- 个人中心游客态不得调用需要 token 的账号 API，避免 401 被全局 request 拦截后跳登录。
- Mine 点击处理函数不得向 Vue 原生事件处理器返回 `uni.navigateTo()` Promise，避免导航失败形成未处理拒绝。
- 本轮不改登录 API、session 恢复、首页游客态、资料页深链守卫或现有页面布局。

## 5. 约束条件

- 遵循 `SHARED_CONVENTIONS.md` 中小程序自定义导航和返回按钮规范。
- 继续以 `00-187 / 00-188 / 00-189` 为复审整改上游依据。
- 微信开发者工具仍固定打开 `kaipai-frontend/dist/dev/mp-weixin`。
