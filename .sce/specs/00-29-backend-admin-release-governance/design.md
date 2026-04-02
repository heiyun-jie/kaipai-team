# 后端与管理端标准发布治理 - 技术设计

_Requirements: 00-29 全部_

## 1. 设计目标

00-29 解决的不是某次具体发版，而是：

1. 让发布动作有统一入口
2. 让规则和执行手册分层存储
3. 让后端与管理端的发布可追溯、可回滚、可复盘

## 2. 文档分层

```text
00-29 Spec
  -> 发布规则
  -> 发布角色 / 阶段 / 门禁
  -> 证据要求

.sce/runbooks/backend-admin-release/
  -> 标准发布手册
  -> 发布证据模板
  -> 每次发布记录
```

### 2.1 Spec 职责

- 定义必须遵循的发布规则
- 定义发布阶段、门禁和回滚触发条件
- 定义产物、证据和记录的最小集合

### 2.2 运维文档职责

- 给出可直接执行的步骤
- 使用当前环境真实路径、真实命令和真实验证方式
- 给出记录模板，要求每次发布后落档
- 区分“一次性引导层”和“每次正式发布层”

## 3. 发布对象模型

### 3.1 后端发布对象

当前仓内与目标环境已确认事实：

- 本地工程：`kaipaile-server/`
- 构建产物：`target/kaipai-backend-1.0.0-SNAPSHOT.jar`
- 远端运行目录：`/opt/kaipai`
- 远端运行 jar：`/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
- 远端容器名：`kaipai-backend`
- 远端镜像名：`kaipai-kaipai:latest`
- 容器启动参数关键项：
  - `NACOS_ENABLED=true`
  - `SPRING_PROFILES_ACTIVE=dev`
  - `SERVER_PORT=8080`
- nginx `/api` 当前反代：`http://kaipai-backend:8080`

### 3.2 管理端发布对象

当前仓内与目标环境已确认事实：

- 本地工程：`kaipai-admin/`
- 本地发布对象：`kaipai-admin/` 当前工作区快照
- 当前已补齐 `Node.js v22.22.2` 与 `npm 10.9.7`，且已落地“git snapshot -> bare repo -> 服务端检出构建 -> helper 发布”的正式主链路
- 管理端运行时 API 基线：`VITE_API_BASE_URL=/api`
- 远端 nginx 静态目录：`/opt/kaipai/nginx/html`
- 远端 nginx 配置目录：`/opt/kaipai/nginx/conf`
- 当前静态 root：`/usr/share/nginx/html`
- 当前静态访问规则：`try_files $uri $uri/ /index.html`
- 远端服务器当前为 `Ubuntu 22.04 LTS`，`apt-get` 可用；当前已安装 `Node.js v22.22.2` 与 `npm 10.9.7`，并已在标准脚本与 helper 中完成服务端构建闭环

## 4. 发布阶段模型

### Phase A: 发布申请与范围确认

输入：

- 本次变更说明
- 发布范围：`backend-only` / `admin-only` / `backend+admin`
- 关联 Spec / issue / 样本或验收记录

输出：

- 唯一发布批次号
- 需要执行的 runbook 分支

### Phase B: 发布前检查

必须检查：

- 本地产物可构建
- 目标环境明确
- 运行时集合核对完成
- 备份路径可用
- 回滚路径明确

### Phase C: 产物构建与备份

后端：

- 构建 jar
- 记录 SHA256
- 通过标准脚本上传 jar 到远端暂存目录
- 由远端 helper 备份当前 jar、compose 定义、容器 inspect 和关键日志
- 由远端 helper 使用当前 `docker compose` 运行定义完成重建与回读

管理端：

- 本地从 `kaipai-admin/` 生成临时 git snapshot 仓库
- 正式发布前先通过引导脚本完成 key auth、helper、sudoers 与 bare repo 基线安装
- 通过原生 `git push` 将 release ref 推送到远端 bare repo（当前基线：`/home/kaipaile/kaipai-admin-release.git`）
- 通过原生 `ssh` 调用远端 helper 在服务器按 release ref 检出并执行 `npm ci && npm run build`
- helper 将源码正式检出到 `/opt/kaipai/repos/kaipai-admin-releases/<release-id>/src`
- helper 将服务端构建出的 `dist/` 归档到 `/opt/kaipai/builds/<release-id>/admin-dist.tar.gz`
- helper 完成备份、替换与回读
- 标准入口由脚本 `run-admin-only-release.py` 统一编排，不再允许靠人工逐条执行替代

### Phase D: 发布执行

默认顺序：

1. `backend-only`：后端部署 -> 后端 smoke
2. `admin-only`：管理端静态替换 -> nginx / 页面 smoke
3. `backend+admin`：后端部署 -> 后端 smoke -> 管理端替换 -> 串联 smoke

#### 后端当前推荐链路

1. 一次性执行 `bootstrap-admin-release.py`
2. 若仅补运行时来源，先执行 `run-backend-compose-env-sync.py`
3. 每次正式发布执行 `run-backend-only-release.py`
4. 正式发布使用本地 `JDK 17 + Maven` 产出 jar
5. 正式发布使用 `scp/ssh` 上传和触发远端 helper
6. 远端 helper 统一执行备份、`docker compose build/up`、运行时回读和 smoke

#### 管理端当前推荐链路

1. 一次性执行 `bootstrap-admin-release.py`
2. 每次正式发布执行 `run-admin-only-release.py`
3. 正式发布使用 `git push/ssh`，不再使用 Paramiko 作为主链路
4. 当前正式发布已切换为“git snapshot push + 服务端检出构建”
5. 这条链路不依赖当前主仓存在可用 remote，也不要求当前主仓先提交所有改动

