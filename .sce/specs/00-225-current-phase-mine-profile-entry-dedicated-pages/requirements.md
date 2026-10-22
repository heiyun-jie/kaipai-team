# 00-225 当前阶段个人中心资料入口独立承载

## 1. 概述

用户在 `pages/mine/index` 指出「个人资料 / 演艺经历 / 自我介绍」不能都跳到同一个个人资料页面。此前 `00-199` 将职业资料与自我介绍收在 `pages/actor-profile/edit` 同页展开，但本轮用户明确裁决：演艺经历就是设置演艺经历，自我介绍就是设置自我介绍，三者应有可感知且语义独立的承载。

本 Spec 覆盖个人中心资料分组的入口路由、独立页面承载、后端最小接口补齐与 UI 风格约束。

## 2. 用户故事

- 作为演员用户，我点击「个人资料」时，只进入基础/职业资料维护，不被带到演艺经历或自我介绍设置。
- 作为演员用户，我点击「演艺经历」时，进入作品/经历管理页，可以查看、新增、编辑、删除自己的演艺经历。
- 作为演员用户，我点击「自我介绍」时，进入独立自我介绍编辑页，可以只保存自我介绍，不被头像、姓名、年龄等个人资料必填项卡住。

## 3. 功能需求

### 3.1 个人中心入口分流

**描述**：`pages/mine/index` 的资料分组必须按业务语义跳转到不同承载页。

**验收标准**：

- WHEN 点击「个人资料」THEN 跳转 `/pages/actor-profile/edit`。
- WHEN 点击「演艺经历」THEN 跳转 `/pkg-profile/works/index`。
- WHEN 点击「自我介绍」THEN 跳转 `/pkg-profile/intro/index`。
- WHEN 检查源码 THEN 不得再通过 `?tab=experience` / `?tab=intro` 把后两个入口伪装成个人资料页锚点。

### 3.2 演艺经历独立管理

**描述**：新增 `pkg-profile/works/index`，使用本人 `actor_experience` 事实源维护演艺经历。

**验收标准**：

- WHEN 页面加载 THEN 调用 `/api/actor/works` 获取真实演艺经历列表。
- WHEN 用户新增或编辑经历 THEN 调用 `/api/actor/works` 的 POST / PUT 保存，不写占位或示例数据。
- WHEN 用户新增或编辑经历 THEN 表单必须在页面内弹窗 / 底部抽屉中承载，不得作为普通卡片插入列表页面流导致主列表被表单挤下。
- WHEN 用户删除经历 THEN 调用 `/api/actor/works/{id}` DELETE；若后端返回引用保护错误，前端显示明确失败信息。
- WHEN 列表为空 THEN 显示真实空态和新增入口。

### 3.3 自我介绍独立编辑

**描述**：新增 `pkg-profile/intro/index`，只维护 `actor_profile.intro`。

**验收标准**：

- WHEN 页面加载 THEN 读取 `/api/actor/profile/mine` 获取当前自我介绍和 `profileVersion`。
- WHEN 用户保存 THEN 调用独立 intro 保存接口，只更新 `intro`，不要求头像、公开名称、性别、年龄、身高或当前城市同时完整。
- WHEN 版本冲突或网络失败 THEN 显示明确提示，不静默覆盖。
- WHEN 内容超过 2000 字 THEN 前端限制并提示当前字数。

### 3.4 风格与运行态约束

**描述**：两个新增页必须沿用 3.0 蓝白视觉系统和普通返回模式 B，不干扰用户桌面。

**验收标准**：

- WHEN 查看新增页 THEN 使用 `KpFloatingBackButton + 本地居中标题 + sticky/relative 白色导航容器`。
- WHEN 查看顶部导航 THEN 分割线由导航容器底部伪元素承载并预留底部呼吸位。
- WHEN 查看按钮 THEN 显式锁定高度、字号、居中和 disabled 态，避免小程序原生 button 文字排版漂移。
- WHEN 核验 THEN 默认只做源码、build/dev 产物和 MCP 内部项目检查；不得置顶、抢焦点、控制整屏或强杀微信开发者工具。

## 4. 非功能需求

- 新接口为 additive，不能破坏旧前端的 `/api/actor/profile/mine` 合同。
- 本轮不做数据库 DDL / DML。
- 新增页面必须登记在 `pages.json` 的 `pkg-profile` 分包内，避免挤占主包。

## 5. 约束条件

- 用户裁决覆盖 `00-199` 中「职业资料与自我介绍在当前页原位置展开」的旧页面组织方式；旧约定仅保留为历史背景，不再作为本轮验收基线。
- 演艺经历与职业资料不是同一个概念：职业资料仍可留在个人资料页，演艺经历由 `actor_experience` 独立页面维护。
