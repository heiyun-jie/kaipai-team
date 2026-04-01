# 05-09 实名认证（Identity Verification）

> 状态：前端已实现（后端审核链路待服务端对接） | 优先级：P0 | 依赖：无
> 被依赖：05-05 v2（等级体系前置条件）、05-10（邀请资格前置条件）

## 1. 功能概述

为演员提供实名认证流程，作为等级体系（05-05）和邀请裂变（05-10）的前置条件。

后端已有数据基础：
- `User.realAuthStatus`：0=未认证, 1=认证中, 2=已认证, 3=认证失败
- `ActorProfile.isCertified`：布尔值
- `ActorProfile.realName`：真实姓名字段

当前缺失：认证提交接口、审核流程、前端认证页面。

## 2. 产品边界

### 2.1 本轮范围

- 演员提交实名认证（姓名 + 身份证号）
- 后台人工审核（初期方案，避免第三方 API 成本）
- 认证状态展示与引导
- 档案完成度 ≥ 70% 作为认证提交前置条件

### 2.2 不在本轮范围

- 第三方身份核验 API（人脸识别、公安实名校验）
- 企业/剧组认证（已有 `CompanyProfile.isCertified`，后续独立处理）
- 认证���诉 / 二次认证

### 2.3 后续可扩展

- 接入第三方实名核验（如腾讯云人脸核身、阿里实人认证）
- 接入芝麻信用 / 其他信用体系

## 3. 需求清单

### 3.1 认证提交

- **R1** 认证入口在"我的"页和等级中心页
- **R2** 提交前置条件：档案完成度 ≥ 70%，不满足时引导去编辑档案
- **R3** 提交信息：真实姓名 + 身份证号
- **R4** 身份证号前端校验格式（18 位，校验位合法）
- **R5** 提交后状态变为"认证中"，等待后台审核

### 3.2 审核��程

- **R6** 初期采用人工审核：管理员在后台审核认证申请
- **R7** 审核结果：通过 → `realAuthStatus=2, isCertified=true`；拒绝 → `realAuthStatus=3`
- **R8** 审核拒绝时需填写拒绝原因，前端展示给用户
- **R9** 认证失败后允许重新提交

### 3.3 状态展示

- **R10** 认证状态在"我的"页、等级中心、名片页均有体现：

| 状态 | 展示 |
|------|------|
| 未认证 (0) | "去认证" 按钮，提示认证后可生成名片 |
| 认证中 (1) | "审核中" 标签，预计 1-3 个工作日 |
| 已认证 (2) | "已认证" 绿色标签 + ✓ |
| 认证失败 (3) | "认证失败" 红色标签 + 失败原因 + "重新提交" |

- **R11** 未认证用户尝试生成名片时，弹窗引导去认证

### 3.4 安全约束

- **R12** 身份证号后端加密存储，前端展示时脱敏（显示前 3 后 4）
- **R13** 每位用户同���时间只能有一个待审核的认证申请
- **R14** 认证通过后不可修改真实姓名和身份证号（需联系客服）

## 4. 数据模型

### 4.1 后端

```sql
-- 认证申请表（新建）
CREATE TABLE identity_verification (
  id              BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id         BIGINT NOT NULL,
  real_name       VARCHAR(32) NOT NULL,
  id_card_no      VARCHAR(256) NOT NULL,   -- 加密存储
  status          TINYINT NOT NULL DEFAULT 1, -- 1=待审核, 2=通过, 3=拒绝
  reject_reason   VARCHAR(256),
  reviewer_id     BIGINT,
  reviewed_at     DATETIME,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status)
);
```

审核通过后同步更新：
- `user.realAuthStatus = 2`
- `actor_profile.isCertified = true`
- `actor_profile.realName = identity_verification.real_name`

### 4.2 前端类型

```ts
interface IdentityVerification {
  status: 0 | 1 | 2 | 3  // 未提交 | 待审核 | 已通过 | 已拒绝
  realName?: string       // 脱敏后
  idCardNo?: string       // 脱敏后 (前3后4)
  rejectReason?: string
  submittedAt?: string
}
```

## 5. 页面设计

### 5.1 认证提交页 `pkg-card/verify/index`

```
┌───────────────────────────┐
│ [返回]    实名认证          │
│                           │
│  ┌─ 说明卡 ────────────┐  │
│  │ 完成实名认证后即可：   │  │
│  │ · 生成个人名片        │  │
│  │ · 邀请好友提升等级     │  │
│  │ · 使用 AI 润色简历     │  │
│  └─────────────────────┘  │
│                           │
│  真实姓名                  │
│  ┌─────────────────────┐  │
│  │ 请输入身份证上的姓名   │  │
│  └─────────────────────┘  │
│                           │
│  身份证号                  │
│  ┌─────────────────────┐  │
│  │ 请输入18位身份证号码   │  │
│  └─────────────────────┘  │
│                           │
│  ⚠️ 信息仅用于身份核实，   │
│  加密存储，不会泄露给第三方 │
│                           │
│  [提交认证]                │
└───────────────────────────┘
```

### 5.2 路由

放在 `pkg-card` 分包：

```json
{ "path": "verify/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
```

## 6. 接��清单

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/api/verify/status` | GET | 获取当前认证状态 | 需登录 |
| `/api/verify/submit` | POST | 提交认证申请 | 需登录 |
| `/api/admin/verify/list` | GET | 管理后台：待审核列表 | 管理员 |
| `/api/admin/verify/review` | POST | 管理后台：审核操作 | 管理员 |

## 7. 验收标准

- [ ] 档案完成度 < 70% 时不允许提交认证，引导去编辑
- [ ] 身份证号格式校验正确（18 位 + 校验位）
- [ ] 提交后状态变为"认证中"
- [ ] 后台审核通过后 `realAuthStatus` 和 `isCertified` 同步更新
- [ ] 审核拒绝后用户可查看原因并重新提交
- [ ] 身份证号加密存储，前端脱敏展示
- [ ] 未认证用户无法生成名片（引导认证）
- [ ] `npm run build:mp-weixin` 通过
