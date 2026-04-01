# Week 01（2026-04-01 ~ 2026-04-07）

## 本周目标

第 1 周不追求“把所有工程都完整跑起来”，只追求三件事：

1. 看懂当前仓库的三端结构
2. 追通“实名认证审核”这条普通业务链路
3. 留下一份自己的结构图和一份链路笔记

## 执行规则

- 每天默认 1 小时，按 `10 + 40 + 10` 执行
- 如果当天只有 20-30 分钟，优先完成“读文档 / 读代码 + 记录结论”
- 本周只保留一个主题：实名认证审核链路
- 启动环境是加分项，不是第 1 周唯一目标

## Day 1｜2026-04-01

主题：看懂仓库边界

阅读：

- `.sce/specs/README.md`
- `.sce/specs/00-10-platform-admin-backend-architecture/requirements.md`
- `.sce/specs/00-11-platform-admin-console/requirements.md`

动作：

- 用你自己的话写出这三个工程分别负责什么：
  - `kaipai-frontend`
  - `kaipai-admin`
  - `kaipaile-server`
- 画一个最简结构图，哪怕只是文本版

今日产物：

- 一张三端结构图
- 一段不超过 10 行的“项目边界说明”

完成标准：

- 能说清楚为什么当前阶段是“模块化单体”，不是微服务

## Day 2｜2026-04-02

主题：从后台页面追到 API

阅读：

- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/api/verify.ts`
- `kaipai-admin/src/types/verify.ts`

动作：

- 找出实名认证列表页有哪些操作
- 记录页面在什么时机调用了哪些 API
- 写一条“页面 -> API 方法”的追踪链

今日产物：

- 一份页面行为清单
- 一份 API 调用关系笔记

完成标准：

- 能回答“点一次审核通过，前端会调用哪个方法”

## Day 3｜2026-04-03

主题：从 API 追到后端分层

阅读：

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/IdentityVerificationService.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`

动作：

- 找出列表查询、详情查询、审核通过、审核拒绝分别落在哪个方法
- 记录 Controller / Service 各自负责什么
- 写一条“前端 API -> Controller -> Service”追踪链

今日产物：

- 一份后端分层笔记
- 一张调用链草图

完成标准：

- 能回答“审核拒绝时，业务逻辑主要落在谁身上”

## Day 4｜2026-04-04

主题：看懂数据模型

阅读：

- `kaipaile-server/src/main/java/com/kaipai/module/model/verify/entity/IdentityVerification.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/mapper/IdentityVerificationMapper.java`
- `kaipaile-server/src/main/resources/db/migration/V20260331_001__platform_admin_baseline.sql`

动作：

- 找出 `identity_verification` 这张表的核心字段
- 写出这张表至少 3 个索引为什么存在
- 记录认证状态有哪些，状态是如何流转的

今日产物：

- 一份 `identity_verification` 数据模型笔记
- 一份状态流转草图

完成标准：

- 能回答“为什么审核类业务不能只靠前端状态判断”

## Day 5｜2026-04-05

主题：准备本地启动

阅读：

- `kaipai-admin/README.md`
- `kaipaile-server/src/main/resources/bootstrap.yml`
- `kaipaile-server/src/main/resources/application.yml`
- `kaipaile-server/src/main/resources/application-dev.yml`

动作：

- 记录后台 Web 启动命令
- 记录后端服务启动所需的 Java / 数据库 / Redis 依赖
- 确认哪些配置是本地已有，哪些可能卡住

建议尝试：

- `kaipai-admin`：`npm install`，`npm run dev`
- `kaipaile-server`：准备 `Java 17 + Maven`，然后尝试 `mvn spring-boot:run`

今日产物：

- 一份启动命令清单
- 一份“已具备条件 / 可能阻塞项”清单

完成标准：

- 即使没完全跑起来，也能清楚说出阻塞点是什么

## Day 6｜2026-04-06

主题：做一个最小改动

前提：

- 如果本地环境已可验证，做一个低风险小改动
- 如果环境仍未准备好，只做“计划中的改动设计”和验证路径说明

可选练习：

1. 在实名认证后台页面挑一个低风险文案或展示字段做微调
2. 在后端查询结果里追一个字段，并验证它如何显示到页面
3. 补一段你自己的验证说明，明确这条链路如何测试

今日产物：

- 一个最小改动，或一份最小改动设计稿
- 一段验证步骤说明

完成标准：

- 你能说清楚“这不是盲改，我知道它影响哪条链路”

## Day 7｜2026-04-07

主题：复盘

动作：

- 回看本周所有笔记
- 补齐你还没写完的结构图、链路图或阻塞清单
- 只回答这 4 个问题：
  1. 我已经看懂了哪些边界？
  2. 我还不懂的点是什么？
  3. 第 2 周最该继续追哪一条线？
  4. 当前最大的真实阻塞是技术问题还是时间分配问题？

今日产物：

- 一页周复盘

完成标准：

- 能明确第 2 周继续的单一主题，而不是重新发散

## 本周最低保底线

如果这一周时间被打断，最低也要完成以下 3 项：

1. Day 1 的三端结构图
2. Day 2-4 的实名认证调用链笔记
3. Day 7 的周复盘

## 今天就做什么

今天是 `2026-04-01`，只做 Day 1：

1. 读 `README` 和 `00-10 / 00-11`
2. 写出三端边界
3. 画一张最简结构图

今天不要再额外打开第二个学习主题。
