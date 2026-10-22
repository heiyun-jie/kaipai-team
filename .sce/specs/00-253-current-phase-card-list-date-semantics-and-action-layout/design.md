# 名片夹日期语义与操作区布局收口 - 技术设计

## 1. 影响范围

- 页面：`kaipai-frontend/src/pages/card-list/index.vue`
- 门禁：`kaipai-frontend/scripts/verify-00253-card-list-layout.mjs`
- 构建产物：`kaipai-frontend/dist/dev/mp-weixin/pages/card-list/index.{js,wxml,wxss}`

不修改后端、数据库、路由、API DTO 和公开分享页。

## 2. 日期事实源

新增页面内纯函数：

```text
published -> publishedAt || lastUpdate -> 发布于...
draft     -> lastUpdate                -> 更新于...
```

日期通过 `Date#getFullYear/getMonth/getDate` 组装中文文案，避免运行时区域格式把日期重新输出成裸 `9/2`。当前年份省略年份，跨年补齐年份。

## 3. 模板结构

```text
card
├── card-main
│   ├── card-cover
│   └── card-info
│       ├── card-title
│       ├── draft progress（仅草稿）
│       └── card-meta
├── card-actions
│   └── ops--published / ops--draft
└── delete-error（按需）
```

删除卡片内重复状态标签。卡片上层保留整体点击行为；操作项继续使用 `.stop`。

## 4. 样式策略

- `card` 从单层横向 Flex 改为块级容器。
- `card-main` 承担封面与信息区的横向布局。
- 封面固定 `112rpx x 112rpx`，信息区 `min-width: 0`。
- `card-actions` 使用顶部浅分隔线，与信息区建立层级。
- 已发布操作栏使用三列等宽 Grid，草稿使用两列等宽 Grid。
- 操作项固定 `64rpx` 高度、单行文本，分享按钮占满网格单元。
- 删除失败信息使用正常文档流，避免覆盖操作栏。

## 5. 发版兼容

- 前端只消费后端已存在的 `publishedAt` 与 `lastUpdate`，没有新增接口字段。
- `publishedAt` 为空时回退 `lastUpdate`，兼容历史已发布卡。
- 不改变分享、复制、删除和导航请求，因此旧后端可继续工作。
- 源码变化会使当前测试 Candidate 失效，完成后必须重新走候选冻结与准入，不能冒用旧 Candidate。

## 6. 验证

1. `npm run type-check`
2. `npm run verify:card-list-layout`
3. `npm run build:mp-weixin`
4. 再次执行 `npm run verify:card-list-layout`
5. 核对固定 `dist/dev` 的 WXML/WXSS/JS 和 scoped hash
