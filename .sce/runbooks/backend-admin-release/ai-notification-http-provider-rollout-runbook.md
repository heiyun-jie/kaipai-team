# AI 通知 HTTP Provider 发布 Runbook

> 对应 Spec：
> - `00-29 backend-admin-release-governance`
> - `00-60 current-phase-ai-governance-real-notification-foundation`
>
> 适用范围：
> - 当前批次明确要把 AI 通知从 `manual` 推进到 `provider-code=http`
> - 目标是把 bridge endpoint / callback 地址 / backend-only / 样本验证 固化为一次标准总控

## 1. 目的

把 `provider-code=http` 的发布流程固定成一条可复跑链路，避免重复出现：

- 代码已支持 `http` provider，但根本没有真实 bridge endpoint
- 只改了 `provider-code=http`，没有同时改 `callback-url`
- 只同步了 Nacos，没有执行 `backend-only`
- 没有 bridge 输入时还继续口头宣告“下一步就能联调”

## 2. 本地输入文件

- AI 通知基础输入：
  - `D:\XM\kaipai-team\.sce\config\local-secrets\ai-resume-notification.env`
- HTTP bridge 输入：
  - `D:\XM\kaipai-team\.sce\config\local-secrets\ai-notification-http-bridge.env`
- bridge 模板：
  - `D:\XM\kaipai-team\.sce\config\ai-notification-http-bridge.env.example`

## 3. Bridge 输入契约

当前 `provider-code=http` 发布最少必须具备：

- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE=http`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH`
- 可选：
  - `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER`
  - `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN`

当前脚本会自动派生：

- `AI_RESUME_NOTIFICATION_PROVIDER_CODE=http`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT=<PUBLIC_ENDPOINT>`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL=<CALLBACK_BASE_URL><CALLBACK_PATH>`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`

## 4. 标准顺序

1. 初始化 bridge 本地 secret 文件
2. 检查 bridge 输入是否合法
3. 执行 `provider=http` 总控
4. 总控内部固定执行：
   - `bridge-input`
   - `ai-notification-config-sync`
   - `backend-only`
   - `run-ai-resume-notification-foundation-validation.py`

## 5. 初始化 bridge 输入文件

若本机还没有 gitignored bridge 输入文件，执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/init-local-ai-notification-http-bridge-secret-file.py
```

注意：

- 该脚本只负责创建输入位
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT` 默认留空
- 留空时门禁必须判定为 `blocked`

## 6. 只读门禁

执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-local-ai-notification-http-bridge-inputs.py --label <label>
```

通过条件：

- `Release Ready: yes`
- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE: passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT: passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL: passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH: passed`

blocked 时的标准结论：

- 当前没有真实 bridge endpoint/回调地址输入
- 本轮不得继续推 `provider-code=http`
- 必须保留 blocked 记录，而不是口头说“以后再补”

## 7. 一键总控

执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py --label <label> --operator <name>
```

dry-run：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py --label <label> --operator <name> --dry-run
```

总控职责：

- 先检查 bridge 输入是否就绪
- 再把派生后的 `callback-url / http.endpoint / auth` 注入 AI 通知配置总控
- 然后执行标准 `backend-only`
- 最后以 `AI_NOTIFICATION_PROVIDER_CODE=http` 运行 `run-ai-resume-notification-foundation-validation.py`

## 8. 禁止事项

- 不允许没有 `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT` 还切 `provider-code=http`
- 不允许只做 bridge 输入门禁，不做后续 `backend-only`
- 不允许只执行 `backend-only`，不执行 `run-ai-resume-notification-foundation-validation.py`
- 不允许把本地 mock bridge 样本误写成目标环境 `provider=http` 已通过

## 9. blocked 收口

若当前没有真实 bridge endpoint，标准动作是：

1. 执行 `read-local-ai-notification-http-bridge-inputs.py`
2. 执行 `run-ai-notification-http-provider-rollout.py --dry-run`
3. 保留 blocked 记录
4. 在 `00-60` 与 `00-28` 回填“当前缺的是真实 bridge 输入，不是代码骨架”
