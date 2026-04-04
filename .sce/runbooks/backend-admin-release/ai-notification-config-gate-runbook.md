# AI 通知配置门禁 Runbook

> 对应 Spec：
> - `00-29 backend-admin-release-governance`
> - `00-60 current-phase-ai-governance-real-notification-foundation`
>
> 适用范围：
> - 仅当当前批次明确要推进 AI 治理真实通知发送 / provider callback / receipt foundation 时启用
> - 若当前批次不触达 `00-60` 的真实通知基础设施，本 runbook 只保留为后续入口，不构成其它业务批次主阻塞

## 1. 目的

把 AI 治理真实通知配置门禁收口成一页固定流程，避免再出现以下误判：

- 只因为本地 secret 文件存在，就误判“本地输入已就绪”
- 只因为远端 Nacos 里已有部分键，就误判“真实通知链路已可验证”
- 只因为 dry-run 跑过，就误判“线上已经生效”
- 只因为 `provider-code=manual`，就误判“callback token 可以缺省”

## 2. 当前固定输入位

- 本地 gitignored secret 文件：
  - `D:\XM\kaipai-team\.sce\config\local-secrets\ai-resume-notification.env`
- 本地模板文件：
  - `D:\XM\kaipai-team\.sce\config\ai-resume-notification.env.example`
- 目标环境：
  - `101.43.57.62`
  - `NACOS_ENABLED=true`
  - `SPRING_PROFILES_ACTIVE=dev`
- 目标 Nacos dataId：
  - `kaipai-backend-dev.yml`

## 3. 标准顺序

1. 初始化本地 secret 文件
2. 判定本地 AI 通知输入是否合法
3. 跑 AI 通知配置总控
4. 执行标准 `backend-only` 重建
5. 跑 `00-60` 通知基础设施验证脚本

## 4. 第一步：初始化本地 secret 文件

若本机还没有 gitignored secret 文件，执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/init-local-ai-notification-secret-file.py
```

结果：

- 会创建 `.sce/config/local-secrets/ai-resume-notification.env`
- 会预填：
  - `AI_RESUME_NOTIFICATION_ENABLED=true`
  - `AI_RESUME_NOTIFICATION_PROVIDER_CODE=manual`
  - `AI_RESUME_NOTIFICATION_CALLBACK_HEADER=X-Kaipai-Ai-Notification-Token`
- 会写入 placeholder token

注意：

- 这一步只负责建立输入位
- 这一步完成后，门禁通常仍然是 `blocked`
- 未替换真实 `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN` 前，不允许继续宣告“可验证”

## 5. 第二步：判定本地 AI 通知输入是否合法

执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-local-ai-notification-config-inputs.py --label <label>
```

看以下结论：

- `Release Ready: yes`
- `AI_RESUME_NOTIFICATION_ENABLED: passed`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE: passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER: passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN: passed`

当前脚本会拒绝以下输入：

- `replace-with-real-*`
- `fake-*`
- `example`
- `dummy`
- `sample`
- 过短 token
- `AI_RESUME_NOTIFICATION_ENABLED=false`

当前特殊说明：

- `AI_RESUME_NOTIFICATION_PROVIDER_CODE=manual` 允许作为第一阶段真实通知基础设施验证输入
- 这只代表统一 dispatch / receipt callback 骨架可验证
- 不代表商用 vendor 已接入

## 6. 第三步：跑 AI 通知配置总控

本地输入合法后，执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-ai-notification-config-sync-pipeline.py --label <label>
```

总控固定顺序：

1. `read-local-ai-notification-config-inputs.py`
2. `read-backend-nacos-config.py`
3. `run-backend-nacos-config-sync.py`

说明：

- 第 2 步远端预检查用于固化“同步前事实”
- 不要求同步前远端就已经通过
- 若第 1 步本地输入不合法，总控会直接中止并生成 blocked 记录

若只想先看当前阻塞点，再执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-ai-notification-config-sync-pipeline.py --label <label> --dry-run
```

## 7. 第四步：执行标准重建

Nacos 配置来源同步完成后，必须继续执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>
```

原因：

- Nacos 同步不等于运行时已生效
- 当前后端运行时仍需要标准 `backend-only` 重建后，容器与运行 jar 才会统一读取最新配置

## 8. 第五步：跑 `00-60` 真实通知验证脚本

重建完成后执行：

```powershell
python .sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-resume-notification-foundation-validation.py <label>
```

目标样本：

- dispatch sent
- manual send_failed
- pending_receipt
- provider callback delivered
- provider callback receipt_failed

只有这一步跑完，才允许把 `00-60` 从“配置来源已补齐”推进到“真实通知基础设施已可验证”。

## 9. 当前禁止事项

- 不允许把 placeholder token 当成真实输入继续总控
- 不允许跳过 `read-local-ai-notification-config-inputs.py` 直接写 Nacos
- 不允许只做 Nacos 同步，不做 `backend-only` 重建就宣告“线上已生效”
- 不允许只看到后台通知状态字段变化，就宣告“真实 callback 已闭环”

## 10. 当前最短路径

1. 把真实 `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN` 写入：
   `D:\XM\kaipai-team\.sce\config\local-secrets\ai-resume-notification.env`
2. 执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-ai-notification-config-sync-pipeline.py --label <label>`
3. 执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>`
4. 执行：
   `python .sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-resume-notification-foundation-validation.py <label>`
