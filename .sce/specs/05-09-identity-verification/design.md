# 实名认证 - 技术设计

_Requirements: 05-09 全部_

## 1. 路由

```json
{ "root": "pkg-card", "pages": [
  { "path": "verify/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
]}
```

## 2. 模块分工

| 模块 | 职责 |
|------|------|
| `pkg-card/verify/index.vue` | 认证提交页 |
| `types/verify.ts` | 认证状态类型 |
| `api/verify.ts` | 认证接口 |
| `stores/user.ts` | 认证状态集成（`isCertified`, `realAuthStatus`） |

## 3. 身份证校验

```ts
// utils/verify.ts
function validateIdCard(idCard: string): boolean {
  if (idCard.length !== 18) return false
  const weights = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
  const checkCodes = '10X98765432'
  let sum = 0
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCard[i]) * weights[i]
  }
  return idCard[17].toUpperCase() === checkCodes[sum % 11]
}

function maskIdCard(idCard: string): string {
  return idCard.slice(0, 3) + '***********' + idCard.slice(-4)
}
```

## 4. 后端加密存储

- 身份证号使用 AES-256 加密后存入 `identity_verification.id_card_no`
- 密钥通过 Nacos 配置中心管理，不硬编码
- 查询时解密仅在后台审核页面，前端永远只拿脱敏值

## 5. 状态机

```
未提交(0) → 提交 → 待审核(1)
                     ├→ 通过(2) → 结束
                     └→ 拒绝(3) → 可重新提交 → 待审核(1)
```

## 6. 任务清单

- [ ] T1 新建 `types/verify.ts`、`api/verify.ts`、`utils/verify.ts`
- [ ] T2 实现 `pkg-card/verify/index.vue` 认证提交页
- [ ] T3 后端新建 `identity_verification` 表和接口
- [ ] T4 后端实现审核接口（管理员）
- [ ] T5 `stores/user.ts` 集成认证状态
- [ ] T6 "我的"页和等级中心添加认证入口与状态展示
- [ ] T7 未认证��户名片页拦截引导
