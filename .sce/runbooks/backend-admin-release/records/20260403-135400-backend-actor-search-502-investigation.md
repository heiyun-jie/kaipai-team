# 后端 `/api/actor/search` 502 排查记录

## 1. 基本信息

- 排查批次号：`20260403-135400-backend-actor-search-502-investigation`
- 排查时间：`2026-04-03 13:54 +0800`
- 排查对象：`http://101.43.57.62/api/actor/search?page=1&size=20`
- 排查背景：
  - 用户在浏览器侧看到 `502 Bad Gateway`
  - 怀疑服务器上遗留的上传临时脚本或发布脚本导致持续重启
- 关联 Spec / Runbook：
  - `00-29 backend-admin-release-governance`
  - `backend-admin-standard-release.md`

## 2. 证据来源

- 标准只读诊断：
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-134836-actor-search-502-check/`
- 追加代理层诊断：
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-140350-actor-search-502-nginx-check/`
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-140350-actor-search-502-backend-window/`
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-140502-actor-search-502-nginx-wide/`
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-141009-actor-search-502-post-helper-sync/`
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-141009-actor-search-502-post-helper-sync-nginx/`
- 关联正式发布记录：
  - `.sce/runbooks/backend-admin-release/records/20260403-065616-backend-only-recruit-role-search-undefined-guard.md`
- 关联 helper 基线同步记录：
  - `.sce/runbooks/backend-admin-release/records/20260403-140949-helper-baseline-sync.md`
- 追加只读检查：
  - 公网重复探测 `GET /api/actor/search?page=1&size=20`
  - 远端只读回读 `crontab`
  - 远端只读回读上传目录
  - 远端只读确认 helper 非常驻进程

## 3. 排查结果

### 3.1 当前接口并非持续性 502

- `2026-04-03 13:48 +0800` 首次复测：
  - `GET /api/actor/search?page=1&size=20` 返回 `200`
  - `GET /api/v3/api-docs` 返回 `200`
- `2026-04-03 13:52 +0800` 连续 5 次外部重复探测：
  - 全部返回 `200`
  - 响应长度稳定为 `12152`

结论：

- 该 `502` 在排查时点未持续存在，更像瞬时故障，而不是当前仍在进行中的持续崩溃。

### 3.1.1 Nginx 近 6 小时未记录该接口的 `502`

- 追加抓取 `kaipai-nginx` 近 6 小时 `tail 2000` 日志后，`/api/actor/search?page=1&size=20` 多次命中均为 `200`
- 包含以下时间点：
  - `2026-04-03 12:03:10 +0800`
  - `2026-04-03 12:38:37 +0800`
  - `2026-04-03 13:42:59 +0800`
  - `2026-04-03 13:46:13 +0800`
  - `2026-04-03 13:48:20 +0800`
  - `2026-04-03 13:52:25 ~ 13:52:34 +0800`
  - `2026-04-03 14:04:08 +0800`
- 同一份 `nginx` 日志中未发现：
  - `/api/actor/search?page=1&size=20` 的 `502`
  - `upstream timed out`
  - `connect() failed`
  - `upstream prematurely closed connection`
  - `no live upstreams`
- 该时间窗内唯一与 upstream 相关的异常只是 `/api/v3/api-docs` 大响应触发的 `buffered to a temporary file` `warn`，不属于 `502`，也不指向后端崩溃

结论：

- 至少在当前已保留的 Nginx 近 6 小时访问 / 错误输出里，`actor/search` 没有出现过服务端 `502` 证据。
- 这说明“服务器因为这个接口持续崩溃”这个判断当前证据不成立。

### 3.2 没有发现后端在排查前 7 小时内持续重启

- 标准诊断目录中的 `docker-ps.txt` 显示：
  - `kaipai-backend   kaipai-kaipai   Up 7 hours`
- helper 基线同步后重新抓取的结构化容器状态显示：
  - `status=running`
  - `startedAt=2026-04-02T22:57:09.339192575Z`
  - `restartCount=0`
  - `oomKilled=false`
  - `restartPolicy=unless-stopped`
- 关联发布记录显示：
  - `20260403-065616-backend-only-recruit-role-search-undefined-guard` 在 `2026-04-03 06:57 +0800` 重建后端容器
  - 发布后容器状态为 `Up 9 seconds`

