# 00-54 当前阶段演员主线前端 Mock 退场（Current Phase Actor Mainline Mock Retirement）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-27 mini-program-frontend-architecture，03-04 page-actor-profile-edit，04-04 page-actor-profile-detail
> 记录目的：把演员首页、演员公开详情和本人档案编辑依赖的 `actor` 前端 API，从“仍保留 mock 双轨”推进到“只认真实接口”，避免当前阶段演员主入口继续存在假事实源。

## 1. 背景

当前产品口径已经切换为：

- 演员首页主入口是演员档案列表
- `pages/actor-profile/detail` 是公开名片页
- `pages/actor-profile/edit` 是本人演员档案编辑主入口

但前端 `src/api/actor.ts` 仍保留：

- `getMyActorProfile`
- `updateActorProfile`
- `searchActors`
- `getActorDetail`

四个接口的 `useApiMock('actor') ? mock : real` 双轨分支。

这会让当前阶段演员主线继续停留在“页面看起来已切真，但源码仍允许退回 mock”的不一致状态，因此需要单独起 spec 收口。

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-54` Spec，固化演员主线前端 mock 退场边界
- 移除 `src/api/actor.ts` 中 `getMyActorProfile / updateActorProfile / searchActors / getActorDetail` 的 mock 分支
- 清理 `src/mock/service.ts` 中已无入口的 actor API mock 函数
- 清理 `src/utils/runtime.ts` 中已无使用方的 `actor` capability
- 回填 `00-28` 状态文档、路线图 / 任务或总体评估
- 更新 Spec 索引与映射

### 2.2 本轮不处理

- 删除 `mockActors` 本体
- 删除 invite、fortune、AI 等仍依赖 `mockActors` 的演示域
- 重做演员档案产品结构、字段模型或公开名片 UI
- 处理 `/api/actor/profile/{userId}` 兼容接口是否退场

## 3. 需求

### 3.1 当前阶段演员主线事实源

- **R1** 当前阶段 `getMyActorProfile / updateActorProfile / searchActors / getActorDetail` 不得继续保留 `useApiMock('actor')` 双轨分支。
- **R2** 当前阶段演员主线必须直接调用真实接口：
  - `GET /api/actor/profile/mine`
  - `PUT /api/actor/profile`
  - `GET /api/actor/search`
  - `GET /api/actor/{userId}`
- **R3** 当前阶段如果演员档案、演员搜索或公开详情接口有问题，页面必须直接暴露真实错误，不得再由前端 actor mock 掩盖。

### 3.2 Mock 退场边界

- **R4** `src/mock/service.ts` 中 `getActorProfileMock / updateActorProfileMock / searchActorsMock / getActorDetailMock` 必须删除。
- **R5** `mockActors` 作为 invite / AI / fortune 等演示域依赖的基础数据可以保留，但必须明确它不再承担演员主线 API 的运行时事实源。
- **R6** `src/utils/runtime.ts` 中若 `actor` capability 已无使用方，必须同步删除，避免继续暗示演员主线支持 mock 兜底。

### 3.3 治理回填

- **R7** 必须通过独立 Spec 固化这次演员主线 mock 退场，不得只改代码。
- **R8** 必须同步回填 `00-28`，让后续读文档的人能直接看到：演员首页和演员档案主线已不再保留前端 actor mock 双轨。

## 4. 验收标准

- [x] 已新增独立 `00-54` Spec 并登记索引与映射
- [x] `src/api/actor.ts` 已不再保留 `useApiMock('actor')` 分支
- [x] `src/mock/service.ts` 已删除无入口 actor API mock 函数
- [x] `src/utils/runtime.ts` 已删除无使用方的 `actor` capability
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 至少一张状态页和总体评估已明确回填“actor 主线前端 mock 已退场”
