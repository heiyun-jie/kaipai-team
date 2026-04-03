# 00-32 设计说明

## 1. 设计原则

- 工作台负责呈现治理入口链，不负责复制子页面全部信息
- 保持“单卡总览 + 快速入口”结构，避免拆成多个分散卡片
- 待处理信号仍以异常邀请积压作为优先级锚点

## 2. 设计策略

### 2.1 referral 模块改造

把原模块：

- 标题：`异常邀请审核`
- 动作：`进入异常邀请`

调整为：

- 标题：`邀请治理`
- 文案：强调风险复核、记录核查、资格发放、规则维护属于同一治理链
- 主 CTA：继续指向 `/referral/risk`

### 2.2 快速入口链

在 referral 模块内部增加 quick links：

- `/referral/risk`
- `/referral/records`
- `/referral/eligibility`
- `/referral/policies`

展示形态为同卡片内的胶囊式入口按钮。

### 2.3 其它工作台模块

- `VERIFY / MEMBERSHIP / CONTENT` 保持现状
- 不新增新的 dashboard 模块数据结构来源，只在前端模块配置层扩展 `quickLinks`

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
