# 00-183 当前阶段后端环境打包切换

## 1. 概述

后端已接入 Nacos 配置中心，但 `bootstrap.yml` 当前把 `spring.profiles.active` 固定为 `dev`，导致测试 / 生产打包与运行前需要手工改文件才能切到 `prod`。这种方式容易造成源码漂移，也容易把本地开发环境误连到生产配置。

本 Spec 负责把后端环境选择改为外部环境变量驱动，并提供标准本地打包入口。打包产物仍保持同一份 Spring Boot JAR；环境差异由 `SPRING_PROFILES_ACTIVE` 与 `NACOS_ENABLED` 在打包验证或运行时决定，不把 `prod` 写死进源码。

## 2. 用户故事

作为开发者，我希望本地默认仍使用 `dev`，不需要额外设置也能继续开发。

作为发布人员，我希望测试 / 生产打包时可以显式指定 `prod`，并自动启用 Nacos，避免每次手工修改 `bootstrap.yml`。

作为维护者，我希望环境切换方式可追溯、可复用，后续排查时能从脚本输出直接确认本次选择的 profile 与 Nacos 开关。

## 3. 功能需求

### 3.1 `bootstrap.yml` 支持外部 profile 覆盖

**描述**：`spring.profiles.active` 不再固定为 `dev`，必须支持通过 `SPRING_PROFILES_ACTIVE` 覆盖，默认值仍为 `dev`。

**验收标准**：

- WHEN 未设置 `SPRING_PROFILES_ACTIVE` THEN 后端默认激活 `dev`。
- WHEN 设置 `SPRING_PROFILES_ACTIVE=prod` THEN 后端激活 `prod`，并按 Spring Cloud Nacos 规则读取 `kaipai-backend-prod.yml`。
- WHEN 源码提交 THEN 不得把 `prod` 写死为默认值。

### 3.2 Nacos 开关继续由环境变量控制

**描述**：`spring.cloud.nacos.config.enabled` 继续使用 `NACOS_ENABLED` 控制，默认不启用，测试 / 生产环境通过外部环境或打包脚本显式打开。

**验收标准**：

- WHEN 未设置 `NACOS_ENABLED` THEN 默认值为 `false`。
- WHEN 设置 `NACOS_ENABLED=true` THEN 启用 Nacos 配置中心。
- WHEN `prod + Nacos` 运行 THEN 目标 dataId 为 `kaipai-backend-prod.yml`。

### 3.3 提供标准打包入口

**描述**：新增后端本地打包脚本，允许通过参数选择 `dev` 或 `prod`，并按环境自动解析 Nacos 开关。

**验收标准**：

- WHEN 执行 `scripts/package-backend.ps1 -Environment dev -SkipTests` THEN 使用 `dev`，默认不启用 Nacos。
- WHEN 执行 `scripts/package-backend.ps1 -Environment prod -SkipTests` THEN 使用 `prod`，默认启用 Nacos。
- WHEN 显式传入 Nacos 开关 THEN 以显式参数为准。
- WHEN 打包完成 THEN 输出 profile、Nacos 开关与 JAR 路径。

## 4. 非功能需求

- 不引入新的后端运行依赖。
- 不改变 Nacos server 地址、namespace、group、账号与密码。
- 不改变现有 release 总控脚本，只补本地 / 手工打包入口。

## 5. 约束条件

- 同一份 JAR 应可在不同环境复用，最终运行环境仍以进程环境变量为准。
- 本轮不负责修改远端 Nacos 配置内容；只核验目标 dataId 是否可读。
