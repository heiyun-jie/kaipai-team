# 会员与模板真实环境闭环验证清单

## 1. 目标

把当前“局部完成”的 membership 链路，收口成一条可重复验证的真实环境样本链：

`后台会员开通 / 模板发布 -> 后端摘要输出 -> membership / actor-card / detail / invite / fortune 同步变化`

## 2. 验证前置

### 2.1 运行时确认

- 小程序、后台、后端必须确认同一环境
- 必查项：
  - profile
  - 反向代理
  - `VITE_API_BASE_URL`
  - `VITE_USE_MOCK`
  - 数据库目标环境

### 2.2 账号与样本

- 准备 1 个基础演员样本
- 准备 1 个会员演员样本
- 准备 1 个模板发布样本
- 准备 1 个模板回滚样本
- 准备 1 个后台账号：至少具备会员产品、会员账户、模板管理权限
- 准备 1 个微信开发者工具登录账号：必须是目标小程序 `appid` 的开发者，否则不能把页面编译成功误判成“可截图、可自动化”

### 2.3 记录规范

- 每次验证必须固定记录：
  - 环境名
  - actorUserId
  - membershipAccountId
  - templateId
  - publishLogId
  - sceneKey
- 每次至少保留 4 类证据：
  - 小程序页面截图
  - 后台页面截图
  - API 响应
  - DB 查询结果
- 如果小程序截图因运行时授权或 DevTools 账号问题无法生成，必须额外补一份阻塞证据：
  - `cli auto` / `preview` 直接输出
  - DevTools `WeappLog`
  - 目标 `appid`
  - 自动化端口是否实际监听
  - 若怀疑旧缓存干扰，再对同一份 dist 复制到全新路径重放一次 `cli auto`

## 3. 主链路验证

### 3.1 后台开通会员

- 后台入口：
  - `/membership/accounts`
- 需要确认：
  - 会员状态已变更
  - 日志可追溯
  - 小程序侧 `membershipTier / shareCapability` 同步变化

### 3.2 后台发布模板

- 后台入口：
  - `/content/templates`
- 需要确认：
  - 发布动作成功
  - `template_publish_log` 有记录
  - 小程序 `actor-card / detail / invite / fortune` 恢复最新模板 / 主题 / artifact

### 3.3 后台回滚模板

- 后台入口：
  - `/content/templates`
- 需要确认：
  - 回滚动作成功
  - 前台恢复到指定版本表现
  - 发布日志与操作日志一致

### 3.4 小程序恢复链

- 页面：
  - `pkg-card/membership`
  - `pkg-card/actor-card`
  - `pages/actor-profile/detail`
  - `pkg-card/invite`
  - `pkg-card/fortune`
- 需要确认：
  - 页面都优先消费同一份 personalization / level 摘要
  - 会员能力 gating 口径一致
  - 主题、artifact path、template 恢复一致

### 3.5 编辑态 overlay

- 需要确认：
  - 未保存 preview overlay 只作为显式前端编辑态存在
  - 它不会覆盖后台已发布模板作为主事实源

## 4. 判定标准

### 4.1 仍只能判定“局部完成”

满足以下任一条，即不能宣告 membership 闭环完成：

- 没有同一样本链的真实环境证据
- 后台开通会员后，小程序 `membership / actor-card / detail / invite / fortune` 没同步变化
- 后台发布 / 回滚模板后，前台恢复不一致
- 前台仍需依赖本地完整 resolver 才能恢复主链
- preview overlay 继续被误当作主事实源

### 4.2 可以升级为“闭环完成”

- 会员开通 / 延期 / 关闭链路真实走通
- 模板发布 / 回滚链路真实走通
- 小程序 5 个主页面恢复结果一致
- 后台、接口、数据库三端口径一致

## 5. 回填模板

每次验证结束后，按下面结构回填到 `status/membership-status.md`：

```md
### YYYY-MM-DD（联调回填）

- 当前判定：`局部完成` / `闭环完成`
- 样本：
  - actorUserId:
  - membershipAccountId:
  - templateId:
  - publishLogId:
- 已确认：
  - 
- 未确认：
  - 
- 缺陷归因：
  - 前端：
  - 后端：
  - 后台：
```
