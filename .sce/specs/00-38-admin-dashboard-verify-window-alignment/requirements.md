# 00-38 后台工作台 verify 时间窗口对齐（Admin Dashboard Verify Window Alignment）

> 状态：已完成 | 优先级：P1 | 依赖：00-37 admin-dashboard-context-carry-route-alignment
> 记录目的：补齐 verify 列表的提交时间窗口能力，让 dashboard 到 verify 的时间窗口链路真正闭环。

## 1. 背景

在 `00-37` 中已确认：

- `risk/refund/payment` 已具备目标页时间窗口承接能力
- `verify/pending` 是当前唯一接不住 dashboard 时间窗口的入口

原因不是前端跳转没做，而是 verify 后端列表接口本身当前只支持：

- `userId`
- `status`
- `pageNo/pageSize`

因此要让 dashboard 到 verify 的时间窗口真正闭环，必须先补齐 verify 列表的提交时间筛查能力，再回接管理端页面和 dashboard 跳转。

## 2. 范围

### 2.1 本轮必须处理

- `kaipaile-server/src/main/java/com/kaipai/module/model/verify/dto/IdentityVerificationListReqDTO.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`
- `kaipai-admin/src/types/verify.ts`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/dashboard/OverviewView.vue`

### 2.2 本轮不处理

- verify 详情接口
- 审核动作接口
- reviewedAt 维度筛查

## 3. 需求

### 3.1 后端查询

- **R1** verify 列表查询必须补齐提交时间窗口字段。
- **R2** 提交时间窗口应作用于实名认证记录 `create_time`。
- **R3** 现有 `userId/status/pageNo/pageSize` 行为不得被破坏。

### 3.2 管理端页面

- **R4** `VerificationBoard` 必须补齐提交时间窗口筛查 UI。
- **R5** `VerificationBoard` 必须支持读取路由 query 并回填提交时间窗口后自动查询。
- **R6** 重置操作必须清空提交时间窗口。

### 3.3 dashboard 跳转

- **R7** dashboard 进入 `/verify/pending` 时，应把当前时间窗口映射为 verify 页真实支持的 query 字段。
- **R8** 不得继续让 verify 成为唯一不支持 dashboard 时间窗口闭环的业务线入口。

## 4. 验收标准

- [x] 已新增独立 Spec 并登记索引与代码映射
- [x] verify 后端列表已支持提交时间窗口筛查
- [x] verify 管理页已支持提交时间窗口筛查与 query 回填
- [x] dashboard -> verify 可携带时间窗口进入
- [x] `npm run build` 在 `kaipai-admin` 通过
