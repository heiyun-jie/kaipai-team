# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`20260511-091559-backend-only-ai-profile-artifact-delete`
- 发布时间：`2026-05-11 09:16:55 +0800`
- 发布范围：`backend-only`
- 操作人：`codex`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 使用标准发布脚本执行一次 `backend-only` 发布

## 2. 发布前检查

- 目标环境：
  - 远端主机：`101.43.57.62`
  - 公网审查域名：`https://api.kplyyk.com`
  - 后端运行目录：`/opt/kaipai`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本地工程目录：`D:\XM\kaipai-team\kaipaile-server`
  - 本地发布源模式：`working_tree`
  - 本地构建根目录：`D:\XM\kaipai-team\kaipaile-server`
  - 本地工作树非 target 脏改：`none`
  - 本轮 overlay 文件：`none`
  - 本地构建 JDK：`C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot`
  - 远端重建方式：`docker compose build kaipai && docker compose up -d --force-recreate kaipai`
  - 运行环境变量回读：见下方 `DOCKER_INSPECT_ENV`
- 管理端运行时集合核对：
  - 本轮不发布管理端，仅要求 `/api` 反代仍正常
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 backend-only 脚本发布`

## 3. 产物信息

### 3.1 后端

- 本地 jar 路径：`D:\XM\kaipai-team\kaipaile-server\target\kaipai-backend-1.0.0-SNAPSHOT.jar`
- 本地 jar SHA256：`C5565F8F0C765BAB422CCF031028584D8A370FB29D649B46E1B9309591B6529F`
- 远端备份路径：`/opt/kaipai/backups/releases/20260511-091559-backend-only-ai-profile-artifact-delete/backend`
- 远端落地路径：`/opt/kaipai/builds/20260511-091559-backend-only-ai-profile-artifact-delete/kaipai-backend-1.0.0-SNAPSHOT.jar`
- 当前运行 jar：`/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
- 当前运行 jar SHA256：`C5565F8F0C765BAB422CCF031028584D8A370FB29D649B46E1B9309591B6529F`
- 容器内 `/app/app.jar` SHA256：`C5565F8F0C765BAB422CCF031028584D8A370FB29D649B46E1B9309591B6529F`

### 3.2 管理端

- 本地源码目录：`N/A`
- 本地快照仓库：`N/A`
- 本地 release branch：`N/A`
- 本地 release commit：`N/A`
- 远端静态备份路径：`N/A`
- 远端源码落地路径：`N/A`
- 远端 bare repo：`N/A`
- 远端检出 branch / commit：`N/A`
- 远端 dist 归档路径：`N/A`
- 远端 dist 归档 SHA256：`N/A`
- `index.html` 回读结果：`N/A`

## 4. 执行摘要

- 后端执行命令摘要：
  - 本地：`mvn -q -DskipTests clean package`
  - 本地：`scp kaipai-backend-1.0.0-SNAPSHOT.jar kaipaile@101.43.57.62:/home/kaipaile/backend-release-uploads/20260511-091559-backend-only-ai-profile-artifact-delete/kaipai-backend-1.0.0-SNAPSHOT.jar`
  - 远端：`sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --release-id 20260511-091559-backend-only-ai-profile-artifact-delete --upload-path /home/kaipaile/backend-release-uploads/20260511-091559-backend-only-ai-profile-artifact-delete/kaipai-backend-1.0.0-SNAPSHOT.jar --jar-sha C5565F8F0C765BAB422CCF031028584D8A370FB29D649B46E1B9309591B6529F --operator-user kaipaile`
  - 远端：`docker compose build kaipai && docker compose up -d --force-recreate kaipai`
- 管理端执行命令摘要：`无`
- 是否执行回滚：`否`

## 5. smoke 结果

- 后端容器状态：

