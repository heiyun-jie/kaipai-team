# 05-10 邀请裂变（Invite Referral）

> 状态：待实现 | 优先级：P0 | 依赖：05-09（实名认证）
> 被依赖：05-05 v2（等级计算数据来源）

## 1. 功能概述

演员通过邀请新用户注册来提升等级。邀请人数是等级体系（05-05）的核心驱动数据。

后端已有 `invite_record` 表，但当前用于剧组邀请演员参演，与"用户裂变邀请"是**不同概念**。需新建裂变邀请模型。

## 2. 产品边界

### 2.1 本轮范围

- 生成个人邀请码 / 邀请链接（小程序码）
- 被邀请人注册后自动关联邀请关系
- 邀请计数与等级联动
- 邀请记录查看
- 防作弊基础策略

### 2.2 不在本轮范围

- 邀请奖励（现金、积分、实物）
- 多级裂变（A 邀 B、B 邀 C，A 不算 C）
- 团队邀请 / 剧组批量邀请

## 3. 需求清单

### 3.1 邀请码

- **R1** 每位已认证用户自动生成唯一邀请码（6-8 位字母数字组合）
- **R2** 邀请码可生成对应小程序码图片，用于分享
- **R3** 邀请链接格式：小程序路径 `pages/login/index?inviteCode=XXXX`

### 3.2 邀请流程

- **R4** 被邀请人通过邀请码/链接进入小程序 → 注册 → 自动绑定邀请关系
- **R5** 只有被邀请人**完成注册**才计为有效邀请（仅扫码不算）
- **R6** 被邀请人必须是**新用户**（未注册过的手机号）
- **R7** 每个新用户只能被一个邀请人邀请（首次注册时绑定）

### 3.3 邀请计数

- **R8** 有效邀请 = 被邀请人成功注册数（不要求被邀请人也完成认证）
- **R9** 邀请计数实时更新，等级随之自动提升
- **R10** 等级只升不降：被邀请人注销账号不扣减邀请计数

### 3.4 防作弊

- **R11** 邀请人必须已通过实名认证
- **R12** 被邀请人必须完善演员资料（档案完成度 ≥ 50%）后邀请才计为"有效"
- **R13** 同一设备 ID 注册的多个账号，只计第一个为有效邀请
- **R14** 短时间内（1 小时）同一邀请码注册超过 5 个，触发人工审核

### 3.5 邀请记录

- **R15** 邀请记录页展示：被邀请人昵称（脱敏）、注册时间、是否有效
- **R16** 邀请记录页在等级中心可达

### 3.6 入口

- **R17** 等级中心页"邀请好友"按钮 → 生成邀请海报/小程序码
- **R18** 名片页底部可添加"邀请好友一起用"引导

## 4. 数据模型

### 4.1 后端

```sql
-- 邀请码表
CREATE TABLE invite_code (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT NOT NULL UNIQUE,
  code         VARCHAR(8) NOT NULL UNIQUE,  -- 邀请码
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_code (code)
);

-- 裂变邀请记录（区别于已有的 invite_record 剧组邀请表）
CREATE TABLE referral_record (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  inviter_user_id  BIGINT NOT NULL,       -- 邀请人
  invitee_user_id  BIGINT NOT NULL,       -- 被邀请人
  invite_code      VARCHAR(8) NOT NULL,
  device_id        VARCHAR(128),          -- 被邀请人设备 ID
  is_valid         BOOLEAN DEFAULT FALSE, -- 是否有效（被邀请人完善资料后变 true）
  flagged          BOOLEAN DEFAULT FALSE, -- 是否被标记为可疑
  registered_at    DATETIME NOT NULL,     -- 被邀请人注册时间
  validated_at     DATETIME,              -- 变为有效的时间
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_invitee (invitee_user_id),
  INDEX idx_inviter (inviter_user_id)
);

-- User 表新增
ALTER TABLE user ADD COLUMN invite_code VARCHAR(8) DEFAULT NULL COMMENT '用户邀请码';
ALTER TABLE user ADD COLUMN invited_by_user_id BIGINT DEFAULT NULL COMMENT '邀请人 ID';
ALTER TABLE user ADD COLUMN valid_invite_count INT DEFAULT 0 COMMENT '有效邀请计数（冗余，用于快速查等级）';
```

### 4.2 前端类型

```ts
interface InviteInfo {
  inviteCode: string
  validInviteCount: number
  totalInviteCount: number  // 含未生效的
}

interface ReferralRecord {
  inviteeNickname: string   // 脱敏
  registeredAt: string
  isValid: boolean
  validatedAt?: string
}
```

## 5. 邀请海报

邀请海报由前端 canvas 生成（复用名片海报能力）：

```
┌───────────────────────────┐
│                           │
│  「开拍了」               │
│  演员专属名片平台          │
│                           │
│  {用户昵称} 邀请你加入     │
│                           │
│  [小程序码图片]            │
│  长按扫码，开始制作你的名片 │
│                           │
│  邀请码: ABCD1234          │
└───────────────────────────┘
```

## 6. 接口清单

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/api/invite/code` | GET | 获取/生成邀请码 | 需登录+已认证 |
| `/api/invite/qrcode` | GET | 生成邀请小程序码图片 | 需登录+已认证 |
| `/api/invite/records` | GET | 邀请记录列表 | 需登录 |
| `/api/invite/stats` | GET | 邀请统计（有效数/总数） | 需登录 |
| `/api/auth/register` | POST | 注册时增加 `inviteCode` 可选参数 | 公开 |

注：注册接口需改造，增加 `inviteCode` 字段处理邀请绑定。

## 7. 注册流程改造

```
原流程：手机号 + 验证码 + 角色 → 注册
新流程：手机号 + 验证码 + 角色 + inviteCode(可选) → 注册
  → 如有 inviteCode：
    1. 校验邀请码有效
    2. 创建 referral_record (is_valid=false)
    3. user.invited_by_user_id = 邀请人 ID
  → 被邀请人后续完善资料至 ≥ 50%：
    1. referral_record.is_valid = true
    2. 邀请人 user.valid_invite_count += 1
    3. 触发邀请人等级重算
```

## 8. 验收标准

- [ ] 已认证用户可生成邀请码和小程序码
- [ ] 被邀请人通过邀请链接注册后自动绑定邀请关系
- [ ] 被邀请人完善资料后邀请变为有效，邀请人等级自动提升
- [ ] 同一新用户只能被一个人邀请
- [ ] 未认证用户不能生成邀请码
- [ ] 防作弊：同设备多注册只计首个，异常频率触发标记
- [ ] 邀请记录页可查看所有邀请及状态
- [ ] 注册页正确处理 inviteCode 参数
- [ ] `npm run build:mp-weixin` 通过
