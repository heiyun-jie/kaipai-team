# 后端运行时配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260509-225142-backend-env-ai-profile-card-kplyyk-auth`
- 执行时间：`2026-05-09 22:51:59 +0800`
- 操作人：`codex`
- 范围：`backend-compose-env-sync`
- dry-run：`否`
- 关联 Spec：
  - `00-29 backend-admin-release-governance`
  - `00-28 invite wxacode execution card`

## 2. 目标

- 将后端 compose / env source 的运行时变量变更收口到标准脚本
- 本次仅同步 `docker-compose.yml` 的后端环境变量来源，不执行后端发版与容器重建

## 3. 变更项

- `AI_PROFILE_CARD_PROVIDER_CODE`: `<missing>` -> `kplyyk`
- `AI_PROFILE_CARD_KPLYYK_AUTH_TOKEN`: `[REDACTED]` -> `[REDACTED]`

## 4. 目标值预览

- `AI_PROFILE_CARD_PROVIDER_CODE` => `kplyyk`
- `AI_PROFILE_CARD_KPLYYK_AUTH_TOKEN` => `[REDACTED]`

## 5. 当前结论

- 当前容器运行时是否已生效：`否，已更新 compose 来源，仍需后续 backend-only 发布/重建`
- 后续必须动作：
  - 通过标准 `backend-only` 脚本重建后端容器
  - 再通过标准诊断确认 compose 来源摘录与容器 env 都包含目标变量

## 6. 远端回读

- 远端备份路径：`/opt/kaipai/backups/releases/20260509-225142-backend-env-ai-profile-card-kplyyk-auth/backend-env`
- 远端构建归档目录：`/opt/kaipai/builds/20260509-225142-backend-env-ai-profile-card-kplyyk-auth`
- 运行时 compose 文件：`/opt/kaipai/docker-compose.yml`
- 归档 compose 文件：`/opt/kaipai/builds/20260509-225142-backend-env-ai-profile-card-kplyyk-auth/docker-compose.yml`

### 6.1 当前容器环境变量

```text
SERVER_PORT=8080
SPRING_DATASOURCE_USERNAME=root
SPRING_DATA_REDIS_PASSWORD=<redacted>
SPRING_PROFILES_ACTIVE=dev
SPRING_DATA_REDIS_PORT=6379
SPRING_DATASOURCE_PASSWORD=<redacted>
SPRING_DATA_REDIS_HOST=redis
SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/kaipai_dev?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false&connectTimeout=3000&socketTimeout=3000
NACOS_ENABLED=false
PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
JAVA_HOME=/opt/java/openjdk
LANG=en_US.UTF-8
LANGUAGE=en_US:en
LC_ALL=en_US.UTF-8
JAVA_VERSION=jdk-17.0.18+8
```

### 6.2 compose 后端来源摘录

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

### 6.3 compose 渲染后后端定义摘录

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

### 6.4 compose 候选文件校验输出

```text
name: kaipai
services:
  kaipai:
    build:
      context: /opt/kaipai
      dockerfile: Dockerfile
    container_name: kaipai-backend
    depends_on:
      mysql:
        condition: service_started
        required: true
      redis:
        condition: service_started
        required: true
    environment:
      AI_PROFILE_CARD_KPLYYK_AUTH_TOKEN: "<redacted>"
      AI_PROFILE_CARD_PROVIDER_CODE: kplyyk
      NACOS_ENABLED: "false"
      SERVER_PORT: "8080"
      SPRING_DATA_REDIS_HOST: redis
      SPRING_DATA_REDIS_PASSWORD: "<redacted>"
      SPRING_DATASOURCE_PASSWORD: "<redacted>"
        protocol: tcp
    restart: unless-stopped
    volumes:
      - type: bind
        source: /opt/kaipai/logs
        target: /app/logs
        bind:
          create_host_path: true
  mysql:
    container_name: kaipai-mysql
    environment:
      MYSQL_DATABASE: kaipai
      MYSQL_ROOT_PASSWORD: "<redacted>"
        protocol: tcp
    restart: always
    volumes:
      - type: bind
        source: /opt/kaipai/mysql-data
        target: /var/lib/mysql
        bind:
          create_host_path: true
  nginx:
    container_name: kaipai-nginx
    image: nginx:latest
    networks:
      default: null
    ports:
      - mode: ingress
        target: 80
        published: "80"
        protocol: tcp
    restart: always
    volumes:
      - type: bind
        source: /opt/kaipai/nginx/conf
        target: /etc/nginx/conf.d
        bind:
          create_host_path: true
      - type: bind
        source: /opt/kaipai/nginx/html
        target: /usr/share/nginx/html
        bind:
          create_host_path: true
  redis:
    command:
      - redis-server
      - --requirepass
      - <redacted>
    container_name: kaipai-redis
    image: redis:7
    networks:
      default: null
    ports:
      - mode: ingress
        target: 6379
        published: "6379"
        protocol: tcp
    restart: always
    volumes:
      - type: bind
        source: /opt/kaipai/redis-data
        target: /data
        bind:
          create_host_path: true
networks:
  default:
    name: kaipai_default
```
