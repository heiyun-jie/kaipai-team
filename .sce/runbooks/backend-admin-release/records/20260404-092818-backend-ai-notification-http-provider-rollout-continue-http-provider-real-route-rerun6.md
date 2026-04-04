# AI 通知 HTTP Provider 总控记录

## 1. 基本信息

- 批次号：`20260404-092818-backend-ai-notification-http-provider-rollout-continue-http-provider-real-route-rerun6`
- 执行时间：`2026-04-04 09:30:19 +0800`
- 操作人：`codex`
- 范围：`provider=http rollout`
- dry-run：`否`
- 最终状态：`completed`
- 中止/结束原因：`pipeline_finished`

## 2. 固定执行顺序

1. `read-local-ai-notification-http-bridge-inputs.py`
2. `run-backend-ai-notification-config-sync-pipeline.py`
3. `run-backend-only-release.py`
4. `run-ai-resume-notification-foundation-validation.py`

## 3. Bridge 输入门禁

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092818-continue-http-provider-real-route-rerun6-bridge-input`
- releaseReady：`是`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL`：`http://101.43.57.62/api/internal/ai/resume/notification-receipts/provider`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`：`Authorization`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`：`http://101.43.57.62/bridge/ai-notification/`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`：`http`

## 4. AI 通知配置总控

- 记录路径：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092818-backend-ai-notification-config-pipeline-continue-http-provider-real-route-rerun6.md`
- 本地输入诊断：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092818-continue-http-provider-real-route-rerun6-local-input`
- 远端 Nacos 预检查：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092818-continue-http-provider-real-route-rerun6-remote-nacos`
- Nacos 同步记录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092826-backend-nacos-continue-http-provider-real-route-rerun6.md`

## 5. backend-only

- 发布记录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092842-backend-only-continue-http-provider-real-route-rerun6.md`
- 本地 jar SHA256：`620BD98425BA1932F7BA05B75DF232C0E805736C31DAE83EB86640A5EB4879C1`
- `/api/v3/api-docs`：`200`
- `/api/admin/auth/login`：`200`

## 6. 真实通知样本

- 验证脚本退出码：`0`
- 样本目录：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\ai-resume\samples\20260404-093013-continue-http-provider-real-route-rerun6`

## 7. 下一步

- 当前已完成 `provider=http` 的标准总控与真实样本验证；后续只需补真实 vendor/bridge 变更时复用同一路径
