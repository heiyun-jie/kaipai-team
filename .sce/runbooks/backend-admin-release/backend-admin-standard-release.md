# 后端与管理端标准发布手册

> 对应 Spec：`00-29 backend-admin-release-governance`
> 适用范围：`kaipaile-server`、`kaipai-admin`
> 当前目标环境事实基线：
> - 远端主机：`101.43.57.62`
> - 后端运行目录：`/opt/kaipai`
> - 后端运行 jar：`/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
> - 后端容器：`kaipai-backend`
> - 后端镜像：`kaipai-kaipai:latest`
> - 后端运行环境：`NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`、`SERVER_PORT=8080`
> - nginx 配置目录：`/opt/kaipai/nginx/conf`
> - nginx 静态目录：`/opt/kaipai/nginx/html`
> - nginx `/api` 反代目标：`http://kaipai-backend:8080`
> - 管理端本地构建目录：`D:\XM\kaipai-team\kaipai-admin\dist`
> - 远端系统：`Ubuntu 22.04 LTS`
> - 远端包管理器：`apt-get`
> - 远端 Node.js：`v22.22.2`
> - 远端 npm：`10.9.7`

## 1. 硬规则

1. 每次发布都必须先填写发布批次号，推荐格式：`YYYYMMDD-HHMM-<scope>-<label>`。
2. 每次发布都必须先确定范围：`backend-only`、`admin-only`、`backend+admin`。
3. 每次发布都必须先备份，再替换。
4. 每次发布都必须留下产物 SHA、备份路径和 smoke 结果。
5. 若任何关键检查失败，立即中止；若关键 smoke 失败，进入回滚判断。
6. 若执行中发现当前 runbook 与实际可执行链路不一致，必须先暂停发布并更新 Spec + runbook，再继续发布。
7. 标准 `backend-only` 发布必须通过脚本 `scripts/run-backend-only-release.py` 执行；手工逐条命令只允许作为脚本故障时的应急兜底，并且必须先修正文档或脚本。
8. 标准 `admin-only` 发布必须通过脚本 `scripts/run-admin-only-release.py` 执行；手工逐条命令只允许作为脚本故障时的应急兜底，并且必须先修正文档或脚本。
9. 标准 `backend-only` 发布默认使用 `OpenSSH key auth + scp/ssh + 远端 sudo helper`；标准 `admin-only` 发布默认使用 `OpenSSH key auth + git push/ssh + 远端 sudo helper`；`password + Paramiko` 只允许用于一次性引导或修复，不再作为正式发布链路。
10. 当前标准 `admin-only` 发布已切换为“本地生成 git snapshot 仓库，push 到远端 bare repo，由服务器按 release ref 检出执行 `npm ci && npm run build`，再由 helper 完成静态替换”。
11. 当前标准 `backend-only` 发布已切换为“本地 JDK 17 构建 jar，上传到远端临时目录，再由 helper 统一完成备份、compose 重建、运行时回读与 smoke”。

## 1.1 环境基线变更

当前已允许的环境基线增强动作：

1. 在远端 `Ubuntu 22.04` 上通过系统包源安装 `node/npm`
2. 安装完成后必须记录版本
3. 当前已完成版本基线：`Node.js v22.22.2`、`npm 10.9.7`
4. 当前标准主链路已完成切换：`git snapshot -> bare repo -> 服务端检出构建 -> helper 发布`
5. `tar.gz` 仍保留为 helper 产物归档与故障回退链路，不再作为默认正式上传入口

本节目的：

- 给后续服务端构建能力预留基础
- 避免把“装了工具”误判成“已经切换发布方案”

## 2. 发布前通用检查

每次发布都先完成以下检查：

1. 确认本次变更对应的 Spec / 需求 / 样本记录。
2. 确认本次范围是否需要联合发布。
3. 确认目标环境还是当前这套：
   - `/api` 仍由 nginx 反代到 `kaipai-backend:8080`
   - 后端仍走 `NACOS_ENABLED=true + SPRING_PROFILES_ACTIVE=dev`
   - 管理端静态目录仍是 `/opt/kaipai/nginx/html`
