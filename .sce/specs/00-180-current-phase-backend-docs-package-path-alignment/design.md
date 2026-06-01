# 当前阶段后端包结构迁移文档对齐 - 技术设计

## 1. 设计结论

本轮采用“三层文档治理”方案：

```text
P0 活文档：必须更新到当前包结构
P1 近期能力文档：追加迁移后当前路径注记
P2 历史证据：保留原文，只在被当作当前入口时加说明
```

这样既能防止后续开发被旧路径误导，也不会把历史执行记录改成与当时事实不符的内容。

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 文档分层

### 2.1 P0 活文档

这些文档直接指导当前开发，必须更新：

| 文件 | 更新目标 |
|------|----------|
| `kaipaile-server/AGENTS.md` | 如有必要，补充后端当前包结构总入口说明 |
| `kaipaile-server/.agents/backend-conventions.md` | 从“业务目录在 module”改为当前六个包根职责 |
| `kaipaile-server/.agents/project-architect.md` | 按业务分区重写当前路径 |
| `kaipaile-server/.agents/auth-security-agent.md` | 更新 auth / verify / sms / wechat 路径 |
| `kaipaile-server/.agents/talent-profile-agent.md` | 更新 actor / crew / card / level 路径 |
| `kaipaile-server/.agents/recruit-transaction-agent.md` | 更新 recruit / order / payment / refund 路径 |
| `kaipaile-server/.agents/ai-governance-agent.md` | 更新 AI controller / service / model / integration 路径 |
| `kaipaile-server/.agents/admin-operations-agent.md` | 更新 admin / system / referral / adminauth 路径 |
| `.sce/steering/CURRENT_CONTEXT.md` | 更新当前后端代码基线中的旧路径 |
| `.sce/specs/spec-code-mapping.md` | 更新当前事实源路径，历史条目加标注 |

_Requirements: 3.1, 3.2_

### 2.2 P1 近期能力文档

这些文档近期仍会被继续查阅，但其中部分内容属于执行时点事实。处理方式是追加迁移后当前路径：

| Spec | 文件 | 处理方式 |
|------|------|----------|
| `00-176` | `tencent-cloud-phone-realname-investigation.md`、`execution.md` | 保留调研时旧路径，追加当前 auth / verify / sms / realname 路径注记 |
| `00-177` | `design.md`、`execution.md` | 把短信 provider 当前路径指到 `integration/sms`，保留历史说明 |
| `00-178` | `design.md`、`execution.md` | 把实名 provider 当前路径指到 `integration/verify`，保留历史说明 |
| `00-179` | `tasks.md` 或 `execution.md` | 可追加本 Spec 为后续治理承接，不重复写全量规则 |

_Requirements: 3.3_

### 2.3 P2 历史证据

这些文件默认不改：

| 类型 | 示例 | 策略 |
|------|------|------|
| 发布记录 | `.sce/runbooks/backend-admin-release/records/*.md` | 保留原始路径，作为当时执行证据 |
| 历史 `execution.md` | 早期后端 execution 记录 | 保留原始路径，除非该文档仍被当前入口引用 |
| 历史架构学习材料 | `00-26-*` 等 | 保留原文，必要时只加“历史材料”说明 |

_Requirements: 3.4_

## 3. 路径映射规则

| 旧路径 | 新路径 | 备注 |
|--------|--------|------|
| `src/main/java/com/kaipai/module/controller/admin/*` | `src/main/java/com/kaipai/controller/admin/*` | 后台管理接口 |
| `src/main/java/com/kaipai/module/controller/{domain}/*` | `src/main/java/com/kaipai/controller/api/{domain}/*` | 小程序 / C 端接口 |
| `src/main/java/com/kaipai/module/server/{domain}/service/*` | `src/main/java/com/kaipai/service/{domain}/*` | 业务服务 |
| `src/main/java/com/kaipai/module/server/{domain}/service/impl/*` | `src/main/java/com/kaipai/service/{domain}/impl/*` | 业务服务实现 |
| `src/main/java/com/kaipai/module/server/{domain}/mapper/*` | `src/main/java/com/kaipai/mapper/{domain}/*` | MyBatis Mapper |
| `src/main/java/com/kaipai/module/model/{domain}/*` | `src/main/java/com/kaipai/model/{domain}/*` | DTO / entity |
| `src/main/java/com/kaipai/module/server/auth/sms/*` | `src/main/java/com/kaipai/integration/sms/*` | 腾讯云 SMS provider |
| `src/main/java/com/kaipai/module/server/verify/realname/*` | `src/main/java/com/kaipai/integration/verify/*` | 腾讯云实名 provider |
| `src/main/java/com/kaipai/module/server/wechat/*` | `src/main/java/com/kaipai/integration/wechat/*` | 微信小程序能力 |
| `src/main/java/com/kaipai/module/server/ai/provider/*` | `src/main/java/com/kaipai/integration/ai/*` | AI 供应商适配 |

_Requirements: 3.5_

## 4. Agent 文档目标结构

### 4.1 身份入口层

当前应写为：

