# Share Card MVP 统一证据索引

本索引用于把 `share-card-mvp` 当前可复用的 **API 回归样本 / 小程序页面证据 / 后台页面证据** 收口到一个入口，避免每次发布后再从多个样本目录里手工拼接证据链。

## 1. 当前推荐基线

### 1.1 API / 治理主样本

- 样本目录：`samples/20260405-224334-dev-remote-governance-sample-v2/`
- 摘要文件：`samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
- 适用范围：
  - owner `/card/my-cards`
  - viewer `/card/personalization`
  - viewer `/card/view-histories`
  - viewer `/card/contact-requests/*`
  - admin `/admin/content/contact-requests`
  - admin `/admin/content/share-cards`
  - admin `/admin/content/share-cards/{shareCardId}`
  - admin `/admin/content/share-cards/legacy-summary`
  - admin `/admin/content/default-general-card/*`
- 当前结论：
  - `shareCardId=1`
  - `bindingConsistent=true`
  - `legacy-summary.totalPendingCount=0`
  - 当前唯一 blocker 仍是 `sendCode` 为开发态验证码

### 1.2 小程序页面证据

- 样本目录：`samples/20260405-232141-share-card-mini-program-page-evidence-v3/`
- 摘要文件：`samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
- 固定页面：
  - owner 首页
  - owner 我的名片
  - owner 卡片编辑页
  - owner 小程序卡片分享终态
  - owner 分享海报终态
  - viewer 从分享 path 再次进入小程序卡片页
  - viewer 从分享 path 再次进入分享海报页
  - owner 个人中心
  - viewer 公开名片页
  - viewer 查看历史页
- 当前结论：
  - `Unique Screenshot Hash Count=10`
  - `Visual Did Not Refresh=False`
  - 页面证据直接复用真实远端 share-card 样本上下文
  - `page-data-owner-share-action-mini-program.json` 与 `page-data-owner-share-action-poster.json` 当前已固定 `onShareAppMessage / onShareTimeline` 终态 payload
  - `page-data-viewer-shared-reentry-*.json` 当前已固定 `shared=1 / shareCardId / artifact` 回流再次进入参数

### 1.2.1 小程序阻塞样本（当前 00-68 读法）

- 样本目录：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/`
- 摘要文件：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
- 配套 preflight：`samples/20260420-161105-share-runtime-poster-page-evidence-r11-preflight/summary.md`
- 适用场景：
  - `run-share-card-mini-program-page-evidence.py` 未进入截图阶段
  - `ws://127.0.0.1:9421` 无法连接
  - 需要先判断是 DevTools 授权问题还是页面 / 脚本问题
- 当前结论：
  - 当前 page evidence 会先走内置 preflight，再决定是否进入截图链路
  - 本轮 preflight：`probeResult=devtools_auth_gate`
  - 官方 CLI replay：`登录用户不是该小程序的开发者`
  - 端口探测：`NO_LISTENER`
  - 当前 blocker 停在 DevTools 开发者授权，不在 share-card 页面实现
- 当前补充：
  - `page-evidence-result.json` 当前已显式带出 `preflightProbeResultPath`
  - `captures/devtools-auth-blocker.txt` 与 skip log 当前也已显式带出 preflight `probe-result.json` 路径
- 当前推荐读法：
  - `samples/20260420-161105-share-runtime-poster-page-evidence-r11-preflight/summary.md`
  - `captures/devtools-auth-blocker.txt`
  - `captures/devtools-cli-auto.stdout.log`
  - `captures/devtools-cli-auto.stderr.log`
  - `captures/port-check.txt`

### 1.2.2 DevTools 授权前置探针

- 样本目录：`samples/20260420-164437-share-card-devtools-auth-probe-r6/`
- 摘要文件：`samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`
- 适用场景：
  - 还没决定是否重跑整套 mini-program page evidence
  - 想先确认 `9421` automation port 与 DevTools 授权是否恢复
- 当前结论：
  - `AppID=wxd38339082a9cfa4e`
  - `probeResult=devtools_auth_gate`
  - `port-check=NO_LISTENER`
  - 当前阻塞停在 DevTools 开发者授权
- 当前补充：
  - `probe-result.json` 与 CLI stdout 当前都已显式带出 `sampleId / probeSummaryPath / resultPath / portCheckResult / cliReplay`
- 当前建议：
  - 先跑这个探针；只有探针不再返回 `devtools_auth_gate`，再继续跑 `run-share-card-mini-program-page-evidence.py`
  - `run-share-card-mini-program-page-evidence.py` 现已内置同一套 preflight；若直接执行且探针仍失败，会直接产出 blocker 样本并回链对应 preflight 摘要，而不再先进入截图阶段

### 1.3 后台页面证据

- 样本目录：`samples/20260420-152642-share-card-admin-page-evidence-v7/`
- 摘要文件：`samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
- 固定页面：
  - 联系方式申请列表
  - 联系方式申请详情
  - 分享卡治理 repair-legacy 动作截图
  - 分享卡治理列表
  - 分享卡治理详情
  - 默认普通卡治理页
- 当前补充：
  - `summary.md` 已显式输出 `Source Share Card Sample Selection / Display / Note`
  - `admin-page-evidence-result.json` 已可直接供后续脚本消费，不必只读 summary
- 当前结论：
  - 本地 vite + 远端真实 payload 抓图链已稳定
  - 分享卡治理页面当前不仅纳入截图与 `page-data` 基线，也已补到 `repair-legacy` 动作级证据

## 2. 三类证据如何一起使用

推荐按下面顺序使用：

1. 先看 `samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
   - 确认后端 runtime、治理接口、legacy-summary 是否仍为当前基线
2. 先看 `samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`
   - 确认当前是否仍卡在 DevTools 授权 / automation 端口
2.1 再看 `samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
   - 确认小程序主页面是否仍消费同一条真实链路
2.2 若 page evidence 未能产出截图，立即切到 `samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
    - 确认阻塞是否停在 DevTools 授权 / automation 端口，而不是前端页面逻辑
3. 最后看 `samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
    - 确认后台治理页 UI 与接口消费是否仍和当前治理链一致

这样可以回答三件事：

- 远端 API 是否正常
- 小程序页面是否仍连到真实链路
- 后台治理页是否仍能回看同一批数据

## 3. 当前闭环判断

### 已确认闭环的部分

- `shareCardId-only` 主链已在 API 样本中再次确认
- 分享卡治理列表 / 详情已可直接核对真实 `UserShareCard`
- `legacy-summary` 已确认清零
- 小程序主线页面已有截图与 page-data 证据
- 小程序“分享小程序 / 分享海报”终态 payload 已有 page-data 证据
- 后台关键治理页已有截图与 page-data 证据

### 尚未宣告闭环的部分

- `sendCode` 仍是开发态验证码返回
- 正式短信能力与 `sendCode` 仍未切到生产口径

## 4. 后续回归建议

每次发布后，最少更新下面三份资产中的一份：

| 场景 | 首选脚本 | 目标产物 |
|------|----------|----------|
| 后端 / 治理 API 回归 | `run-share-card-mvp-governance-sample.py` | 新的 `dev-remote-governance-sample-*` |
| 小程序 UI 回归 | `run-share-card-mini-program-page-evidence.py` | 新的 `share-card-mini-program-page-evidence` |
| 后台 UI 回归 | `run-share-card-admin-page-evidence.py` | 新的 `share-card-admin-page-evidence` |

若只是例行发布校验，优先跑 API / 治理样本；若涉及页面改动，再追加对应 UI 样本。

## 5. 当前建议的下一补位

下一轮优先补：

1. 三类证据的单目录聚合总包索引
2. `sendCode` 正式短信能力验证样本
3. 分享后真正外部回流再次进入的小程序链路证据
