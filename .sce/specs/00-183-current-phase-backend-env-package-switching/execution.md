# 00-183 当前阶段后端环境打包切换 - 执行记录

## 1. 改动摘要

- `kaipaile-server/src/main/resources/bootstrap.yml`
  - `spring.profiles.active` 已由固定 `dev` 改为 `${SPRING_PROFILES_ACTIVE:dev}`。
  - `spring.cloud.nacos.config.enabled` 保持 `${NACOS_ENABLED:false}`。
  - Nacos server、namespace、group、file-extension、username、password 未改动。
- `kaipaile-server/scripts/package-backend.ps1`
  - 新增本地后端打包入口。
  - 支持 `-Environment dev|prod`、`-NacosEnabled auto|true|false`、`-SkipTests`。
  - `auto` 规则：`prod -> true`，`dev -> false`。
- `.sce/specs/README.md`
  - 已登记 `00-183 current-phase-backend-env-package-switching`。

## 2. 验证记录

### 2.1 静态配置核验

命令：

```powershell
Select-String -Path src\main\resources\bootstrap.yml -Pattern "SPRING_PROFILES_ACTIVE|NACOS_ENABLED|server-addr|namespace|group|file-extension"
```

结果：

- `active: ${SPRING_PROFILES_ACTIVE:dev}`
- `enabled: ${NACOS_ENABLED:false}`
- `server-addr: 101.43.57.62:8848`
- `namespace: ''`
- `group: DEFAULT_GROUP`
- `file-extension: yml`

### 2.2 Nacos prod dataId 只读核验

目标：

- `dataId=kaipai-backend-prod.yml`
- `group=DEFAULT_GROUP`
- `server=101.43.57.62:8848`

结果：

- HTTP `200`
- 内容长度 `742`
- 已包含 `datasource:` 配置

### 2.3 prod 打包验证

命令：

```powershell
.\scripts\package-backend.ps1 -Environment prod -SkipTests
```

结果：

- `SPRING_PROFILES_ACTIVE=prod`
- `NACOS_ENABLED=true`
- Maven 命令：`mvn -DskipTests clean package`
- `BUILD SUCCESS`
- 生成 JAR：`D:\XM\kaipai-team\kaipaile-server\target\kaipai-backend-1.0.0-SNAPSHOT.jar`

### 2.4 产物配置核验

命令：

```powershell
Get-Content target\classes\bootstrap.yml
```

结果：

- 产物内 `bootstrap.yml` 保留 `${SPRING_PROFILES_ACTIVE:dev}`。
- 产物内 `bootstrap.yml` 保留 `${NACOS_ENABLED:false}`。

## 3. 使用方式

本地开发默认：

```powershell
.\scripts\package-backend.ps1 -Environment dev -SkipTests
```

测试 / 生产环境打包验证：

```powershell
.\scripts\package-backend.ps1 -Environment prod -SkipTests
```

若需手工覆盖 Nacos 开关：

```powershell
.\scripts\package-backend.ps1 -Environment prod -NacosEnabled false -SkipTests
```

最终启动 JAR 时仍需在运行进程环境显式设置：

```powershell
$env:SPRING_PROFILES_ACTIVE = "prod"
$env:NACOS_ENABLED = "true"
java -jar target\kaipai-backend-1.0.0-SNAPSHOT.jar
```

## 4. 说明

本轮没有把 `prod` 写死进源码，也没有把 Nacos 默认值改成 `true`。同一份 JAR 可在不同环境复用，实际运行环境由 `SPRING_PROFILES_ACTIVE` 与 `NACOS_ENABLED` 决定。