```text
src/main/java/com/kaipai/controller/api/auth
src/main/java/com/kaipai/controller/api/verify
src/main/java/com/kaipai/controller/admin/auth
src/main/java/com/kaipai/service/auth
src/main/java/com/kaipai/service/verify
src/main/java/com/kaipai/model/auth
src/main/java/com/kaipai/model/verify
src/main/java/com/kaipai/mapper/verify
src/main/java/com/kaipai/integration/sms
src/main/java/com/kaipai/integration/verify
src/main/java/com/kaipai/integration/wechat
```

### 4.2 供给资料层

当前应写为：

```text
src/main/java/com/kaipai/controller/api/actor
src/main/java/com/kaipai/controller/api/crew
src/main/java/com/kaipai/controller/api/card
src/main/java/com/kaipai/controller/api/level
src/main/java/com/kaipai/service/actor
src/main/java/com/kaipai/service/crew
src/main/java/com/kaipai/service/card
src/main/java/com/kaipai/model/actor
src/main/java/com/kaipai/model/crew
src/main/java/com/kaipai/model/card
src/main/java/com/kaipai/model/level
src/main/java/com/kaipai/mapper/actor
src/main/java/com/kaipai/mapper/crew
src/main/java/com/kaipai/mapper/card
```

### 4.3 交易撮合层

当前应写为：

```text
src/main/java/com/kaipai/controller/api/recruit
src/main/java/com/kaipai/controller/api/order
src/main/java/com/kaipai/controller/api/payment
src/main/java/com/kaipai/controller/api/refund
src/main/java/com/kaipai/controller/admin/recruit
src/main/java/com/kaipai/service/recruit
src/main/java/com/kaipai/service/order
src/main/java/com/kaipai/service/payment
src/main/java/com/kaipai/service/refund
src/main/java/com/kaipai/model/recruit
src/main/java/com/kaipai/model/order
src/main/java/com/kaipai/model/payment
src/main/java/com/kaipai/model/refund
src/main/java/com/kaipai/mapper/recruit
src/main/java/com/kaipai/mapper/order
src/main/java/com/kaipai/mapper/payment
src/main/java/com/kaipai/mapper/refund
```

### 4.4 AI 能力层

当前应写为：

```text
src/main/java/com/kaipai/controller/api/ai
src/main/java/com/kaipai/controller/admin/ai
src/main/java/com/kaipai/service/ai
src/main/java/com/kaipai/model/ai
src/main/java/com/kaipai/mapper/ai
src/main/java/com/kaipai/integration/ai
```

### 4.5 后台治理层

当前应写为：

```text
src/main/java/com/kaipai/controller/admin
src/main/java/com/kaipai/service/adminauth
src/main/java/com/kaipai/service/system
src/main/java/com/kaipai/service/referral
src/main/java/com/kaipai/model/adminauth
src/main/java/com/kaipai/model/system
src/main/java/com/kaipai/model/referral
src/main/java/com/kaipai/mapper/adminauth
src/main/java/com/kaipai/mapper/system
src/main/java/com/kaipai/mapper/referral
```

_Requirements: 3.1, 3.5_

## 5. SCE 文档处理规则

### 5.1 `spec-code-mapping.md`

处理策略：

1. 对仍在当前主线或近期能力中使用的后端路径，更新为新路径。
2. 对明显属于历史记录的旧路径，增加“历史路径，迁移后见 `00-179 / 00-180`”说明。
3. 不为了清零旧字符串而破坏历史语境。

### 5.2 `CURRENT_CONTEXT.md`

处理策略：

1. 当前代码基线中的后端路径必须改为新路径。
2. 如需说明历史迁移，引用 `00-179`，不在 CURRENT_CONTEXT 中展开长表。

### 5.3 近期腾讯云 Spec

处理策略：

1. `00-176` 作为调研文档保留调研时路径，同时追加迁移后路径。
2. `00-177` 把短信 provider 当前路径明确为 `integration/sms`。
3. `00-178` 把实名 provider 当前路径明确为 `integration/verify`。

_Requirements: 3.2, 3.3, 3.4_

## 6. 验证命令

完成后执行：

```powershell
rg -n "src/main/java/com/kaipai/module|com\.kaipai\.module|module/server|module/controller|module/model" `
  kaipaile-server/.agents `
  .sce/steering/CURRENT_CONTEXT.md `
  .sce/specs/spec-code-mapping.md `
  .sce/specs/00-176-current-phase-tencent-cloud-phone-realname-integration-research `
  .sce/specs/00-177-current-phase-tencent-sms-login-enablement `
  .sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement `
  --glob "*.md"
```

期望：

- `kaipaile-server/.agents` 无旧路径命中。
- `CURRENT_CONTEXT.md` 无旧路径命中。
- `spec-code-mapping.md` 如仍有旧路径，必须标注历史语境。
- `00-176 / 00-177 / 00-178` 如仍有旧路径，必须紧邻迁移后当前路径注记。

_Requirements: 3.6_

## 7. 非目标

- 不改写 `.sce/runbooks/backend-admin-release/records/*.md`。
- 不尝试让全仓所有历史文档旧路径命中数归零。
- 不改业务代码。
- 不执行 actor profile stash 恢复。
- 不处理 `target/classes`。
