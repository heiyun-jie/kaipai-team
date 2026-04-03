# 00-32 后台工作台邀请治理入口对齐 - 执行记录

> 执行日期：2026-04-03
> 范围：`kaipai-admin/src/views/dashboard/OverviewView.vue`

## 1. 本轮结论

- 工作台 referral 模块已从“异常邀请审核”升级为“邀请治理”。
- 模块内已补齐四个 referral 子入口：
  - 异常邀请
  - 邀请记录
  - 邀请资格
  - 邀请规则
- 主 CTA 仍优先指向异常邀请审核。

## 2. 落地文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`

## 3. 结构调整说明

### 3.1 模块口径

- 标题从 `异常邀请审核` 改为 `邀请治理`
- 模块说明改为：
  - 先处理风险积压
  - 再回看事实链与治理配置

### 3.2 模块入口链

在同一张 referral 模块卡内新增 quick links：

- `/referral/risk`
- `/referral/records`
- `/referral/eligibility`
- `/referral/policies`

### 3.3 其它工作台收口

- Hero 提示从“邀请异常”调整为“邀请治理”
- `异常邀请待处理` 指标卡保留，继续作为风险积压信号

## 4. 交互边界确认

- 未新增 dashboard API 字段
- 未修改 recent items 路由逻辑
- 未改动 referral 四个子页面本身

## 5. 验证结果

- 已执行：`cd kaipai-admin && npm run build`
- 结果：通过
- 保留告警：
  - Vite chunk size warning
  - Sass legacy JS API deprecation warning

本轮未新增阻塞错误。