结论：

- 截至 `2026-04-03 13:48 +0800` 的标准诊断时点，容器已经连续运行约 7 小时。
- 这与 `06:57 +0800` 的正式发布重建时间一致。
- helper 升级后的结构化回读进一步确认：`restartCount=0`，不存在“发布后容器又被反复拉起”的证据。
- 若存在“临时脚本持续重启容器”，不会呈现这种连续 `Up 7 hours` 的状态。

### 3.3 没有发现计划任务残留触发重启

- `kaipaile` 用户 crontab：空
- `root` crontab：空
- `/etc/cron.d` 与系统 crontab 目录按关键字扫描：
  - 未发现 `kaipai`
  - 未发现 `backend-release-helper`
  - 未发现 `docker compose up`
  - 未发现 `force-recreate`

结论：

- 没有证据表明服务器上存在通过 cron 持续触发后端重建的残留任务。

### 3.4 没有发现上传临时脚本常驻或反复执行

- `sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --healthcheck` 正常返回 `helper-ok`
- 进程检查未发现常驻的 `kaipai-backend-release-helper.sh`
- 上传目录检查：
  - `/home/kaipaile/backend-release-uploads/20260403-065616-backend-only-recruit-role-search-undefined-guard`
  - `/home/kaipaile/backend-release-uploads/20260403-043255-backend-only-invite-wxacode-fallback-mainline`
  - 两个目录都未发现残留文件
- 本地 helper 脚本实现也明确在发布完成后执行 `rm -f "$upload_path"`

结论：

- 当前没有证据支持“上传过程中写入的临时脚本没有删除，并且一直在重启服务”这个判断。
- 上传目录保留的是发布批次目录本身，不是持续执行的脚本进程。

### 3.5 后端日志中未见崩溃型异常证据

- 标准诊断抓取的近 2 小时后端日志以正常业务查询为主
- 关键字扫描未发现：
  - `Exception`
  - `ERROR`
  - `OutOfMemory`
  - `OOM`
  - `Killed`
  - `upstream`

结论：

- 当前已保存的后端容器日志里没有直接证明“服务崩溃后被拉起”的异常栈或 OOM 证据。

## 4. 最终结论

- 这次 `/api/actor/search` 的 `502`，在排查时点未复现为持续故障。
- 当前证据不支持“服务器一直在崩溃”。
- 当前证据也不支持“上传临时脚本残留导致持续重启”。
- 当前更接近的结论是：
  - 用户侧看到过一次瞬时 `502`
  - 但在保留下来的 Nginx 和 backend 近 6 小时证据中，没有复现出对应的服务端 `502`
  - 因此暂时不能把根因归到“后端崩溃”“容器重启”“上传临时脚本残留”这三类
- 若之后再次出现同类问题，更可能要在“同一秒级时间点的 Nginx error log / access log 与客户端截图”联合对齐后再下结论

## 5. 已补的流程改进

- 已在本地 `00-29` 诊断链路补充：
  - helper `--runtime-diagnostics` 增加容器状态摘要
  - `read-backend-runtime-logs.py` 增加 `docker-inspect-state.txt`
  - Spec 与 runbook 明确要求回读：
    - `status`
    - `StartedAt`
    - `FinishedAt`
    - `RestartCount`
    - `OOMKilled`
    - `restartPolicy`
- 已新增独立 helper 修复入口：
  - `python .sce/runbooks/backend-admin-release/scripts/sync-release-helper-baseline.py --operator <name>`
- 已在 `2026-04-03 14:09 +0800` 完成一次远端 helper / sudoers 基线同步，并复抓结构化状态证据

## 6. 后续建议

- 下一次若浏览器再次出现 `502`，应立即：
  - 先用业务入口复现一次
  - 立刻运行标准诊断脚本抓同时间窗
  - 先抓 `--container kaipai-nginx`，再抓 `--container kaipai-backend`
  - 同时保留浏览器请求时间点，便于和 nginx / backend 日志对齐
- 当前远端 helper 已同步到支持 `docker-inspect-state.txt` 的版本，后续可以直接用结构化的 `RestartCount` 证据判断是否真的发生过重启。