### Phase E: 发布后验证与归档

必须输出：

- 产物 SHA 回读
- 运行时集合回读
- smoke 结果
- 失败 / 回滚情况
- 发布记录归档

## 5. 运行时集合检查设计

### 5.1 后端集合

后端每次发布前后，都必须成组核对：

- 容器名 / 镜像名
- `docker compose` 运行定义
- compose / env source 变更记录
- `NACOS_ENABLED`
- `SPRING_PROFILES_ACTIVE`
- 容器端口映射
- Docker network
- `/api` 反代目标
- 实际连接的数据库 / Redis 所在环境

### 5.2 管理端集合

管理端每次发布前后，都必须成组核对：

- `dist/` 是否来自本次构建
- 上传归档格式是否符合当前 runbook
- 本地 OpenSSH key 是否存在且可用
- 远端 helper、sudoers 与 bare repo 是否可用
- 远端 `node/npm` 版本是否符合当前基线
- 本地 release ref 是否已成功 push
- 远端源码工作目录是否来自本次 release ref 检出
- 远端静态目录是否完成备份和替换
- nginx `location /` 与 `location /api` 未被误改
- 管理端首页是否可打开
- 管理端 API 仍走 `/api`

## 6. smoke 设计

### 6.1 后端最小 smoke

最小必做：

- `docker compose ps` / `docker ps` / `docker inspect`
- 容器内 `/app/app.jar` SHA256
- `GET /api/v3/api-docs`
- 至少一个本次变更业务域接口；当前标准脚本默认附带 `admin auth`、`admin recruit roles`、`role search` 三条后端业务 smoke

### 6.1.1 后端标准诊断入口

当后端已完成发布，但真实环境仍出现 `400/500`、业务异常或“本地环境无法等价复现”时，不允许直接退回人工零散 `ssh` 排障；必须先走 runbook 固化的只读诊断入口。

当前标准入口为：

- `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since <window>`

该入口职责：

- 复用标准发布所要求的 `OpenSSH key auth`
- 先验证远端 helper / sudoers 基线仍可用
- 以只读方式回读 `docker ps`、容器环境变量和 `docker logs`
- 以只读方式回读远端 `/opt/kaipai/docker-compose.yml` 的后端服务来源摘录
- 以只读方式回读 `docker compose config` 渲染后的后端服务定义摘录
- 将诊断产物固定落到 `.sce/runbooks/backend-admin-release/records/diagnostics/<capture-id>/`

该入口不替代业务 Spec 的联调脚本；它只负责为业务 Spec 提供可信的运行时事实。

### 6.1.2 后端 compose 来源同步入口

当问题已经确认不在代码，而在后端 compose / env source 缺失变量时，必须先走脚本化的来源同步入口，而不是直接手改远端 `docker-compose.yml`。

当前标准入口为：

- `python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label <label> --from-local-env <KEY>`

该入口职责：

- 复用标准发布所要求的 `OpenSSH key auth`
- 回读远端当前 compose 文件
- 只修改 `services.kaipai.environment` 的目标变量
- 由远端 helper 先备份现有 compose，再执行 `docker compose config` 校验候选文件
- 将来源摘录、渲染结果和当前容器 env 固化到独立记录

该入口不替代正式 `backend-only` 发布；它只负责把运行时变量来源变更标准化、证据化。

### 6.2 管理端最小 smoke

最小必做：

- `curl http://<host>/` 或等效首页访问
- 远端 `index.html` 存在且替换完成
- `index.html` 引用的实际 `assets/*.js` 入口返回成功
- `/api/v3/api-docs` 或至少一个后台依赖接口可通
- 至少一个本次变更后台页面人工进入验证
- 服务端构建日志尾部可回读

### 6.3 联合 smoke

若同批包含 `backend+admin`，必须再补一轮：

- 后台登录页 / 首页可打开
- 后台变更页面至少访问一次
- 页面依赖的后端接口返回成功

## 7. 回滚设计

### 7.1 后端回滚

- 使用发布前备份的 jar 恢复远端运行 jar
- 重新执行镜像构建 / 容器重建
- 回读容器内 jar SHA 和运行时集合

### 7.2 管理端回滚

- 使用发布前备份的静态目录恢复 `/opt/kaipai/nginx/html`
- 如有必要 reload nginx
- 重新访问首页和后台关键页

### 7.3 回滚门禁

满足以下任一条，默认进入回滚判断：

- 后端容器无法稳定启动
- `/api` 基础入口失败
- 管理端首页不可打开
- `/api` 反代断开
- 关键业务页不可用

## 8. 记录设计

每次发布都必须生成记录，建议统一保存在：

- `.sce/runbooks/backend-admin-release/records/`

记录字段最小集合：

- 发布批次号
- 发布时间
- 发布范围
- 操作人
- 关联 Spec / 需求
- 后端 jar SHA
- 管理端构建批次 / 目录
- 备份路径
- 执行命令摘要
- smoke 结果
- 是否回滚
- 最终结论

## 9. 使用方式

以后每次发版不再从“记得上次怎么发”开始，而是先回答：

1. 本次发布范围是什么？
2. 对应 runbook 的哪一段？
3. 运行时集合是否核对完？
4. 备份路径和回滚路径是什么？
5. smoke 和发布记录是否已补齐？

只要这 5 个问题有一个答不出来，就不允许宣告发布完成。

补充约束：

- 若执行中发现上传格式、解包方式或替换步骤与 runbook 不一致，必须先回写 00-29 与 runbook，再继续同批次发布。