```text
NAMES                 IMAGE                                            STATUS                  PORTS
kaipai-backend        kaipai-kaipai                                    Up 8 seconds            0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
clirelay-8388-green   clirelay-8388:20260502-monitor-token-units       Up 44 hours (healthy)   8317/tcp, 8388/tcp
clirelay-8388-blue    clirelay-8388:20260429-1150-imagepage-fix        Up 44 hours (healthy)   8317/tcp, 8388/tcp
clirelay-8388-proxy   clirelay-8388-proxy:20260428-224900-quota-fix2   Up 46 hours             0.0.0.0:8388->8388/tcp, [::]:8388->8388/tcp
kaipai-mysql          mysql:8.0                                        Up 2 days               0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp, 33060/tcp
nacos                 nacos/nacos-server:v2.3.2                        Up 2 weeks              0.0.0.0:8848->8848/tcp, [::]:8848->8848/tcp, 0.0.0.0:9848->9848/tcp, [::]:9848->9848/tcp
kaipai-redis          redis:7                                          Up 2 weeks              0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp
```

- Docker Compose 状态：

```text
NAME             IMAGE           COMMAND                  SERVICE   CREATED         STATUS         PORTS
kaipai-backend   kaipai-kaipai   "java -jar app.jar"      kaipai    9 seconds ago   Up 9 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp
kaipai-mysql     mysql:8.0       "docker-entrypoint.s…"   mysql     2 days ago      Up 2 days      0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp
kaipai-redis     redis:7         "docker-entrypoint.s…"   redis     6 weeks ago     Up 2 weeks     0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

- 运行时环境变量：

```text
SERVER_PORT=8080
AI_PROFILE_CARD_KPLYYK_AUTH_TOKEN=[REDACTED]
SPRING_PROFILES_ACTIVE=dev
AI_PROFILE_CARD_PROVIDER_CODE=kplyyk
NACOS_ENABLED=false
SPRING_DATA_REDIS_HOST=redis
SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/kaipai_dev?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false&connectTimeout=3000&socketTimeout=3000
SPRING_DATASOURCE_USERNAME=[REDACTED]
SPRING_DATASOURCE_PASSWORD=[REDACTED]
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=[REDACTED]
PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
JAVA_HOME=/opt/java/openjdk
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
JAVA_VERSION=jdk-17.0.18+8
```

- Compose 后端来源摘录：

```text
4:services:
6:    image: mysql:8.0
7:    container_name: kaipai-mysql
9:    environment:
13:    ports:
19:    image: redis:7
20:    container_name: kaipai-redis
23:    ports:
29:    image: nginx:latest
30:    container_name: kaipai-nginx
32:    ports:
38:  kaipai:
40:    container_name: kaipai-backend
42:    ports:
49:    environment:
50:      - NACOS_ENABLED=false
51:      - SPRING_PROFILES_ACTIVE=dev
52:      - SERVER_PORT=8080
```

- Compose 渲染后后端定义摘录：

```text
2:services:
3:  kaipai:
7:    container_name: kaipai-backend
15:    environment:
18:      NACOS_ENABLED: "false"
19:      SERVER_PORT: "8080"
26:      SPRING_PROFILES_ACTIVE: dev
29:    ports:
42:    container_name: kaipai-mysql
43:    environment:
47:    image: mysql:8.0
50:    ports:
63:    container_name: kaipai-nginx
64:    image: nginx:latest
67:    ports:
89:    container_name: kaipai-redis
90:    image: redis:7
93:    ports:
```

- `/api/v3/api-docs`：

```text
status=200
{"openapi":"3.0.1","info":{"title":"开拍了 API 文档","version":"v1.0.0"},"paths":"[REDACTED: docs body omitted in committed release record]"}
```

- 业务接口 smoke：
  - 内网：`POST http://127.0.0.1:8080/api/admin/auth/login`

```text
status=200
{"code":200,"message":"操作成功","data":{"accessToken":"[REDACTED]","adminUserInfo":{"adminUserId":2,"account":"admin","userName":"admin","phone":"[REDACTED]","email":"[REDACTED]","roleCodes":["ADMIN"],"permissions":"[REDACTED]"}}}
```

  - 内网：`GET http://127.0.0.1:8080/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=`

```text
status=401
{"code":401,"message":"未登录或Token已过期","data":null}
```

  - 内网：`GET http://127.0.0.1:8080/api/role/search?page=1&size=1&keyword=&gender=`

```text
status=401
{"code":401,"message":"未登录或Token已过期","data":null}
```

- 管理端首页：`N/A`
- 实际静态入口资源 smoke：`N/A`
- 后台页面人工验证：`N/A`
- 联合 smoke：`N/A`

## 6. 结论

