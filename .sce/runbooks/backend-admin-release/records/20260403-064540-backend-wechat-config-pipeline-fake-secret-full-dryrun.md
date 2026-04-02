# 后端微信配置来源同步总控记录

## 1. 基本信息

- 配置批次号：`20260403-064540-backend-wechat-config-pipeline-fake-secret-full-dryrun`
- 执行时间：`2026-04-03 06:46:09 +0800`
- 操作人：`codex`
- 范围：`backend-wechat-config-sync-pipeline`
- dry-run：`是`
- 最终状态：`completed`
- 中止/结束原因：`pipeline_finished`

## 2. 固定执行顺序

1. `read-local-wechat-config-inputs.py`
2. `read-backend-wechat-config-precheck.py`
3. `run-backend-compose-env-sync.py`
4. `run-backend-nacos-config-sync.py`

## 3. 本地输入检查

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260403-064541-fake-secret-full-dryrun-local-input`
- releaseReady：`是`
- project appId：`wxd38339082a9cfa4e`

## 4. 远端门禁预检查

- 诊断目录：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\diagnostics\20260403-064541-fake-secret-full-dryrun-remote-gate`
- gate status：`blocked`
- failing checks：`compose_source, compose_rendered, container_env, nacos:kaipai-backend, nacos:kaipai-backend.yml, nacos:kaipai-backend-dev.yml`

## 5. Compose 来源同步

- 记录路径：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260403-064551-backend-env-fake-secret-full-dryrun.md`
- dry-run：`是`

## 6. Nacos 配置同步

- 记录路径：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260403-064601-backend-nacos-fake-secret-full-dryrun.md`
- dry-run：`是`

## 7. 下一步

- 若总控已在本地输入检查中止，先取得合法 `appSecret` 输入，再重新执行本总控脚本
- 若 compose / Nacos 已同步完成，后续仍必须执行标准 `backend-only` 发布 / 重建
- 后续重建完成后，再重新执行 `read-backend-wechat-config-precheck.py` 验证运行时门禁
