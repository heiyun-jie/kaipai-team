# 测试小程序候选单一事实源与人工验收准入 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 事实源模型

```text
candidate-manifest + checksum
              |
artifact-evidence + checksum
              |
frozen artifacts/mini-program-test  <-- 唯一候选事实源
              |
              +---- compare --> runtime dist/dev/mp-weixin (唯一测试入口)
              |
              +---- optional compare --> explicitly supplied isolated build dir
                                      |
                                      +-- runtime-readiness.json
```

`dist/build` 与 `dist/dev` 都不能产生候选身份。Candidate ID 只能来自冻结记录目录和已校验 manifest。00-252 之后，工作区 `dist/build` 不再是日常测试准入的默认输入；只有显式 `--build-dir` 才进行隔离构建诊断。

测试候选构建在复制 `mini-program-test` 前写入字节稳定的 `project.private.config.json`：

```json
{
  "setting": {
    "urlCheck": false
  }
}
```

该文件只进入测试候选，防止 DevTools 首次打开后增加 1 个运行本地文件导致完整目录 mismatch；正式候选保持原产物集合。

## 2. 准入脚本

新增 `.sce/runbooks/backend-admin-release/scripts/verify-test-miniapp-acceptance.py`：

1. 校验 Candidate ID 字符集和记录目录边界，拒绝绝对路径和目录穿越。
2. 校验 `candidate-manifest.sha256` 与 `artifact-evidence.sha256` sidecar。
3. 校验最终 manifest 反向绑定当前 artifact evidence SHA256；允许 `DRAFT/NO-GO` 仅因远端生产 helper 或凭据治理阻塞，其他 blocker 失败关闭。
4. 复用 `generate-release-candidate-manifest.py::validate_artifact_evidence` 校验四类候选产物和 API target proof。
5. 复用 `collect_repository` 比较 backend/admin/frontend 的 commit、branch 和 overlays；root 中的 Spec/证据文档变化不冒充运行代码变化。
6. 用统一的 `hash_artifact_directory` 比较冻结候选与固定 dev 的 `fileCount / totalSize / treeSha256`；仅当调用方显式传入 `--build-dir` 时比较隔离 build。
7. 扫描 dev 运行文件，要求测试 API 命中大于零，本地/正式 API 命中为零。
8. 校验 `records/<Candidate>/00-243/runtime-readiness.json` 与同一 Candidate 和同一 dev 目录树绑定。

## 3. 运行证明合同

```json
{
  "schemaVersion": 1,
  "candidateId": "CANDIDATE",
  "projectPath": "ABSOLUTE_DIST_DEV_PATH",
  "runtimeTreeSha256": "SHA256",
  "expectedApiBaseUrl": "https://test-api.kplyyk.com",
  "testApiMatches": 1,
  "localApiMatches": 0,
  "releaseApiMatches": 0,
  "liveRequestVerified": true,
  "liveRequestEnvironment": "test",
  "status": "PASSED"
}
```

该文件必须由完成项目级 compile cache 清理、内部刷新、缓存扫描和实时鉴权请求的 `00-243` 执行步骤生成。仅有磁盘 mismatch=0 不能替代运行证明。

## 4. 裁决优先级

1. 候选记录或哈希错误：`INVALID_CANDIDATE / exit 2`。
2. 实现输入或显式隔离 build 漂移：`CANDIDATE_REFREEZE_REQUIRED / exit 3`。
3. dev、API 或运行证明不一致：`RUNTIME_NOT_SWITCHED / exit 4`。
4. 全部通过：`READY_FOR_MANUAL_ACCEPTANCE / exit 0`。

优先级保证当前源码或 build 已变化时不会继续把旧 dev 候选描述为待验收。

## 5. 测试

新增 `test_verify_test_miniapp_acceptance.py`，使用临时 Git 仓库和最小四类候选产物覆盖：

- 完整一致通过；
- 前端输入变化要求重冻；
- build 漂移要求重冻；
- dev 漂移阻断运行态；
- 运行证明不匹配阻断运行态；
- 冻结候选被修改判定无效。

## 6. 桌面与生产边界

脚本不调用微信 CLI，不枚举或结束微信进程，不清缓存，不上传小程序，不连接生产主机。当前运行态的切换仍由 `00-243` 在获得对应操作窗口后执行。