- 最终结论：`完成`
- 发布后审查：
  - 公网审查域名：`https://api.kplyyk.com`
  - 审查门禁：`通过`
  - 判定规则：远端 helper 完成重建、内网 smoke 通过、公网 API smoke 通过、发布记录已写入 `records/`
- 问题与备注：
  - 本轮通过正式发布脚本执行，无人工逐条命令替换
  - 后端重建使用远端 compose 运行定义，避免手写 `docker run` 漂移
  - 若本地存在无关脏改，本脚本会改用 `HEAD clean snapshot + overlay` 构建，并把本轮 overlay 清单写入记录
- 后续动作：
  - 后续 `backend-only` 发布统一调用本脚本

## 7. 附加回读

### 7.1 nginx `/api` 反代块

```text
6:    location /api {
7-        proxy_pass http://kaipai-backend:8080;
8-        proxy_set_header Host $host;
9-        proxy_set_header X-Real-IP $remote_addr;
10-        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
11-    }
12-
```

### 7.2 公网 API Docs

```text
status=200
{"openapi":"3.0.1","info":{"title":"开拍了 API 文档","version":"v1.0.0"},"paths":"[REDACTED: docs body omitted in committed release record]"}
```

### 7.3 公网后台登录回包

```text
status=200
{"code":200,"message":"操作成功","data":{"accessToken":"[REDACTED]","adminUserInfo":{"adminUserId":2,"account":"admin","userName":"admin","phone":"[REDACTED]","email":"[REDACTED]","roleCodes":["ADMIN"],"permissions":"[REDACTED]"}}}
```

### 7.4 公网招聘角色回包

```text
status=401
{"code":401,"message":"未登录或Token已过期","data":null}
```

### 7.5 公网演员角色回包

```text
status=401
{"code":401,"message":"未登录或Token已过期","data":null}
```

### 7.6 服务端重建版本

```text
Docker Compose version v2.24.0
```

### 7.7 容器日志尾部

```text
Standard Commons Logging discovery in action with spring-jcl: please remove commons-logging.jar from classpath in order to avoid potential conflicts

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.3)

2026-05-11T01:17:01.100Z  INFO 1 --- [kaipai-backend] [           main] com.kaipai.KaipaiApplication             : The following 1 profile is active: "dev"
2026-05-11T01:17:02.232Z  INFO 1 --- [kaipai-backend] [           main] .s.d.r.c.RepositoryConfigurationDelegate : Multiple Spring Data modules found, entering strict repository configuration mode
2026-05-11T01:17:02.236Z  INFO 1 --- [kaipai-backend] [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data Redis repositories in DEFAULT mode.
2026-05-11T01:17:02.281Z  INFO 1 --- [kaipai-backend] [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 27 ms. Found 0 Redis repository interfaces.
2026-05-11T01:17:02.652Z  INFO 1 --- [kaipai-backend] [           main] o.s.cloud.context.scope.GenericScope     : BeanFactory id=daf5660f-7d4f-3e1e-990a-a6bbe31946ea
2026-05-11T01:17:03.300Z  INFO 1 --- [kaipai-backend] [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 8080 (http)
2026-05-11T01:17:03.316Z  INFO 1 --- [kaipai-backend] [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2026-05-11T01:17:03.317Z  INFO 1 --- [kaipai-backend] [           main] o.apache.catalina.core.StandardEngine    : Starting Servlet engine: [Apache Tomcat/10.1.19]
2026-05-11T01:17:03.363Z  INFO 1 --- [kaipai-backend] [           main] o.a.c.c.C.[Tomcat].[localhost].[/api]    : Initializing Spring embedded WebApplicationContext
2026-05-11T01:17:03.364Z  INFO 1 --- [kaipai-backend] [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 2236 ms
Standard Commons Logging discovery in action with spring-jcl: please remove commons-logging.jar from classpath in order to avoid potential conflicts
2026-05-11T01:17:03.447Z DEBUG 1 --- [kaipai-backend] [           main] com.kaipai.common.filter.JwtFilter       : Filter 'jwtFilter' configured for use
Logging initialized using 'class org.apache.ibatis.logging.stdout.StdOutImpl' adapter.
Initialization Sequence datacenterId:12 workerId:16
 _ _   |_  _ _|_. ___ _ |    _ 
| | |\/|_)(_| | |_\  |_)||_|_\ 
     /               |         
                        3.5.5
```
