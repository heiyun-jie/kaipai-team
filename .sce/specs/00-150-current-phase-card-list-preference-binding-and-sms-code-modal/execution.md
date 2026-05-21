# 00-150 执行记录

## 2026-04-26 任务建立

触发原因：

- 用户在 `pkg-card/card-list/index` 点击“下一步”后进入下一页弹窗：`{"code":400,"message":"分享偏好未绑定","data":null}`。
- 用户要求 `https://kplyyk.com/api/auth/sendCode` 成功时把响应 `data` 放入弹窗。

处理原则：

- 不在读取个性化时兜底。
- 不吞错，不降级，不保留脏数据。
- 通过创建链路写入必需绑定，通过迁移修复线上已存在缺失绑定。

## 已完成修改

- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java`
  - 新建分享卡后写入 `actor_share_preference`。
  - 复用已存在 active 分享卡时复核偏好绑定。
- `kaipaile-server/src/main/resources/db/migration/V20260426_023__share_card_preference_binding_repair.sql`
  - 备份缺失偏好的 active 分享卡。
  - 补齐 `preferred_artifact='miniProgramCard'`。
- `kaipai-frontend/src/pages/login/index.vue`
  - 验证码发送成功后用弹窗展示后端返回验证码。

## 本地审查

- `mvn -q -DskipTests compile`：通过。
- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过，并已同步到 `dist/dev/mp-weixin`。
- `npm run audit:mp-package`：通过。

包体结果：

```text
main      508.61 KB / 2 MB
pkg-card  111.58 KB / 2 MB
pkg-tools 28.21 KB / 2 MB
```

构建产物审查：

- `dist/build/mp-weixin` 已包含 `验证码发送成功` 与 `验证码：{data}` 弹窗逻辑。
- `dist/dev/mp-weixin` 已同步同一逻辑。

## 发布记录

- Schema 发布：`20260426-210043-backend-schema-share-card-preference-binding-repair`。
- 后端发布：`20260426-210122-backend-only-share-card-preference-binding-fix`。
- 后端 jar SHA256：`B1BD7EEC5DD320290CC43122618950619A62E33B4AE27D9374044065E6037F8B`。

## 线上审查

线上域名：`https://kplyyk.com`。

验证码接口审查：

```json
{
  "sendCodeCode": 200,
  "sendCodeMessage": "验证码发送成功",
  "sendCodeDataPresent": true
}
```

分享页下一步链路审查：

```json
{
  "authCode": 200,
  "tokenPresent": true,
  "profileSaveCode": 200,
  "createCode": 200,
  "createdCardId": 15,
  "personalizationCode": 200,
  "personalizationMessage": "操作成功",
  "preferredArtifact": "miniProgramCard"
}
```

数据库绑定审查：

```text
missing_pref_count=0
backup_rows=3
schema_applied=1
```

全量线上 OpenAPI 模拟审查：

```json
{
  "totalOperations": 161,
  "serverFailureCount": 0,
  "businessCodeGte500WarningCount": 0,
  "failures": []
}
```

审查报告：`output/online-api-audit/20260426-2105-share-card-preference-binding-fix.json`。

## 审查状态

当前状态：已完成。

内部审查评分：95 / 95。

说明：本轮未在个性化读取处增加默认值兜底；错误源通过创建写入和数据库迁移修复，读取强校验保持不变。
