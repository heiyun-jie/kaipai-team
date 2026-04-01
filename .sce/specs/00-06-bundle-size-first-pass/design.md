# 首批减体积优化 - 技术设计

_Requirements: 00-06 全部_

## 1. 设计思路

本轮不直接碰业务逻辑，而是先处理“聚合导出导致的额外公共模块”。

当前现象：

- 多个页面通过 `@/components` 引入共享组件
- 构建产物存在 `dist/build/mp-weixin/components/index.js`
- 该文件本质上承担了组件聚合层，属于可收敛的附加产物

因此本轮策略为：

- 将所有 `@/components` 引用改成具体组件文件路径
- 若不再存在依赖，则删除 `src/components/index.ts`
- 使用构建产物验证聚合文件是否消失

## 2. 接入范围

优先处理当前所有命中的 barrel 使用点：

- `pages/apply-confirm/index.vue`
- `pages/actor-card/index.vue`
- `pages/video-player/index.vue`
- `pages/actor-profile/edit.vue`
- `pages/actor-profile/detail.vue`
- `pages/my-applies/index.vue`
- `pages/membership/index.vue`
- `pages/mine/index.vue`
- `pages/home/index.vue`

## 3. 非目标

- 本轮不处理 mock 体系拆分
- 本轮不处理页面分包迁移
- 本轮不处理 Sass 弃用告警
