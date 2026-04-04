# 后端 AI 通知配置来源同步总控记录

## 1. 基本信息

- 配置批次号：`20260404-091059-backend-ai-notification-config-pipeline-continue-http-provider-real-route-rerun`
- 执行时间：`2026-04-04 09:11:30 +0800`
- 操作人：`codex`
- 范围：`backend-ai-notification-config-sync-pipeline`
- dry-run：`否`
- 最终状态：`completed`
- 中止/结束原因：`pipeline_finished`

## 2. 固定执行顺序

1. `read-local-ai-notification-config-inputs.py`
2. `read-backend-nacos-config.py`
3. `run-backend-nacos-config-sync.py`

## 3. 本地输入检查

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-091100-continue-http-provider-real-route-rerun-local-input`
- releaseReady：`是`
- `AI_RESUME_NOTIFICATION_ENABLED`：`passed`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`：`passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER`：`passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`：`passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL`：`passed`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`：`passed`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`：`passed`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`：`passed`

## 4. 远端 Nacos 预检查

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-091100-continue-http-provider-real-route-rerun-remote-nacos`
- 目的：同步前固定目标 dataId 当前原文与目标键存在性，不再手工进控制台比对
- 预检查摘要：
  kaipai-backend-dev.yml: no AI notification keys matched current grep
- 过滤回读：`[no matching lines]`

## 5. Nacos 配置同步

- 记录路径：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-091110-backend-nacos-continue-http-provider-real-route-rerun.md`
- dry-run：`否`

## 6. 下一步

- 若当前仍是 `local_input_not_ready`，先修正本地 secret 文件，再重新执行本总控
- Nacos 同步完成后，仍必须执行标准 `backend-only` 发布 / 重建
- 重建后再执行 `run-ai-resume-notification-foundation-validation.py`，产出真实 dispatch / callback 样本
