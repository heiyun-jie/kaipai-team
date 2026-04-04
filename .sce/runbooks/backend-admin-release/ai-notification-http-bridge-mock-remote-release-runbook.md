# AI 通知 HTTP Bridge Mock 远端发布 Runbook

> 对应 Spec：
> - `00-29 backend-admin-release-governance`
> - `00-60 current-phase-ai-governance-real-notification-foundation`
>
> 适用范围：
> - 当前没有真实商用 vendor/bridge
> - 但需要把 `provider-code=http` 推进到目标环境可验证

## 1. 目的

把远端 bridge mock 的部署标准化，避免继续出现：

- 只在本机起 mock，目标环境根本不可达
- 每次都手工 ssh 起进程，进程丢了也没记录
- 没有固定公网 endpoint，就先把 `provider-code=http` 写进 Nacos

## 2. 标准入口

dry-run：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-mock-remote-release.py --label <label> --operator <name> --dry-run
```

正式发布：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-mock-remote-release.py --label <label> --operator <name> --sync-local-secret
```

## 3. 发布动作

脚本固定执行：

1. 校验 `ssh key auth`
2. 上传 `run-ai-notification-http-bridge-mock.py` 到远端
3. 停掉旧 bridge mock 进程
4. 在远端 `0.0.0.0:19081` 拉起新进程
5. 先做远端本机探活
6. 再做公网探活
7. 若公网可达，可选回写本地 bridge secret

## 4. 当前默认口径

- 远端目录：`/home/kaipaile/ai-notification-http-bridge`
- 默认端口：`19081`
- 默认公网 endpoint：`http://101.43.57.62:19081/`
- 默认 callback base url：`http://101.43.57.62/api`

## 5. 与 `provider=http` 总控的关系

只有在远端 bridge mock 公网探活通过后，才允许继续执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py --label <label> --operator <name>
```

若远端 bridge mock 发布失败或公网不可达，本轮应先保留发布记录，再决定是否进入 nginx 代理方案。
