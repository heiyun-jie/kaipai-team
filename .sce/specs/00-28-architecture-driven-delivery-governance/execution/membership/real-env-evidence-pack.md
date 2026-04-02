# 会员与模板真实环境证据包

## 1. 用途

本文件用于把 membership 联调从“口头确认”收口成“同一样本链证据确认”。

固定验证链：

`membership account / template publish -> level.info / card.personalization -> membership / actor-card / detail / invite / fortune`

## 2. 前台证据点

### 2.1 等级中心

- 页面：
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
- 必截字段：
  - `membershipTier`
  - `level`
  - `shareCapability`
  - 可见 artifact 数

### 2.2 名片页与公开详情页

- 页面：
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue`
- 必截字段：
  - `scene`
  - `templateId`
  - `themeId`
  - 当前 artifact path
  - 是否存在 preview overlay

### 2.3 邀请页与命理页

- 页面：
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
  - `kaipai-frontend/src/pkg-card/fortune/index.vue`
- 必截字段：
  - 主题是否与 actor-card 一致
  - artifact / tone / themeId 是否一致
  - 锁定状态是否与 membership 一致

### 2.4 小程序运行时阻塞证据

- 当小程序截图无法补齐时，必须补一份运行时阻塞证据，避免把“DevTools 未授权”误判成“前端页面坏了”
- 必留字段：
  - 目标 `appid`
  - `cli auto` / `preview` 返回码和错误文案
  - `WeappLog` 关键报错时间点
  - 是否仍出现 `webview loaded / webview page ready`
  - 自动化端口是否实际监听
  - 如果排查过旧缓存，还要记录“新路径重放是否仍失败”

## 3. 接口证据点

### 3.1 能力与摘要接口

- `GET /api/level/info`
- `GET /api/card/personalization`
- `GET /api/card/scene-templates`
- `GET /api/card/config`
- `GET /api/fortune/report`
- `GET /api/ai/quota`

### 3.2 必核字段

- `level.info`
  - `level`
  - `inviteCount`
  - `membershipTier`
  - `shareCapability`
- `card.personalization`
  - `profile.templateId`
  - `profile.sharePreferences`
  - `theme.themeId`
  - `artifacts[].type`
  - `artifacts[].path`
  - `artifacts[].locked`

## 4. 后台证据点

### 4.1 会员账户

- 页面：
  - `/membership/accounts`
- 必截字段：
  - `membershipAccountId`
  - `userId`
  - `status`
  - `effectiveTime`
  - `expireTime`

### 4.2 模板管理

- 页面：
  - `/content/templates`
- 必截字段：
  - `templateId`
  - `sceneKey`
  - `status`
  - `version`
  - `publishLogId`

## 5. 数据库证据点

### 5.1 `membership_account`

- `membership_id`
- `user_id`
- `tier`
- `status`
- `effective_time`
- `expire_time`
- `source_type`
- `source_ref_id`

### 5.2 `card_scene_template`

- `template_id`
- `template_code`
- `scene_key`
- `status`
- `base_theme_json`
- `artifact_preset_json`
- `last_update`

### 5.3 `template_publish_log`

- `publish_log_id`
- `template_id`
- `publish_version`
- `action_type`
- `published_by`
- `published_at`

### 5.4 `admin_operation_log`

- `operation_log_id`
- `module_code`
- `operation_code`
- `target_type`
- `target_id`
- `operation_result`
- `create_time`

### 5.5 `actor_share_preference`

- `preference_id`
- `user_id`
- `scene_key`
- `preferred_artifact`
- `preferred_tone`
- `enable_fortune_theme`

## 6. 同一样本链的最小比对矩阵

| 证据面 | 必须一致的字段 | 样本值 |
|-------|---------------|--------|
| 后台会员账户页 | `membershipAccountId`、`userId`、`status` | |
| 后台模板页 | `templateId`、`sceneKey`、`publishLogId` | |
| `level.info` | `membershipTier`、`shareCapability` | |
| `card.personalization` | `templateId`、`themeId`、`artifacts[].locked` | |
| membership 页 | `membershipTier`、artifact 可见性 | |
| actor-card | `themeId`、artifact path | |
| detail 页 | `themeId`、公开 path | |
| invite / fortune | 主题和锁定状态 | |
| `membership_account` | `user_id`、`status` | |
| `card_scene_template` | `template_id`、`scene_key`、`base_theme_json` | |
| `template_publish_log` | `publish_log_id`、`template_id`、`publish_version` | |
| `admin_operation_log` | `operation_log_id`、`module_code`、`operation_code` | |

## 7. 当前不能误判为完成的点

满足以下任一条，都不能写“membership 闭环完成”：

- 只验证了后台页面存在，没有验证小程序恢复
- 只验证了 `level.info`，没有验证 `card.personalization`
- actor-card / detail / invite / fortune 之间主题或 gating 不一致
- preview overlay 仍被误当作后台发布模板主事实源
- DevTools 当前登录账号不是目标 `appid` 开发者，导致样本截图仍无法生成

## 8. 建议执行顺序

1. 固定样本 `actorUserId / membershipAccountId / templateId / publishLogId`
2. 先抓后台操作与 API 返回
3. 再核对小程序 5 个页面
4. 再查 `membership_account / card_scene_template / template_publish_log`
5. 最后回填 `status/membership-status.md`
