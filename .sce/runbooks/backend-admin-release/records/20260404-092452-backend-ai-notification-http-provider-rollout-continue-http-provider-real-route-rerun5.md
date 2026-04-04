# AI 通知 HTTP Provider 总控记录

## 1. 基本信息

- 批次号：`20260404-092452-backend-ai-notification-http-provider-rollout-continue-http-provider-real-route-rerun5`
- 执行时间：`2026-04-04 09:27:08 +0800`
- 操作人：`codex`
- 范围：`provider=http rollout`
- dry-run：`否`
- 最终状态：`validation_failed`
- 中止/结束原因：`validation_failed`

## 2. 固定执行顺序

1. `read-local-ai-notification-http-bridge-inputs.py`
2. `run-backend-ai-notification-config-sync-pipeline.py`
3. `run-backend-only-release.py`
4. `run-ai-resume-notification-foundation-validation.py`

## 3. Bridge 输入门禁

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092452-continue-http-provider-real-route-rerun5-bridge-input`
- releaseReady：`是`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL`：`http://101.43.57.62/api/internal/ai/resume/notification-receipts/provider`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`：`Authorization`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`：`http://101.43.57.62/bridge/ai-notification/`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`：`http`

## 4. AI 通知配置总控

- 记录路径：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092452-backend-ai-notification-config-pipeline-continue-http-provider-real-route-rerun5.md`
- 本地输入诊断：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092452-continue-http-provider-real-route-rerun5-local-input`
- 远端 Nacos 预检查：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260404-092452-continue-http-provider-real-route-rerun5-remote-nacos`
- Nacos 同步记录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092505-backend-nacos-continue-http-provider-real-route-rerun5.md`

## 5. backend-only

- 发布记录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260404-092531-backend-only-continue-http-provider-real-route-rerun5.md`
- 本地 jar SHA256：`ABD935AE2C5710C683F918B4DA6BFF73817672B25AA3C49A370FA98D8C4F7701`
- `/api/v3/api-docs`：`200`
- `/api/admin/auth/login`：`200`

## 6. 真实通知样本

- 验证脚本退出码：`1`
- 样本目录：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\ai-resume\samples\20260404-092705-continue-http-provider-real-route-rerun5`

## 7. 下一步

- 若样本失败，先阅读对应 sample `summary.md` 和发布记录，再决定是桥接服务问题、Nacos 漂移还是运行时数据问题
