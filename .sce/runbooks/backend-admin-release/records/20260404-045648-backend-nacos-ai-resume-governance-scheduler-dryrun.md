# 后端 Nacos 配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260404-045648-backend-nacos-ai-resume-governance-scheduler-dryrun`
- 执行时间：`2026-04-04 04:56:58 +0800`
- 操作人：`codex`
- 范围：`backend-nacos-config-sync`
- dry-run：`是`
- publish-current：`否`
- Nacos dataId：`kaipai-backend-dev.yml`
- content type：`yaml`

## 2. 变更项

- `kaipai.ai.resume.governance-scheduler.enabled`: `<missing>` -> `true`
- `kaipai.ai.resume.governance-scheduler.initial-delay`: `<missing>` -> `2m`
- `kaipai.ai.resume.governance-scheduler.fixed-delay`: `<missing>` -> `15m`
- `kaipai.ai.resume.governance-scheduler.limit`: `<missing>` -> `20`
- `kaipai.ai.resume.governance-scheduler.lock-ttl`: `<missing>` -> `14m`
- `kaipai.ai.resume.governance-scheduler.reason`: `<missing>` -> `AI治理定时sweep`

## 3. 目标值预览

- `kaipai.ai.resume.governance-scheduler.enabled` => `true`
- `kaipai.ai.resume.governance-scheduler.initial-delay` => `2m`
- `kaipai.ai.resume.governance-scheduler.fixed-delay` => `15m`
- `kaipai.ai.resume.governance-scheduler.limit` => `20`
- `kaipai.ai.resume.governance-scheduler.lock-ttl` => `14m`
- `kaipai.ai.resume.governance-scheduler.reason` => `AI治理定时sweep`

## 4. 当前结论

- 当前运行时是否已生效：`否，当前仅做 dry-run 预演`
- 后续必须动作：
  - 若 compose 侧仍缺同组变量，先按 `run-backend-compose-env-sync.py` 补齐
  - 再执行标准 `backend-only` 发布
  - 发布后重新执行 `read-backend-nacos-config.py` 与 `read-backend-runtime-logs.py`

## 5. 远端回读

- 本次为 dry-run，本地仅完成候选配置预演，未写入远端 Nacos
