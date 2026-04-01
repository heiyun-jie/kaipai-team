# 小程序包体治理 - 技术设计

_Requirements: 00-05 全部_

## 1. 总体策略

本轮先建立“治理基线”，再做“真实迁移”。

原因：

- 当前 `mp-weixin` 构建产物总体积尚未逼近 2MB，立即大规模改路由收益有限，风险更高
- 当前主线仍在持续重构，先沉淀可重复执行的审计机制，后续每轮都能基于真实数据决策
- 包体治理不是一次性动作，应该具备持续检查能力

## 2. 审计设计

新增脚本：

```powershell
kaipai-frontend/scripts/audit-mp-package.ps1
```

输入：

- `dist/build/mp-weixin/app.json`
- `dist/build/mp-weixin/**`

输出：

- 主包体积
- 各分包体积
- 总构建体积
- 阈值比较结果

规则：

- 若 `app.json` 无 `subPackages` / `subpackages`，则视为“全部仍在主包”
- 若存在分包，则按 `root` 前缀匹配文件归属
- 默认阈值为 2MB，可通过参数覆盖
- 任一包超限则脚本 `exit 1`

## 3. 迁移边界

当前页面分为三类：

### 3.1 主包保留

- `pages/login/index`
- `pages/role-select/index`
- `pages/home/index`
- `pages/mine/index`

原因：

- 启动即达
- tab 页
- 主链路入口

### 3.2 第一批候选迁移

- `pages/actor-card/index`
- `pages/membership/index`
- `pages/webview/index`
- `pages/video-player/index`

原因：

- 非 tab
- 入口明确
- 与名片、会员、工具能力相关，天然适合独立收口

### 3.3 第二批候选迁移

- `pages/role-detail/index`
- `pages/apply-confirm/index`
- `pages/my-applies/index`
- `pages/apply-detail/index`
- `pages/actor-profile/edit`
- `pages/actor-profile/detail`
- `pages/project/create`
- `pages/project/role-create`
- `pages/apply-manage/index`
- `pages/company-profile/edit`

原因：

- 均为深入链路页或后台残留页
- 迁移时会涉及更多历史路径和联动页面，适合在审计基线稳定后处理

## 4. 非目标

- 本轮不强制完成全部页面分包迁移
- 本轮不调整现有业务功能和文案
- 本轮不处理 Sass 弃用告警

## 5. 长期执行规则

后续功能开发默认按以下顺序判断：

1. 该功能是否为启动即达或 tab 主入口依赖
2. 该功能是否可以作为独立业务模块访问
3. 该功能是否会持续增长脚本、图片、海报、协议页或复杂 UI

决策口径：

- 若答案偏向 2 / 3，则优先新建独立分包
- 若答案偏向 1，则允许留在主包
- 不能因为开发方便就默认继续堆主包
