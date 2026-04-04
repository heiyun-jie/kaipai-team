# 后端 Nacos 配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260404-072835-backend-nacos-continue-ai-notification-random-token`
- 执行时间：`2026-04-04 07:28:57 +0800`
- 操作人：`codex`
- 范围：`backend-nacos-config-sync`
- dry-run：`否`
- publish-current：`否`
- Nacos dataId：`kaipai-backend-dev.yml`
- content type：`yaml`

## 2. 变更项

- `kaipai.ai.resume.notification.enabled`: `<missing>` -> `true`
- `kaipai.ai.resume.notification.provider-code`: `<missing>` -> `manual`
- `kaipai.ai.resume.notification.callback-header`: `<missing>` -> `X-Kaipai-Ai-Notification-Token`
- `kaipai.ai.resume.notification.callback-token`: `[REDACTED]` -> `[REDACTED]`

## 3. 目标值预览

- `kaipai.ai.resume.notification.enabled` => `true`
- `kaipai.ai.resume.notification.provider-code` => `manual`
- `kaipai.ai.resume.notification.callback-header` => `X-Kaipai-Ai-Notification-Token`
- `kaipai.ai.resume.notification.callback-token` => `[REDACTED]`

## 4. 当前结论

- 当前运行时是否已生效：`否，当前仅写入 Nacos，仍需后续 backend-only 发布 / 重建并回读`
- 后续必须动作：
  - 若 compose 侧仍缺同组变量，先按 `run-backend-compose-env-sync.py` 补齐
  - 再执行标准 `backend-only` 发布
  - 发布后重新执行 `read-backend-nacos-config.py` 与 `read-backend-runtime-logs.py`

## 5. 远端回读

- 远端备份路径：`/opt/kaipai/backups/releases/20260404-072835-backend-nacos-continue-ai-notification-random-token/nacos-config`
- 远端归档目录：`/opt/kaipai/builds/20260404-072835-backend-nacos-continue-ai-notification-random-token`
- Nacos 服务：`127.0.0.1:8848`
- Nacos group：`DEFAULT_GROUP`
- Nacos namespace：``

### 5.1 发布前过滤视图

```text
[no matching lines]
```

### 5.2 发布后过滤视图

```text
[no matching lines]
```

### 5.3 发布接口返回

```text
true
```