4. 创建本次发布记录文件：
   - `.sce/runbooks/backend-admin-release/records/<release-id>.md`
5. 在记录文件里先写清：
   - 发布批次号
   - 发布范围
   - 操作人
   - 关联 Spec / 需求

## 3. backend-only 发布

### 3.0 标准入口

首次引导入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>
```

引导脚本职责：

- 生成或复用本地专用发布 key
- 把公钥安装到远端 `~/.ssh/authorized_keys`
- 安装远端 helper：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
- 安装最小 sudo 授权：`/etc/sudoers.d/kaipai-admin-release`
- 初始化远端 bare repo：`/home/kaipaile/kaipai-admin-release.git`
- 验证正式发布所需的 `ssh/scp`、`git push` 与 `sudo -n helper` 全部可用

标准 `backend-only` 发布入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>
```

脚本职责：

- 自动选择可用的本地 `JDK 17`
- 自动执行 `mvn -q -DskipTests clean package`
- 自动计算本地 jar SHA256
- 自动通过原生 `scp` 上传 jar 到远端临时目录
- 自动通过原生 `ssh` 调用远端 helper 完成备份、替换、`docker compose build/up`、运行时回读和 smoke
- 自动生成发布记录到 `records/`

以下 `3.1` 到 `3.5` 是脚本必须遵循的标准链路，也是脚本异常时才允许人工接管的兜底步骤。

禁止事项：

- 不允许继续手写 `docker build && docker rm && docker run` 作为标准正式发布链路
- 不允许在本地仍运行 JDK 8 的情况下继续宣告后端构建已准备就绪
- 若远端 helper、sudoers 或 compose 入口不可用，先执行引导或修复脚本，再继续当前批次

### 3.1 本地构建

在 `D:\XM\kaipai-team\kaipaile-server` 执行：

```powershell
mvn -q -DskipTests clean package
Get-FileHash .\target\kaipai-backend-1.0.0-SNAPSHOT.jar -Algorithm SHA256
```

要求：

- 构建成功
- 构建使用 `JDK 17`
- 记录本地 jar SHA256

### 3.2 远端备份

备份建议目录：

- `/opt/kaipai/backups/releases/<release-id>/backend/`

至少备份：

- 当前运行 jar
- `Dockerfile`
- `docker-compose.yml`
- `docker inspect kaipai-backend`
- `docker ps` 摘要
- `docker logs --tail 200 kaipai-backend`

### 3.3 上传与替换

将本地 jar 先上传到：

- `/home/kaipaile/backend-release-uploads/<release-id>/kaipai-backend-1.0.0-SNAPSHOT.jar`

然后在远端执行：

1. helper 比对上传后 SHA256
2. helper 将该 jar 归档到 `/opt/kaipai/builds/<release-id>/kaipai-backend-1.0.0-SNAPSHOT.jar`
3. helper 将该 jar 覆盖到 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`

### 3.4 容器重建

在远端 `/opt/kaipai` 执行 compose 重建：

```bash
docker compose build kaipai
docker compose up -d --force-recreate kaipai
```

注意：

- 不允许只重启容器而不重新确认 compose 定义和环境变量
- 若当前线上残留同名旧容器但未受 compose 接管，helper 必须先清理旧容器，再执行 `compose up`
- 不允许漏核对 `nginx /api -> kaipai-backend:8080`

### 3.5 发布后检查

至少执行：

```bash
docker compose ps
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker inspect kaipai-backend
docker exec kaipai-backend sh -lc 'sha256sum /app/app.jar'
curl http://127.0.0.1:8080/api/v3/api-docs
curl -X POST http://127.0.0.1:8080/api/admin/auth/login -H 'Content-Type: application/json' -d '{"account":"admin","password":"admin123"}'
curl "http://127.0.0.1:8080/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword="
curl "http://127.0.0.1:8080/api/role/search?page=1&size=1&keyword=&gender="
```

当前标准脚本会把上面 4 条后端 smoke 一并固化；若本次变更还涉及其他业务域，再追加对应 smoke。
其中基础入口探活必须使用“带超时的就绪轮询”，不能再用固定 8 秒等待替代。

记录要求：

- compose 版本与 compose ps
- 容器状态
- 运行时环境变量
- 容器内 `/app/app.jar` SHA256
- 基础入口结果
- 业务 smoke 结果

### 3.6 发布后异常排查

若 `backend-only` 发布完成后，真实环境仍出现 `400/500`、联调脚本卡在单个接口、或本地因 Nacos / DB / Redis 环境差异无法等价复现，必须先走标准只读诊断入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since 15m
```

