# 小程序构建期依赖审计分类刷新

## 1. 概述

重新冻结 `00-254` 全栈测试 Candidate 时，`npm audit --omit=dev` 新增报告 `browserslist` 和 `postcss-selector-parser`。两者由 UniApp 多平台编译依赖树引入，冻结小程序产物中没有对应代码、source map、Node 包清单或 `node_modules`。现有 `00-231` fail-closed 分类集合尚未登记这两个包，导致 Candidate 被标记为 `DEPENDENCY_AUDIT_REVIEW_PENDING`。

本 Spec 只刷新已经完成产物不可达性复核的构建期 advisory 集合，不改变 critical=0、运行时 i18n 版本、产物标记扫描、到期时间和未知 advisory 阻断规则。

## 2. 用户故事

- 作为发布维护者，我希望新出现的 advisory 先经过依赖链和冻结产物可达性复核，再决定是否属于构建工具链残余。
- 作为测试负责人，我希望已确认不可进入客户端运行产物的构建期 advisory 不阻断同一代码 Candidate 的测试部署。
- 作为安全审计者，我希望未知包、运行时命中、source map、包清单、critical 或过期风险继续 fail-closed。

## 3. 功能需求

### 3.1 构建期 advisory 事实

- `browserslist` 必须能追溯到 Babel/Autoprefixer/UniApp 编译链，冻结小程序运行产物字符串命中为 0。
- `postcss-selector-parser` 必须能追溯到 UniApp/PostCSS 编译链，冻结小程序运行产物字符串命中为 0。
- 最终产物必须继续不含 `.map`、Node 包清单和 `node_modules`。

### 3.2 分类刷新

- 只把 `browserslist` 和 `postcss-selector-parser` 加入 `MINI_PROGRAM_BUILD_ONLY_ADVISORY_PACKAGES`。
- `classify_miniprogram_dependency_audit()` 的其他门禁保持不变。
- 未登记 advisory 必须继续返回 `REVIEW_REQUIRED / NOT_ACCEPTED`。

### 3.3 发布边界

- 本次分类只允许 Candidate 继续走隔离测试冻结与部署，不构成正式发布授权。
- 风险决定继续为 `RISK_ACCEPTED_WITH_EXPIRY`，到期时间沿用 `2026-09-30T23:59:59+08:00`。

## 4. 验收标准

- 发布构建脚本单测覆盖两个新增已复核包以及未知 advisory 阻断。
- 发布脚本全量单测通过。
- 新 Candidate 的 `unreviewedAdvisoryPackages` 为空、产物可达性证明通过。
- 新 Candidate 不再包含 `DEPENDENCY_AUDIT_REVIEW_PENDING`，但正式发布相关 blocker 保持不变。

## 5. 约束

- 不升级或改写前端依赖，不修改小程序业务代码。
- 不手工篡改 Candidate manifest；分类结果必须由构建证据重新生成。
- 不执行生产数据库、生产容器、正式 Nginx 或正式小程序变更。
