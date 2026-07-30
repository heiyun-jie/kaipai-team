# 00-204 小程序个人档案体重常驻展示

## 1. 概述

`pages/actor-profile/edit` 当前已经通过 `actor_profile.weight` 和
`PUT /api/actor/profile/mine` 保存体重，但体重输入只位于默认折叠的“职业资料”中。
本 Spec 将现有体重输入移到“核心资料”的年龄 / 身高行常驻展示，并保持页面其他内容
和既有数据链路不变。

## 2. 用户故事

作为演员用户，我希望在个人档案首屏直接填写和查看体重，不必先展开职业资料。

## 3. 功能需求

### 3.1 页面字段

- WHEN 渲染 `pages/actor-profile/edit` 核心资料 THEN 年龄、身高、体重必须在同一测量行展示。
- WHEN 用户填写体重 THEN 输入必须为数字，显示单位 `kg`，空值文案与年龄 / 身高保持一致。
- WHEN 页面加载已有档案 THEN 常驻体重输入必须回显接口返回的 `weight`。
- WHEN 用户保存 THEN 常驻体重输入必须复用现有 `career.weight` 请求字段，不得创建第二套前端状态。
- WHEN 用户展开职业资料 THEN 原体重输入不得重复出现；籍贯、院校、专业和标签等其他职业资料内容必须保持不变。

### 3.2 数据库字段事实

- 当前数据库、旧表夹具和 `ActorProfile` 已存在唯一 `actor_profile.weight`，类型为可空 `INT`，单位语义为 kg。
- WHEN 后端启动前执行本地 schema 兼容性门禁 THEN 必须检查 `actor_profile.weight` 存在。
- 本轮不得新增迁移、重复列或不同命名的体重字段，不得改写既有体重数据。

### 3.3 接口字段

- WHEN 调用 `PUT /api/actor/profile/mine` THEN 请求必须接受 `career.weight`，允许为 `null`，非空值范围保持既有 `20-300` 约束。
- WHEN 调用 `GET /api/actor/profile/mine` 或保存成功 THEN 响应必须包含扁平字段 `weight`。
- WHEN 保存合法体重 THEN 服务必须写入 `actor_profile.weight` 并在响应中返回相同值。
- 现有 Entity、请求 DTO、响应 DTO 和 Service 已具备该字段；本轮不得新增 `weight_kg`、`body_weight` 或第二个 `weight` 列。

### 3.4 范围约束

- 除移动现有体重输入到常驻测量行外，不修改页面文案、颜色、字号、间距、导航、其他字段或业务行为。
- 不修改 `00-199` 当前未提交的视觉收口内容。
- 不修改公开档案、投递确认、AI 分享图或智能导入对既有 `weight` 的消费方式。

## 4. 非功能需求

- 遵循 `SHARED_CONVENTIONS.md` 与 `mp-ui-change-verification`。
- 构建后必须核对 `src / dist/build / dist/dev` 三层均包含核心资料体重输入。
- 数据库与接口事实必须通过只读 schema 核对和专项测试证明。

## 5. 验收清单

- [x] 核心资料测量行显示年龄、身高、体重。
- [x] 体重显示 `kg`，与现有年龄 / 身高控件同构。
- [x] 页面其他可见内容保持不变。
- [x] 数据库已有唯一 `actor_profile.weight`，启动门禁可检查该列。
- [x] PUT 接受 `career.weight`，GET / PUT 响应返回 `weight`。
- [x] 保存后体重可持久化和回显。
