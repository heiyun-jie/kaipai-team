# 00-183 当前阶段后端环境打包切换 - 任务拆解

## 任务列表

### T1 后端 bootstrap 环境变量化
**Validates: Requirements 3.1, 3.2**

- [x] `spring.profiles.active` 改为 `${SPRING_PROFILES_ACTIVE:dev}`。
- [x] `NACOS_ENABLED` 保持默认 `false`。
- [x] 保留 Nacos server / namespace / group / file-extension / 认证信息不变。

### T2 标准打包脚本
**Validates: Requirements 3.3**

- [x] 新增 `scripts/package-backend.ps1`。
- [x] 支持 `-Environment dev|prod`。
- [x] 支持 `-NacosEnabled auto|true|false`。
- [x] 支持 `-SkipTests`。
- [x] 打包完成后输出环境摘要与 JAR 路径。

### T3 验证与记录
**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 静态核验 `bootstrap.yml` 占位符。
- [x] Nacos 只读核验 `kaipai-backend-prod.yml` 可读。
- [x] 执行 prod 打包脚本并确认成功。
- [x] 回填 `execution.md`。

## 追溯

- T1 -> requirements.md 3.1, 3.2 / design.md §2
- T2 -> requirements.md 3.3 / design.md §3
- T3 -> requirements.md 3.1, 3.2, 3.3 / design.md §4
