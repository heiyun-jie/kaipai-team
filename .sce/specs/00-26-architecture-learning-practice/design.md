# 00-26 设计说明（Execution Design）

## 1. 执行方式

本 Spec 采用“轻计划、重连续性”的执行方式：

1. 以周为单位推进，不强依赖固定时段
2. 每次只保持一个主主题，避免多线程学习
3. 每周必须有一个看得见的输出

## 2. 每日最小动作

每次学习按以下模板执行：

```text
10 分钟：读一个文档 / 读一段代码
40 分钟：做一个小动作
10 分钟：记录结论和明日入口
```

其中“一个小动作”只允许是以下之一：

- 追一个调用链
- 画一张结构图
- 改一个字段或一个接口
- 验证一个发布或构建动作
- 为一个模块补一段说明

## 3. 12 周节奏

### 3.1 第 1-4 周：普通全栈基线

目标：

- 看懂仓库边界
- 跑起核心工程
- 追通一个业务链路
- 做一个小改动

阅读优先级：

- `/.sce/specs/README.md`
- `/.sce/specs/00-10-platform-admin-backend-architecture/requirements.md`
- `/.sce/specs/00-11-platform-admin-console/requirements.md`
- `/docs/ops-infrastructure.md`

代码优先级：

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/**`
- `kaipaile-server/src/main/java/com/kaipai/module/server/**`
- `kaipai-admin/src/views/**`
- `kaipai-frontend/src/pages/**`

### 3.2 第 5-8 周：数据与交付

目标：

- 理解数据迁移和状态流转
- 理解权限与审计
- 理解部署结构和排错入口

重点：

- migration SQL
- 操作日志
- Docker Compose / Nginx / 环境配置
- 本地构建与发布链路

### 3.3 第 9-12 周：AI 业务闭环

目标：

- 围绕 `05-04 ai-resume-polish` 建立 AI 架构认知
- 从“调模型”升级到“设计 AI 功能”

重点：

- 档案上下文组装
- Prompt 约束
- 结构化 patch 输出
- 预览确认与撤销
- 配额与失败兜底
- 历史记录与回滚

## 4. 每周产物要求

每周至少产出以下之一：

- 一份结构图
- 一份模块笔记
- 一个小的代码改动
- 一份验证记录
- 一段新的学习 Spec 备注

## 5. 评估方式

不是按“看完多少课程”评估，而按下面三个问题评估：

1. 我是否能解释这个模块为什么这样设计？
2. 我是否能自己改动并验证一处真实行为？
3. 我是否知道下一步该补哪块，而不是继续泛学？

## 6. 当前建议练手主题

推荐先后顺序：

1. 实名认证审核链路
2. 邀请裂变 / 邀请资格链路
3. 会员 / 后台管理链路
4. `05-04 ai-resume-polish`

原因：

- 前三者能先补齐后端、数据、权限、状态流转
- 第四个最适合作为“全栈 AI 架构”切入题
