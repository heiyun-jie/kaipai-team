# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-03-23

## 00 — 全局基础

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 00-01 global-style-system | `src/styles/_tokens.scss` | — | ✅ 已实现 |
| | `src/styles/_mixins.scss` | — | ✅ 已实现 |
| | `src/styles/_page-layout.scss` | — | ✅ 已实现 |
| | `src/styles/_reset.scss` | — | ✅ 已实现 |
| | `src/styles/index.scss` | — | ✅ 已实现 |
| | `src/uni.scss` | — | ✅ 已实现 |
| 00-02 shared-components | `src/components/Kp*.vue`（19 个） | 1,612 | ✅ 已实现 |
| 00-03 shared-utils-api | `src/types/*.ts`（7 个） | — | ✅ 已实现 |
| | `src/utils/*.ts`（7 个） | — | ✅ 已实现 |
| | `src/stores/user.ts` | — | ✅ 已实现 |
| | `src/api/*.ts`（6 个） | — | ✅ 已实现 |

## 01 — 公共页面

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 01-01 page-login | `src/pages/login/index.vue` | 526 | ✅ 已实现 |
| 01-02 page-role-select | `src/pages/role-select/index.vue` | 222 | ✅ 已实现 |

## 02 — 首页

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 02-01 page-home-actor | `src/pages/home/index.vue`（演员视角） | 1,030 | ✅ 已实现 |
| 02-02 page-home-crew | `src/pages/home/index.vue`（剧组视角） | 同上 | ✅ 已实现 |

## 03 — 演员端页面

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 03-01 page-role-detail | `src/pages/role-detail/index.vue` | 600 | ✅ 已实现 |
| 03-02 page-apply-confirm | `src/pages/apply-confirm/index.vue` | 677 | ✅ 已实现 |
| 03-03 page-my-applies | `src/pages/my-applies/index.vue` | 568 | ✅ 已实现 |
| 03-04 page-actor-profile-edit | `src/pages/actor-profile/edit.vue` | 1,417 | ✅ 已实现 |
| 03-05 page-mine | `src/pages/mine/index.vue` | 584 | ✅ 已实现 |

## 04 — 剧组端页面（代码保留，业务主线已迁移后台）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 04-01 page-project-create | `src/pages/project/create.vue` | 695 | ✅ 已实现 |
| 04-02 page-role-create | `src/pages/project/role-create.vue` | 981 | ✅ 已实现 |
| 04-03 page-apply-manage | `src/pages/apply-manage/index.vue` | 580 | ✅ 已实现 |
| 04-04 page-actor-profile-detail | `src/pages/actor-profile/detail.vue` | 72 | ⚠️ 薄实现，待增强 |
| 04-05 page-company-profile-edit | `src/pages/company-profile/edit.vue` | 1,094 | ✅ 已实现 |

## 无独立 Spec 页面

| 源文件 | 行数 | 说明 |
|--------|------|------|
| `src/pages/video-player/index.vue` | 27 | 视频播放工具页 |
| `src/pages/webview/index.vue` | 589 | 内嵌网页容器 |
| `src/pages/apply-detail/index.vue` | 496 | 申请详情页 |

## 05 — 演员增强功能（Spec 已建，代码未完整落地）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 05-01 actor-card | `src/pages/actor-card/index.vue` | — | 📋 未创建 |
| | `src/pages/actor-profile/detail.vue`（公开落地页改造目标） | 72 | ⚠️ 目标页未完成改造 |
| 05-02 actor-profile-enhance | `src/pages/actor-profile/edit.vue`（增强目标页） | 1,417 | ⚠️ 现状为单页实现，未完成拆分增强 |
| | `src/types/actor.ts`（扩展字段） | — | ⚠️ 待扩展 |
| 05-03 credit-score | `src/pages/credit-score/index.vue` | — | 📋 未创建 |
| | `src/pages/credit-record/index.vue` | — | 📋 未创建 |
| | `src/pages/credit-rank/index.vue` | — | 📋 未创建 |
| | `src/types/credit.ts` | — | 📋 未创建 |
| | `src/api/credit.ts` | — | 📋 未创建 |
| | `src/components/KpCreditBadge.vue` | — | 📋 未创建 |
| | `src/components/KpLevelTag.vue` | — | 📋 未创建 |

## 关注项

- `pages/actor-profile/detail.vue` 仍过薄，既不满足剧组详情页的完整展示，也未达到 05-01 公开落地页的目标
- `pages/actor-profile/edit.vue` 仍是大文件，05-02 的拆分与增强尚未落地
- `video-player / webview / apply-detail` 目前仍无独立 Spec，如继续演进应补建或并入既有 Spec
- Phase 05 规划页尚未进入 `pages.json`，当前实现仍以 V1 主链路为准
