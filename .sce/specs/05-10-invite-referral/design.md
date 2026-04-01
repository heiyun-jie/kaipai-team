# 邀请裂变 - 技术设计

_Requirements: 05-10 全部_

## 1. 路由

邀请记录页在 `pkg-card` 分包：

```json
{ "root": "pkg-card", "pages": [
  { "path": "invite/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
]}
```

## 2. 模块分工

| 模块 | 职责 |
|------|------|
| `pkg-card/invite/index.vue` | 邀请记录页 + 邀请海报生成 |
| `types/invite.ts` | 邀请码、裂变记录类型 |
| `api/invite.ts` | 邀请码获取、记录查询、统计接口 |
| `stores/user.ts` | `inviteCount`、`validInviteCount` 集成 |

## 3. 邀请码生成规则

```ts
// 后端生成，6 位大写字母 + 数字
// 排除易混淆字符: O/0, I/1/L
const CHARSET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
```

## 4. 注册流程改造

### 4.1 前端

`pages/login/index.vue` 改造：
- `onLoad` 时检查 `options.inviteCode`，有则存入表单隐藏字段
- 注册请求 `RegisterReqDTO` 新增可选字段 `inviteCode`

### 4.2 后端

`AuthServiceImpl.register()` 改造：
```
if (inviteCode != null) {
  1. 查 invite_code 表找到邀请人
  2. 校验邀请人已认证
  3. 创建 referral_record (is_valid=false)
  4. 设置 user.invited_by_user_id
}
```

`ActorProfileService.updateProfile()` 改造：
```
if (profileCompletion >= 50 && 有 referral_record && !is_valid) {
  1. referral_record.is_valid = true
  2. 邀请人 valid_invite_count += 1
}
```

## 5. 防作弊实现

| 策略 | 实现 |
|------|------|
| 同设备多注册 | `referral_record.device_id` 去重，同 device_id 只计首条 |
| 频率异常 | 同一 invite_code 1 小时内 ≥ 5 条注册 → `flagged=true`，不计入有效 |
| 实名前置 | 邀请人未认证时，`GET /api/invite/code` 返回 403 |

设备 ID 获取：`uni.getSystemInfoSync().deviceId`（微信小程序提供）

## 6. 邀请海报生成

复用名片海报 canvas 能力：
- 背景：品牌渐变色
- 内容：用户昵称 + 邀请语 + 小程序码 + 邀请码文本
- 小程序码通过 `GET /api/invite/qrcode` 获取（后端调微信 `wxacode.getUnlimited`）

## 7. 任务清单

- [ ] T1 后端新建 `invite_code`、`referral_record` 表
- [ ] T2 后端实现邀请码生成、小程序码生成接口
- [ ] T3 后端改造注册接口，支持 inviteCode 参数
- [ ] T4 后端实现被邀请人资料完善后触发有效邀请计数
- [ ] T5 后端实现防作弊策略
- [ ] T6 新建前端 `types/invite.ts`、`api/invite.ts`
- [ ] T7 实现 `pkg-card/invite/index.vue` 邀请记录页 + 海报生成
- [ ] T8 改造 `pages/login/index.vue` 支持 inviteCode 参数
- [ ] T9 等级中心添加邀请入口
- [ ] T10 `stores/user.ts` 集成邀请计数
