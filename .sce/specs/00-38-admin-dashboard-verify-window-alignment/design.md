# 00-38 设计说明

## 1. 设计原则

- 用最小字段集补齐 verify 缺口
- dashboard 与目标页统一按“提交时间”口径对齐
- 不扩展到审核时间等非当前必要维度

## 2. 设计策略

### 2.1 后端 DTO 与查询

`IdentityVerificationListReqDTO` 新增：

- `submitTimeFrom`
- `submitTimeTo`

`IdentityVerificationServiceImpl.adminList()` 在现有 wrapper 上增加：

- `create_time >= submitTimeFrom`
- `create_time <= submitTimeTo`

### 2.2 前端管理页

`VerificationBoard` 新增“提交时间”时间范围筛查，并读写：

- `filters.submitTimeFrom`
- `filters.submitTimeTo`

同时支持从路由 query 回填：

- `submitTimeFrom`
- `submitTimeTo`

### 2.3 dashboard 跳转

`OverviewView` 跳到 `/verify/pending` 时映射：

- `submitTimeFrom=dateFrom`
- `submitTimeTo=dateTo`

## 3. 影响文件

- `kaipaile-server/src/main/java/com/kaipai/module/model/verify/dto/IdentityVerificationListReqDTO.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`
- `kaipai-admin/src/types/verify.ts`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
