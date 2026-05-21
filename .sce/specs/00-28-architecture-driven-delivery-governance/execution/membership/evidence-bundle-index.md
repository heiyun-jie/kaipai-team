# Membership 发布回归总包索引

本文件是 `membership` 当前发布回归的总入口。

与 `real-env-evidence-pack.md` 的区别：

- `real-env-evidence-pack.md` 偏向“证据面应该看什么”
- 本文件偏向“当前这轮 membership 发布后，应该按什么顺序看哪一包证据”

## 1. 当前推荐总包

### 1.1 正式 post-release 样本

- 样本：
  - `samples/20260403-234959-dev-post-release-membership-chain/`
- 样本摘要：
  - `samples/20260403-234959-dev-post-release-membership-chain/validation-report.md`
- 样本台账：
  - `samples/20260403-234959-dev-post-release-membership-chain/sample-ledger.md`
- 当前关键结论：
  - `membershipTier` 已在同一样本里验证 `member -> none -> member`
  - `after-close.reasonCodes=member_required`
  - `publishLogId=26`
  - `publishVersion=SMOKE_V2_ADMIN_20260403_235012`
  - 同一样本已同时并入：
    - 后端 API
    - DB 查询
    - 后台 UI 截图
    - 小程序 5 页截图与 page-data

### 1.2 后台动作摘要

- 文件：
  - `samples/20260403-234959-dev-post-release-membership-chain/admin-membership-template-chain-summary.md`
- 用途：
  - 快速回看“会员账户变更 + 模板发布 / 回滚”的后台动作链

### 1.3 页面与运行时补充

- 证据规范：
  - `real-env-evidence-pack.md`
- 运行时前置：
  - `real-env-runtime-inventory.md`
- 发布后人工勾检：
  - `release-post-checklist.md`
- 第一版控制卡：
  - `release-post-control-card-v1.md`

## 2. 当前发布后读法

membership 当前还没有像 share-card 那样产出独立自动化 `releaseGoNoGoCard / operatorRunCard`。

因此当前标准读法先固定为：

1. `evidence-bundle-index.md`
2. `release-post-checklist.md`
3. `samples/20260403-234959-dev-post-release-membership-chain/validation-report.md`
4. `samples/20260403-234959-dev-post-release-membership-chain/sample-ledger.md`
5. `release-post-control-card-v1.md`
6. `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

其中第 5 份不是当前 membership 已产出的结果卡，而是：

- 之后把 membership 升级成正式控制卡时必须复用的结构模板
- 默认第一读法必须保持为：`releaseGoNoGoCard -> operatorRunCard`

## 3. 当前总包回答的问题

这份总包当前可以直接回答：

### 3.1 后台会员变更与模板发布后，前台有没有一起变化

可以回答。

因为当前正式样本已经同时保留：

- 后台会员账户截图
- 后台模板页与 rollback dialog 截图
- `level.info / card.personalization`
- 小程序 `membership / actor-card / detail / invite / fortune` 五页截图和 page-data

### 3.2 模板发布 / 回滚是否已形成成组证据

可以回答。

因为当前样本已固定：

- 发布版本号
- 回滚 / 恢复动作
- 对应后台页面
- 对应前台摘要与页面恢复

### 3.3 当前是否已经适合接入统一发布后控制卡模板

可以回答。

当前结论是：

- `membership` 已经具备“后端 API + DB + 后台 UI + 小程序页面”同包证据
- 已具备接入统一模板的前置条件
- 但当前仍未生成本域独立 `releaseGoNoGoCard / operatorRunCard`

## 4. 当前总包仍未覆盖的点

当前总包还没有覆盖：

1. membership 域自己的自动化 `releaseGoNoGoCard / operatorRunCard`
2. preview overlay 被提升为更强事实源之前的发布后自动判定
3. 脱离 `dev + Nacos` 运行时的额外环境样本

因此当前总包能证明：

- 主链证据已经同包
- membership 已达到“可接控制卡”的成熟度

但还不能证明：

- membership 已完成独立控制卡自动留档

## 5. 与其它文档的关系

- 执行目录入口：
  - `README.md`
- 证据面说明：
  - `real-env-evidence-pack.md`
- 本文件：
  - `evidence-bundle-index.md`
- 当前发布后人工勾检：
  - `release-post-checklist.md`
- 当前第一版控制卡：
  - `release-post-control-card-v1.md`
- 后续统一控制卡模板：
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

## 6. 下一步接位建议

按优先级：

1. 先用 `release-post-control-card-v1.md` 固定 membership 当前人工 Go/No-Go 读法
2. 再按统一模板把 membership 提升为独立 `releaseGoNoGoCard / operatorRunCard`
3. 后续若有第二份正式样本，再把当前总包升级为自动对比两个发布版本的控制卡输入