脚本职责：

- 复用标准发布的 `OpenSSH key auth`
- 先验证远端 helper / sudoers 基线
- 只读回读 `docker ps`、容器环境变量、`docker logs`
- 将诊断结果落到 `.sce/runbooks/backend-admin-release/records/diagnostics/<capture-id>/`

使用要求：

1. 先用业务 Spec 脚本复现一次真实问题
2. 再立即执行诊断脚本读取同一时间窗内日志
3. 若诊断产物显示是代码问题，再进入修复与重新发布
4. 若诊断产物显示是运行时基线漂移，先更新 00-29 Spec / runbook，再继续处理

## 4. admin-only 发布

### 4.0 标准入口

首次引导入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>
```

引导脚本职责：

- 生成或复用本地专用发布 key
- 把公钥安装到远端 `~/.ssh/authorized_keys`
- 安装远端 helper：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
- 安装最小 sudo 授权：`/etc/sudoers.d/kaipai-admin-release`
- 初始化远端 bare repo：`/home/kaipaile/kaipai-admin-release.git`
- 验证正式发布所需的 `ssh/scp`、`git push` 与 `sudo -n helper` 全部可用

标准 `admin-only` 发布入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label <label> --operator <name>
```

脚本职责：

- 自动生成 `kaipai-admin` 临时 git snapshot 仓库
- 自动将 release ref push 到远端 bare repo
- 自动通过原生 `ssh` 调用远端 helper 在服务器按 release ref 完成 `npm ci && npm run build`
- 自动由 helper 完成备份、替换与回读
- 自动执行公网与内网 smoke
- 自动生成发布记录到 `records/`

以下 `4.1` 到 `4.4` 是脚本必须遵循的标准链路，也是脚本异常时才允许人工接管的兜底步骤。

禁止事项：

- 不允许继续把 `password + Paramiko sftp/exec_command` 当作标准正式发布链路
- 若正式发布发现 key auth、helper 或 sudoers 不可用，先执行引导或修复脚本，再继续当前批次

### 4.1 本地快照

在临时目录 `D:\XM\kaipai-team\tmp\admin-git-snapshot-<release-id>` 生成 git snapshot：

```powershell
git init --initial-branch=release
git config user.name "Codex Release"
git config user.email "codex-release@local"
git config core.autocrlf false
git add .
git commit -m "release <release-id>"
git remote add origin "ssh://kaipaile@101.43.57.62/home/kaipaile/kaipai-admin-release.git"
$env:GIT_SSH_COMMAND='"C:\Windows\System32\OpenSSH\ssh.exe" -i "C:\Users\33340\.ssh\kaipai_release_ed25519" -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new'
git push --force origin HEAD:refs/heads/release/<release-id>
```

要求：

- 临时发布仓库来自 `kaipai-admin/` 当前工作区快照，不直接污染当前主仓
- 记录 release branch 与 commit
- push 成功后，远端 bare repo 可见对应 release ref

禁止事项：

