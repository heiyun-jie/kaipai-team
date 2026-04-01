# 00-18 设计说明

## 1. 设计原则

- 优先改共用壳层，减少逐页散落样式
- 保持当前后台暖色品牌基调
- 用统一的圆角、阴影、分区边界和按钮节奏建立整体一致性

## 2. 设计策略

### 2.1 页头

- `PageContainer` 升级为统一页头面板
- 标题、说明和操作按钮保持稳定的主次关系

### 2.2 筛选区

- `FilterPanel` 升级为浅浮层工具区
- 操作按钮与筛选表单分开，保证查询动作显眼

### 2.3 主卡与详情区

- 统一 `.table-card`、`.detail-card`、`.detail-block`、`.pager` 等样式语言
- 让业务页通过现有类名直接继承统一视觉表现

## 3. 影响文件

- `kaipai-admin/src/components/business/PageContainer.vue`
- `kaipai-admin/src/components/business/FilterPanel.vue`
- `kaipai-admin/src/styles/index.scss`
