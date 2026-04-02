# 后端微信配置来源同步总控记录

## 1. 基本信息

- 配置批次号：`20260403-063339-backend-wechat-config-pipeline-invite-login-wechat-sync`
- 执行时间：`2026-04-03 06:33:39 +0800`
- 操作人：`codex`
- 范围：`backend-wechat-config-sync-pipeline`
- dry-run：`是`
- 最终状态：`blocked`
- 中止/结束原因：`local_input_missing`

## 2. 固定执行顺序

1. `read-local-wechat-config-inputs.py`
2. `read-backend-wechat-config-precheck.py`
3. `run-backend-compose-env-sync.py`
4. `run-backend-nacos-config-sync.py`

## 3. 本地输入检查

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260403-063339-invite-login-wechat-sync-local-input`
- releaseReady：`否`
- project appId：`wxd38339082a9cfa4e`
- 结论：当前本地没有成组 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，总控在第 1 步中止

## 7. 下一步

- 若总控已在本地输入检查中止，先取得合法 `appSecret` 输入，再重新执行本总控脚本
- 若 compose / Nacos 已同步完成，后续仍必须执行标准 `backend-only` 发布 / 重建
- 后续重建完成后，再重新执行 `read-backend-wechat-config-precheck.py` 验证运行时门禁