- 不允许直接把 Windows 生成的 `zip` 包交给 Linux `unzip` 作为标准发布链路
- 若发现当前上传格式会在远端产生路径或文件名异常，必须先更新 runbook，再继续当前批次发布

### 4.2 远端备份

备份建议目录：

- `/opt/kaipai/backups/releases/<release-id>/admin-html/`

发布前先备份：

- `/opt/kaipai/nginx/html`
- `/opt/kaipai/nginx/conf/default.conf`
- 远端 helper 与 sudoers 基线：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
  - `/etc/sudoers.d/kaipai-admin-release`

### 4.3 push 与替换

本地 release ref 先 push 到远端 bare repo：

- `/home/kaipaile/kaipai-admin-release.git`

然后执行：

1. helper 创建 `/opt/kaipai/builds/<release-id>/`、备份目录和源码工作目录
2. helper 备份当前 `/opt/kaipai/nginx/html` 与 `default.conf`
3. helper 从 bare repo 检出 `release/<release-id>` 到 `/opt/kaipai/repos/kaipai-admin-releases/<release-id>/src`
4. helper 在服务器执行 `npm ci && npm run build`
5. helper 将服务端生成的 `dist/` 归档到 `/opt/kaipai/builds/<release-id>/admin-dist.tar.gz`
6. helper 清理当前 `/opt/kaipai/nginx/html` 内容
7. helper 将本次 `dist/` 内容同步到 `/opt/kaipai/nginx/html`
8. helper 回读 `index.html`

标准远端调用：

```bash
git push origin HEAD:refs/heads/release/<release-id>
ssh -i ~/.ssh/kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-admin-release-helper.sh --release-id <release-id> --git-branch release/<release-id> --git-commit <commit> --operator-user kaipaile"
```

### 4.4 发布后检查

至少执行：

```bash
ls -la /opt/kaipai/nginx/html
curl http://127.0.0.1/
curl http://127.0.0.1/api/v3/api-docs
```

然后补一条后台页面人工验证：

- 登录页可打开
- 至少一个本次改动页面可进入

记录要求：

- 远端静态目录回读
- release branch / commit
- 远端 bare repo 与远端检出 commit
- 服务端 `node/npm` 版本
- 服务端构建日志尾部
- helper 检出路径与 dist 落地路径
- 首页访问结果
- `/api` 反代结果
- 实际静态入口资源访问结果
- 人工页面验证结果

## 5. backend+admin 联合发布

默认顺序：

1. 先走 `backend-only`
2. 后端 smoke 通过后，再走 `admin-only`
3. 最后补一轮串联 smoke

串联 smoke 至少包含：

1. 管理端首页可打开
2. 管理端至少一个改动页面可进入
3. 该页面依赖的 `/api` 接口返回成功

## 6. 回滚

### 6.1 后端回滚

使用发布前备份的 jar 恢复：

1. 将备份 jar 覆盖回 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
2. 按当前同样的 compose 命令重新 `build/up -d --force-recreate`
3. 再做一轮后端 smoke

### 6.2 管理端回滚

使用发布前备份的静态目录恢复：

1. 将备份目录恢复到 `/opt/kaipai/nginx/html`
2. 再访问 `/` 与一个后台关键页
3. 确认 `/api` 仍通

## 7. 中止条件

遇到以下任一情况，必须中止当前发布：

1. 本地产物构建失败
2. 产物 SHA、git 检出 commit 或目录回读异常
3. 运行时集合与预期不一致
4. 后端容器无法稳定启动
5. 管理端首页不可访问
6. `/api` 反代失败

## 8. 发布完成定义

只有以下条件同时满足，才能写“发布完成”：

1. 备份完成
2. 新产物落地完成
3. 运行时集合回读完成
4. smoke 通过
5. 发布记录已补齐

## 9. 记录要求

每次发布完成后，必须把结果回填到：

- `.sce/runbooks/backend-admin-release/records/<release-id>.md`

记录模板：

- `backend-admin-release-evidence-template.md`
