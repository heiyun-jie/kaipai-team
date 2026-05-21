# Membership 发布后检查清单

## 1. 目标

把当前 `membership` 发布后的回归检查，先固化成一套可重复执行的标准顺序：

`正式样本 -> 后台动作摘要 -> 小程序页面证据 -> blocker 判断 -> status 回填`

当前目标不是立刻补脚本化控制卡，而是先把：

- 哪一份样本是当前总包
- 发布后必须勾哪些项
- 后续如何升级到 `releaseGoNoGoCard / operatorRunCard`

全部固定下来。

## 2. 检查前置

### 2.1 运行时一致性

- 小程序、后台、后端必须确认同一环境
- 必查项：
  - `VITE_API_BASE_URL`
  - `VITE_USE_MOCK=false`
  - 后台静态资源已切到当前发布版本
  - 后端 runtime 已切到当前 jar / 容器版本
  - 当前数据库仍是样本回填时对应环境

### 2.2 当前标准入口

发布后默认从下面文件开始：

1. `evidence-bundle-index.md`
2. `real-env-evidence-pack.md`
3. 具体 `samples/*`
4. 当前统一模板：
   - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
5. 当前第一版控制卡：
   - `release-post-control-card-v1.md`

### 2.3 当前基线样本

- 正式 post-release 样本：
  - `samples/20260403-234959-dev-post-release-membership-chain/validation-report.md`
- 样本台账：
  - `samples/20260403-234959-dev-post-release-membership-chain/sample-ledger.md`
- 后台动作摘要：
  - `samples/20260403-234959-dev-post-release-membership-chain/admin-membership-template-chain-summary.md`

### 2.4 当前标准读法

membership 当前尚未产出独立自动化控制卡。

因此每次发布后默认先按下面顺序看：

1. `evidence-bundle-index.md`
2. `validation-report.md`
3. `sample-ledger.md`
4. `admin-membership-template-chain-summary.md`
5. `release-post-control-card-v1.md`
6. `release-post-control-card-template.md`

当前先把模板读法预埋为：

1. `releaseGoNoGoCard`
2. `operatorRunCard`

但在本域真正脚本化之前，仍以本清单与 `release-post-control-card-v1.md` 的人工结论为准。

## 3. 发布后标准检查顺序

### 3.1 后台会员与模板动作

优先核对：

- `admin-membership-template-chain-summary.md`

至少确认：

- 会员状态存在 `member -> none -> member`
- `after-close.reasonCodes=member_required`
- `publishLogId` 存在
- `publishVersion` 存在

### 3.2 API / DB 主样本

优先核对：

- `validation-report.md`
- `sample-ledger.md`

至少确认：

- `/api/level/info` 正常
- `/api/card/personalization` 正常
- DB 已回读：
  - `membership_account`
  - `card_scene_template`
  - `template_publish_log`
- 后台动作日志与模板发布记录一致

### 3.3 小程序页面证据

优先核对：

- `captures/mini-program-screenshot-capture.json`

至少确认页面：

- `membership`
- `actor-card`
- `actor-profile-detail`
- `invite-card`
- `fortune`

关键判定：

- 五页截图与 page-data 都存在
- `themeId / artifact / gating` 与 API 样本一致
- 五页不是旧缓存或未刷新状态

### 3.4 后台页面证据

优先核对：

- `captures/admin-screenshot-capture.json`

至少确认页面：

- `membership/accounts`
- `content/templates`
- `content/templates` rollback dialog

关键判定：

- 后台截图中的会员账户与样本用户一致
- 模板页中的 `publishLogId / templateId / sceneKey` 与样本一致

## 4. 本次发布必须勾选的核对项

### 4.1 后台动作与 API

- [ ] 会员状态变更链 `member -> none -> member` 已再次确认
- [ ] `after-close.reasonCodes=member_required` 已再次确认
- [ ] `/api/level/info` 正常
- [ ] `/api/card/personalization` 正常
- [ ] 模板发布版本号已记录
- [ ] `template_publish_log` 已回读
- [ ] `membership_account` 已回读

### 4.2 小程序页面

- [ ] `membership` 页截图正常
- [ ] `actor-card` 页截图正常
- [ ] `actor-profile-detail` 页截图正常
- [ ] `invite-card` 页截图正常
- [ ] `fortune` 页截图正常
- [ ] 对应 page-data 文件都存在
- [ ] 五页的 `themeId / artifact / 锁定状态` 与样本一致

### 4.3 后台页面

- [ ] 会员账户页截图正常
- [ ] 模板页截图正常
- [ ] rollback dialog 截图正常
- [ ] 后台截图里的 `templateId / publishLogId / status` 与样本一致

### 4.4 blocker 判断

- [ ] 当前没有新的主链 4xx / 5xx
- [ ] 当前没有新的模板发布 / 回滚异常
- [ ] 当前没有新的页面证据缺失
- [ ] 当前没有把 preview overlay 误当作后端事实源
- [ ] 当前已明确：membership 尚未产出独立 `releaseGoNoGoCard / operatorRunCard` 自动留档

## 5. 当前不能误判的点

### 5.1 不能误把当前总包当成独立控制卡

当前总包已经足够支持 membership 接入统一模板，
但它还不是本域独立自动化控制卡结果。

因此当前只能写：

- membership 已具备“可接控制卡”的条件

不能直接写：

- membership 已具备独立 `releaseGoNoGoCard / operatorRunCard`

### 5.2 不能误把 preview overlay 当成模板发布事实源

- preview overlay 当前仍是前端显式 session-only 预览态
- 不能因为页面看起来一致，就跳过后台发布与 DB 证据

## 6. 发布后回填要求

每次检查完成后，至少更新以下其一：

- `evidence-bundle-index.md`
- `status/membership-status.md`

若本次发布涉及 membership 主链、模板发布或页面恢复口径变更，必须同时更新：

- `status/membership-status.md`
- `00-28 status/overall-architecture-assessment.md`

## 7. 下一步补位方向

按优先级：

1. 先稳定 `release-post-control-card-v1.md` 的字段和值，避免在 membership 域内反复改读法
2. 再决定是否需要像 share-card 一样，把 membership 的发布后结果进一步脚本化留档
3. 若后续出现第二份正式 post-release 样本，再升级为可对比的本域控制卡基线
