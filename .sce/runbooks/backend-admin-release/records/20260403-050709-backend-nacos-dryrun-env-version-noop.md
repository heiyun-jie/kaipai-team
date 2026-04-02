# 后端 Nacos 配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260403-050709-backend-nacos-dryrun-env-version-noop`
- 执行时间：`2026-04-03 05:07:20 +0800`
- 操作人：`codex`
- 范围：`backend-nacos-config-sync`
- dry-run：`是`
- Nacos dataId：`kaipai-backend-dev.yml`
- content type：`yaml`

## 2. 变更项

- `wechat.miniapp.app-id`: `<missing>` -> `placeholder-appid`
- `wechat.miniapp.app-secret`: `[REDACTED]` -> `[REDACTED]`
- `wechat.miniapp.env-version`: `<missing>` -> `develop`

## 3. 目标值预览

- `wechat.miniapp.app-id` => `placeholder-appid`
- `wechat.miniapp.app-secret` => `[REDACTED]`
- `wechat.miniapp.env-version` => `develop`

## 4. 当前结论

- 当前运行时是否已生效：`否，当前仅做 dry-run 预演`
- 后续必须动作：
  - 若 compose 侧仍缺同组变量，先按 `run-backend-compose-env-sync.py` 补齐
  - 再执行标准 `backend-only` 发布
  - 发布后重新执行 `read-backend-nacos-config.py` 与 `read-backend-runtime-logs.py`

## 5. 远端回读

- 本次为 dry-run，本地仅完成候选配置预演，未写入远端 Nacos
