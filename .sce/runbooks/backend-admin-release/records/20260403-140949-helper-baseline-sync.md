# 发布 helper 基线同步记录

## 1. 基本信息

- 批次号：`20260403-140949-helper-baseline-sync`
- 执行时间：`2026-04-03 14:09 +0800`
- 操作人：`codex`
- 关联 Spec / Runbook：
  - `00-29 backend-admin-release-governance`
  - `backend-admin-standard-release.md`
- 执行入口：
  - `python .sce/runbooks/backend-admin-release/scripts/sync-release-helper-baseline.py --operator codex`

## 2. 本次同步范围

- 远端 admin helper：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
- 远端 backend helper：
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
- 远端 sudoers：
  - `/etc/sudoers.d/kaipai-admin-release`

## 3. 执行结果

- 通过密码登录 SSH 成功连接 `kaipaile@101.43.57.62`
- 远端临时文件上传成功
- 两个 helper 均以 `root:root 0755` 重装成功
- sudoers 以 `root:root 0440` 重装成功
- `visudo -cf /etc/sudoers.d/kaipai-admin-release` 校验通过
- 远端临时文件清理完成
- 发布 key 验证通过
- `sudo -n /usr/local/bin/kaipai-admin-release-helper.sh --healthcheck` 返回 `helper-ok`
- `sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --healthcheck` 返回 `helper-ok`

## 4. 同步后验证

- 重新执行：
  - `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label actor-search-502-post-helper-sync --container kaipai-backend --since 2h --tail 200`
  - `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label actor-search-502-post-helper-sync-nginx --container kaipai-nginx --since 2h --tail 200`
- 诊断目录已产出：
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-141009-actor-search-502-post-helper-sync/`
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-141009-actor-search-502-post-helper-sync-nginx/`
- 两份诊断目录均已包含 `docker-inspect-state.txt`

## 5. 关键回读

后端容器：

```text
status=running startedAt=2026-04-02T22:57:09.339192575Z finishedAt=0001-01-01T00:00:00Z restartCount=0 oomKilled=false error= restartPolicy=unless-stopped
```

nginx 容器：

```text
status=running startedAt=2026-03-26T10:34:48.20978264Z finishedAt=2026-03-26T10:34:47.977102291Z restartCount=0 oomKilled=false error= restartPolicy=always
```

## 6. 结论

- 远端 helper / sudoers 基线已与当前仓版本对齐。
- `docker-inspect-state.txt` 已可稳定产出。
- 后续 `502` 排障可以直接基于结构化 `RestartCount / StartedAt / OOMKilled` 证据判断容器是否真实重启。
