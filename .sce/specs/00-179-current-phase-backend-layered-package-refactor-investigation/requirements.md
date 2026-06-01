# 当前阶段后端分层包结构重构调查 Requirements

> 状态：已调查 / 待接续治理 | 优先级：P0 | 依赖：`00-178`

## 1. 概述

后端远端代码在 `670aeed..bd598a0` 范围内完成了一次大规模分层包结构重构。旧的 `com.kaipai.module` 业务目录已从当前源码运行态退出，后端代码入口改为按 `controller`、`service`、`model`、`mapper`、`integration` 分层组织。

本 Spec 不新增业务能力，也不修改后端运行代码。目标是把本次重构的事实、迁移映射、本地影响、后续治理门禁沉淀为 SCE 文档，避免后续开发继续按旧 `module` 路径落代码。

## 2. 用户故事

- 作为后端开发者，我需要知道当前后端代码应该落在哪个新包根下，避免继续新增 `com.kaipai.module.*`。
- 作为维护者，我需要知道旧本地改动和 stash 应如何迁移到新路径，避免直接 pop 后造成路径冲突或误恢复旧结构。
- 作为实名接入维护者，我需要确认 `00-178` 腾讯云实名能力在新分层结构下的真实落点，避免排障时继续查旧路径。
- 作为项目治理者，我需要知道哪些 agent / 文档仍引用旧路径，并把它们列入后续治理任务。

## 3. 功能需求

### 3.1 建立后端新包结构事实源

**描述**：记录当前后端源码的包根、职责边界和旧 `module` 退出事实。

**验收标准**：

1. WHEN 后续创建后端代码 THEN 默认选择 `com.kaipai.controller`、`com.kaipai.service`、`com.kaipai.model`、`com.kaipai.mapper`、`com.kaipai.integration` 中的对应包根。
2. WHEN 发现新代码试图恢复 `com.kaipai.module.*` THEN 必须视为偏离当前架构，需要先回到本 Spec 复核。
3. WHEN 排查 Mapper 或 MyBatis 类型别名 THEN 以 `com.kaipai.mapper.**` 和 `com.kaipai.model.**.entity` 为当前运行态基线。

### 3.2 沉淀旧路径到新路径迁移映射

**描述**：记录旧 `module` 分层到新顶层包的迁移关系，作为人工迁移本地改动和后续 review 的依据。

**验收标准**：

1. WHEN 旧路径为 `src/main/java/com/kaipai/module/controller/admin/*` THEN 新路径应定位到 `src/main/java/com/kaipai/controller/admin/*`。
2. WHEN 旧路径为 `src/main/java/com/kaipai/module/controller/{domain}/*` THEN 新路径应定位到 `src/main/java/com/kaipai/controller/api/{domain}/*`。
3. WHEN 旧路径为 `src/main/java/com/kaipai/module/server/{domain}/service/*` THEN 新路径应定位到 `src/main/java/com/kaipai/service/{domain}/*`。
4. WHEN 旧路径为 `src/main/java/com/kaipai/module/server/{domain}/mapper/*` THEN 新路径应定位到 `src/main/java/com/kaipai/mapper/{domain}/*`。
5. WHEN 旧路径为 `src/main/java/com/kaipai/module/model/{domain}/*` THEN 新路径应定位到 `src/main/java/com/kaipai/model/{domain}/*`。
6. WHEN 旧路径承载第三方服务商或外部系统适配 THEN 新路径优先定位到 `src/main/java/com/kaipai/integration/*`。

### 3.3 记录腾讯云实名接入在新结构下的落点

**描述**：`00-178` 已接入的腾讯云身份证二要素能力需要在新包结构下重新明确位置。

**验收标准**：

1. WHEN 维护实名认证小程序提交接口 THEN 控制器入口为 `src/main/java/com/kaipai/controller/api/verify/VerifyController.java`。
2. WHEN 维护实名 provider、身份证加密、腾讯云调用 THEN 代码入口为 `src/main/java/com/kaipai/integration/verify/*`。
3. WHEN 维护实名 DTO / entity THEN 代码入口为 `src/main/java/com/kaipai/model/verify/*`。
4. WHEN 维护实名业务状态机 THEN 代码入口为 `src/main/java/com/kaipai/service/verify/*`。

### 3.4 记录本地改动与 stash 迁移边界

**描述**：本次 pull 前存在本地 actor profile 改动，已被保存在 stash 中。该改动基于旧 `module` 路径，不能直接作为当前结构继续应用。

**验收标准**：

1. WHEN 需要恢复 actor profile 本地改动 THEN 先对照新路径人工迁移，不能直接无脑 pop stash。
2. WHEN 看到 `target/classes/*` dirty THEN 识别为编译产物，不纳入本 Spec 文档提交范围。
3. WHEN 本地存在无关未跟踪文件 THEN 本 Spec 不触碰、不删除、不纳入治理结论。

### 3.5 标记 agent 文档与当前结构不一致

**描述**：后端新增的 `.agents/*.md` 文档中仍存在旧 `src/main/java/com/kaipai/module` 路径引用，需要作为后续治理任务处理。

**验收标准**：

1. WHEN 后续使用后端 agent 文档分派任务 THEN 先确认其路径指向是否已更新到新分层结构。
2. WHEN 修复 `.agents` 文档 THEN 应按本 Spec 的迁移映射批量替换旧路径，而不是恢复旧目录。
3. WHEN 本轮只创建调查文档 THEN 不直接修改 `.agents`，避免扩大本次文档任务范围。

### 3.6 留存验证证据

**描述**：记录本次调查使用的命令、关键输出、编译结果和剩余风险。

**验收标准**：

1. WHEN 阅读 `execution.md` THEN 可以看到 commit 范围、变更规模、包结构计数、stash 状态和编译验证结果。
2. WHEN 阅读 `refactor-audit.md` THEN 可以看到详细重构映射、实名影响、配置变化和后续治理事项。
3. WHEN 后续判断后端是否能编译 THEN 以 `cd kaipaile-server && mvn -q -DskipTests compile` 本轮通过作为基础证据。

## 4. 非功能需求

- 本 Spec 只写文档，不修改业务代码、数据库 migration 或运行配置。
- 文档不得包含腾讯云 SecretId、SecretKey、身份证明文或其他敏感值。
- 文档必须明确本次 compile 产生的 `target/classes` dirty 是构建产物，不应随 Spec 提交。
- 文档必须保护现有 stash，不要求 pop、apply 或删除。
- 文档应能作为后续 code review 的路径门禁依据。

## 5. 约束条件

- 不恢复旧 `com.kaipai.module.*` 包结构。
- 不为旧包新增兼容 adapter，除非未来 Spec 明确要求。
- 不触碰根目录已有无关未跟踪文件。
- 不修改 `kaipai-frontend`、`kaipai-admin` 或后端业务源码。
- 如后续要迁移 actor profile 本地改动，必须另建或复用对应业务 Spec。

## 6. 验收总则

1. 新增 `00-179-current-phase-backend-layered-package-refactor-investigation` Spec 目录。
2. Spec 包含 requirements、design、tasks、execution 和重构调查文档。
3. `.sce/specs/README.md` 已登记 `00-179`。
4. 文档明确新包结构、旧新路径映射、实名接入落点、本地 stash 影响、agent 文档后续治理事项。
5. 不引入业务代码改动，不提交敏感信息。
