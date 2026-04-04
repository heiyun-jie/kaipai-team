# 00-52 当前阶段邀请记录页边界对齐（Current Phase Invite Record Page Boundary Alignment）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-48 current-phase-wechat-capability-deferral，05-12 share-invite-code-consolidation
> 记录目的：把 invite 当前阶段真实产品边界从“前台邀请码/海报/分享唯一操作页”校正为“邀请记录页 + 登录承接邀请码 + 分享入口留在 actor-card/membership”，并把 personalization runtime 与偏好保存口径一起收口到当前阶段两种分享产物，避免 spec 与代码继续分叉。

## 1. 背景

当前仓内已经出现一条明确偏差：

- `kaipai-frontend/src/pkg-card/invite/index.vue` 现状只保留邀请记录与状态展示
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 与 `src/pkg-card/membership/index.vue` 当前承担分享入口与邀请记录入口
- `05-12-share-invite-code-consolidation/*` 仍把 `pkg-card/invite/index` 描述为“邀请码 / 邀请链接 / 海报 / 分享给好友 / 邀请记录”的唯一前台操作页

如果不先把这层边界校正，后续 `00-28` 的状态卡、路线图、样本结论和分享主线清理会继续被旧口径误导。

## 2. 范围

### 2.1 本轮必须处理

- `00-28` 路线图、invite 状态卡、总体评估、invite 切片
- `05-12` 的 requirements / design / tasks / execution 顶部口径
- spec 索引与映射
- `/api/card/personalization` 当前阶段分享产物返回口径
- 偏好保存链路中 `preferredArtifact` 的当前阶段归一化
- 前端个性化类型与分享产物 helper 的当前阶段口径同步

### 2.2 本轮不处理

- 删除后端 `/api/invite/code`、`/api/invite/qrcode` 等已上线接口
- 删除历史样本目录里的 `inviteCard` / `publicCardPage` 证据
- 在 invite 以外的全部运行时链路里立即清空所有历史兼容字段
- 重新定义未来微信 `wxacode` 批次

## 3. 需求

### 3.1 当前阶段边界校正

- **R1** 当前阶段文档不得再把 `pkg-card/invite/index` 写成“邀请码、链接、海报、分享唯一操作页”。
- **R2** 当前阶段 invite 前台边界应改写为：
  - `pages/login/index` 承接 `inviteCode / scene`
  - `pkg-card/actor-card/index` 与 `pkg-card/membership/index` 承担分享入口
  - `pkg-card/invite/index` 当前只承担邀请记录与状态查看
- **R3** 当前阶段 invite 验收应以“注册绑定、记录生成、资格链、后台治理、记录页可验证”作为主口径，不再把旧版 invite 分享页能力当成当前阶段必达项。

### 3.2 历史兼容与未来批次

- **R4** 历史 `inviteCard` / `publicCardPage` / 邀请码分享页口径可以保留为兼容事实或历史样本，但必须明确它们不再代表当前阶段产品承诺。
- **R5** 微信官方 `wxacode` 继续由 `00-48` 保留为后续能力批次，不得重新混回当前阶段 invite 页面边界。

### 3.3 治理回填

- **R6** 必须通过独立 Spec 固化本次边界修正，不得只在状态卡里口头说明。
- **R7** 必须同步更新 `00-28` 和 `05-12`，保证后续读文档的人能直接定位“当前阶段 invite 到底验什么”。

### 3.4 Runtime 与保存口径收口

- **R8** 当前阶段 `/api/card/personalization` 返回的 `artifacts` 必须只暴露 `miniProgramCard` 与 `poster` 两种分享产物，不得继续把 `publicCardPage`、`inviteCard` 作为当前阶段分享产物返回给前端。
- **R9** 当前阶段保存名片偏好时，`preferredArtifact` 必须归一化到 `miniProgramCard / poster`，不得把 legacy artifact 重新写回偏好表并在下一次读取时回灌前端。
- **R10** 前端 `personalization` 类型、helper 与 runtime 解析必须与当前阶段两种分享产物口径一致；公开名片页路径可保留为独立 helper，但不得继续作为当前阶段 artifact 类型暴露。

## 4. 验收标准

- [x] 已新增独立 `00-52` Spec 并登记索引与映射
- [x] `00-28` 路线图、invite 状态卡、总体评估与 invite 切片已对齐“记录页边界”
- [x] `05-12` 已显式标记为历史收口 Spec，当前阶段以 `00-52` 为准
- [x] 当前阶段 invite 口径已明确区分“记录页验收面”与“未来微信能力批次”
- [x] `/api/card/personalization` 已收口为当前阶段两种分享产物
- [x] 名片偏好保存已归一化 `preferredArtifact`，不会把 legacy artifact 写回数据库
- [x] 前端 `personalization / share-artifact` 当前阶段口径已与后端一致
