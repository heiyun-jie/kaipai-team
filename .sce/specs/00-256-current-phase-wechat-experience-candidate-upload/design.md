# 微信体验版测试 Candidate 上传 - 技术设计

## 1. 输入

```text
Candidate: 20260902-145540-v3-draft
Project: D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin
AppID: wx4dcc4e1066fd0fb9
Version: 3.0.0.20260902.145540
Description: 体验测试 Candidate 20260902-145540-v3-draft
```

_Requirements: 3.1, 3.2_

## 2. 上传前门禁

1. 执行 `verify-test-miniapp-acceptance.py`。
2. 复核固定目录文件数、字节数、tree SHA256 和 `project.config.json` AppID。
3. 扫描测试、本地、正式 API 目标。
4. 只读检查微信 CLI / 进程 / 登录状态。
5. 读取 `runtime-readiness.json` 的桌面非干扰字段和 `test-stack-readiness.json` 的生产未变字段。

任何一项失败均不上传。

_Requirements: 3.1-3.3_

## 3. 上传命令

使用当前已运行微信工具服务，不指定 `--port`：

```powershell
& 'D:\AP\微信web开发者工具\cli.bat' upload `
  --project 'D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin' `
  --version '3.0.0.20260902.145540' `
  --desc '体验测试 Candidate 20260902-145540-v3-draft' `
  --info-output '<record>/upload-info.json'
```

按用户确认，本轮直接使用微信开发者工具的 `upload` 提交体验测试候选。CLI 返回 `upload` 成功且退出码为 0 后，状态记录为 `DEVTOOLS_EXPERIENCE_CANDIDATE_UPLOADED`；不再进入公众平台页面执行额外版本操作。

_Requirements: 3.3, 3.4_

## 4. 证据

记录目录：

```text
.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-256/
```

包含 CLI 原始输出、`upload-info.json`、上传前后目录哈希、生产未变证明和非干扰字段。事务副本位于本 Spec 的 `evidence/`。

_Requirements: 3.4, 4_

## 5. 回滚

CLI 已上传的开发版本不通过本地文件删除回滚。业务回滚方式是重新上传上一冻结 Candidate 或在微信公众平台选择上一开发版本；本轮只在独立事务副本验证状态记录可恢复，不修改当前冻结产物。正式线上版本未变化，因此不需要生产回切。

_Requirements: 3.5, 4_
