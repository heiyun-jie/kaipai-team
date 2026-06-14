# 00-183 当前阶段后端环境打包切换 - 技术设计

## 1. 改动范围

| 层 | 文件 | 改动 |
|----|------|------|
| 后端配置 | `kaipaile-server/src/main/resources/bootstrap.yml` | `spring.profiles.active` 改为 `${SPRING_PROFILES_ACTIVE:dev}` |
| 后端脚本 | `kaipaile-server/scripts/package-backend.ps1` | 新增按环境打包入口 |
| SCE | `.sce/specs/README.md` | 登记 `00-183` |

不新增 Java 代码、不新增接口、不新增数据库 migration。

_Requirements: 3.1, 3.2, 3.3_

## 2. 配置加载规则

`bootstrap.yml` 保留 Spring Cloud Bootstrap 加载方式：

```yaml
spring:
  application:
    name: kaipai-backend
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  cloud:
    nacos:
      config:
        enabled: ${NACOS_ENABLED:false}
```

当 `SPRING_PROFILES_ACTIVE=prod` 且 `NACOS_ENABLED=true` 时，Nacos 配置中心按 `application.name + profile + file-extension` 解析目标 dataId：`kaipai-backend-prod.yml`。

_Requirements: 3.1, 3.2_

## 3. 打包脚本设计

新增 `kaipaile-server/scripts/package-backend.ps1`：

- 参数 `-Environment dev|prod`，默认 `dev`。
- 参数 `-NacosEnabled auto|true|false`，默认 `auto`。
- `auto` 规则：`prod -> true`，`dev -> false`。
- 参数 `-SkipTests`，传入时执行 `mvn -DskipTests clean package`。
- 脚本在当前进程设置：
  - `SPRING_PROFILES_ACTIVE`
  - `NACOS_ENABLED`
- 打包完成后输出：
  - 当前 profile
  - Nacos 开关
  - Maven 命令
  - JAR 路径

说明：脚本设置的环境变量会影响本次 Maven 进程及测试 / 插件执行环境；最终 JAR 启动时仍应由运行进程环境变量显式指定，避免把生产环境写死进产物。

_Requirements: 3.3_

## 4. 验证方案

- `bootstrap.yml` 静态核验：确认 `SPRING_PROFILES_ACTIVE` 与 `NACOS_ENABLED` 占位符存在。
- Nacos 只读核验：确认 `kaipai-backend-prod.yml` 可从 `101.43.57.62:8848` 读取。
- 打包验证：执行 `kaipaile-server/scripts/package-backend.ps1 -Environment prod -SkipTests`，确认 Maven package 通过并生成 JAR。

_Requirements: 3.1, 3.2, 3.3_

## 5. 不做什么

- 不把 `prod` 作为源码默认 profile。
- 不把 Nacos 默认值改为 `true`。
- 不调整远端 Nacos 配置内容。
- 不修改现有后端 release 总控脚本。
