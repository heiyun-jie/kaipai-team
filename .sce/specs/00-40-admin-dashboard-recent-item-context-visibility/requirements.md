# 00-40 后台工作台最近事项上下文可见化（Admin Dashboard Recent Item Context Visibility）

> 状态：进行中 | 优先级：P1 | 依赖：00-39 admin-dashboard-recent-item-precise-filter-routing
> 记录目的：让目标页显式说明“当前筛查来自工作台最近事项”，并允许运营一键清空上下文。

## 1. 背景

`00-39` 已让最近事项点击后可以把精确筛查字段带到目标页，但页面本身还没有说明这些筛查条件来自哪里。

结果是运营进入目标页后容易误判为：

- 这是自己手动筛出来的结果
- 页面默认就只有这些记录

工作台最近事项是“带上下文进入”的处理流，目标页必须把这层上下文显示出来，并允许一键退出该上下文。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`

### 2.2 本轮不处理

- 模块入口来源可见化
- 详情抽屉自动打开
- 后端接口变更

## 3. 需求

### 3.1 来源标记

- **R1** dashboard 最近事项跳转时，必须带上可识别的来源标记。
- **R2** 目标页必须根据来源标记识别“当前筛查来自工作台最近事项”。

### 3.2 页面提示

- **R3** 目标页必须显式展示当前为“工作台最近事项上下文”。
- **R4** 页面提示应概括当前自动带入的筛查条件。
- **R5** 页面提示不得与页面原有筛选说明混淆成普通静态文案。

### 3.3 清空上下文

- **R6** 目标页必须提供一键清空上下文的动作。
- **R7** 清空上下文后，应移除来源标记及其携带的 query，并回到目标页默认筛查状态。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 最近事项跳转已带来源标记
- [ ] 目标页已显式展示“来自工作台最近事项”的上下文提示
- [ ] 可一键清空上下文并恢复默认状态
- [ ] `npm run build` 在 `kaipai-admin` 通过
