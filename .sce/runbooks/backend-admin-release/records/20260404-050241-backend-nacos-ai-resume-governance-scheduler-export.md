# 后端 Nacos 配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260404-050241-backend-nacos-ai-resume-governance-scheduler-export`
- 执行时间：`2026-04-04 05:02:49 +0800`
- 操作人：`codex`
- 范围：`backend-nacos-config-sync`
- dry-run：`是`
- publish-current：`是`
- Nacos dataId：`kaipai-backend-dev.yml`
- content type：`yaml`

## 2. 变更项

- 无字段变更，本次为原文回写验证

## 3. 目标值预览

- 保持当前 dataId 原文不变

## 4. 当前结论

- 当前运行时是否已生效：`否，当前仅做 dry-run 预演`
- 后续必须动作：
  - 若 compose 侧仍缺同组变量，先按 `run-backend-compose-env-sync.py` 补齐
  - 再执行标准 `backend-only` 发布
  - 发布后重新执行 `read-backend-nacos-config.py` 与 `read-backend-runtime-logs.py`

## 5. 远端回读

- 本次为 dry-run，本地仅完成候选配置预演，未写入远端 Nacos
