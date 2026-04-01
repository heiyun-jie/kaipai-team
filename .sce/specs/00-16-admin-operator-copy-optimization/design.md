# 00-16 设计说明

## 1. 设计原则

- 保留现有后台结构与视觉，不做布局重构
- 通过“标题 + 一句话说明 + 状态标签”传达运营任务
- 技术路径仅保留在代码和文档中，不作为页面主要可见文案

## 2. 文案收敛策略

### 2.1 顶部区域

- 顶部状态提示从“链路已接通”改为“后台服务正常 / 当前可处理运营事务”
- 通用副标题从“统一收口接口/权限”改为“查看数据、执行操作、处理待办”

### 2.2 工作台

- 工作台描述突出“今日待办、风险项、最近事项”
- 模块卡片说明聚焦“可以做什么”
- 状态标签改成运营可读状态

### 2.3 通用业务页

- 页面说明统一描述该页承担的业务动作
- 筛选区说明只保留对运营有帮助的筛选提示

## 3. 影响文件

- `kaipai-admin/src/components/layout/AdminTopbar.vue`
- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/auth/LoginView.vue`
- `kaipai-admin/src/views/shared/PlaceholderView.vue`
- 其他命中接口导向文案的后台页面
