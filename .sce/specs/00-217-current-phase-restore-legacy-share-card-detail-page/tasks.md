# 恢复 1.0 分享落地页并接入首页模板区跳转 - 任务清单

_Requirements: ALL_
_Design: ALL_

> 2026-08-13 完成并构建核验。门禁：`vue-tsc` 0、`build:mp-weixin` EXIT=0、`verify:nav-title` 97/97、`verify:actor-card-attachment` 17/17、`dist/build` ↔ `dist/dev` 双侧产物核对通过。

## T1 从 git 找回分享落地页与依赖（Requirements 3.1）

从 `27d3bef^` 恢复 14 个文件（清单见 design §1），`src/api/card.ts` 为新建（`GET /api/card/my-cards`）。恢复后 `vue-tsc` 迭代补齐缺失模块（`types/share-card-favorite`、`utils/personalization`、`api/personalization`、`utils/share-artifact`），最终 0 报错。

**Validates: Requirements 3.1**

## T2 注册路由（Requirements 3.1）

`src/pages.json` `pkg-card` 分包追加 `ai-profile-card-detail/index`（navigationStyle: custom，照 00-209 前原配置）。

**Validates: Requirements 3.1**

## T3 首页模板区跳分享页（Requirements 3.2）

`src/pages/home/index.vue`：模板卡片 `@click` 改 `goShareCard`；实现取首张分享卡跳 `/pkg-card/ai-profile-card-detail/index?shareCardId={id}&shared=1`；无卡 / 未登录 / 失败均有提示；删除 `goCreateWithStyle`。

**Validates: Requirements 3.2**

## T4 后端接口确认（Requirements 3.3）

核实 `SecurityConfig` 白名单已含 `/card/personalization`、`/card/config`、`/ai/profile-card/share-cards/*/artifact`（观看者未登录可访问）——**后端零改动**。

**Validates: Requirements 3.3**

## T5 构建与产物核对

`vue-tsc` 0；`npm run build:mp-weixin` EXIT=0；核对双层产物：`pkg-card/ai-profile-card-detail/index.{js,wxml}` 存在、`app.json` 含新路由、`pages/home/index.js` 含 `ai-profile-card-detail` 跳转且无 `goCreateWithStyle` 残留、`api/card.js` 含 `my-cards`。

**Validates: Requirements 4, 7**

## T6 文档同步

- `.sce/specs/README.md` 注册 00-217。
- `CURRENT_CONTEXT.md`「分享面」章节更新：1.0 分享落地页已恢复（`00-217`），首页模板区跳分享页；分享出口（`onShareAppMessage`）仍未恢复。

**Validates: Requirements 7**
