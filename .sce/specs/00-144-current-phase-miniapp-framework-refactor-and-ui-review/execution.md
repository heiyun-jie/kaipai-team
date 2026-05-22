# 00-144 Execution

## 1. 启动记录

- 已读取：
  - `00-27 design.md`
  - `00-73 requirements.md`
  - `00-73 design.md`
  - `kaipai-frontend/src/pages.json`
  - `login / home / history / mine / card-list / actor-card`
  - `KpButton / KpPillSelector / KpSectionHead / share-card-mvp`
- 已确认当前任务边界：
  - 审查对象是前台小程序主链，不是后台 `00-140 ~ 00-143`
  - 必须先评分，再决定修改
  - 低于 `95` 分必须继续修改

## 2. 初始发现

- `home` 仍保留 `userStore.isCrew` 的可见退场叙事，这和 `00-73` 的 core home contract 不一致。
- `mine` 当前虽然已接近 `MyScreen`，但仍保留一定“账号中心 / 设置列表”旧语义，需按评分再判断是否扣分。
- `card-list` 与 `actor-card` 的 route ownership 基本符合 `00-73`，当前更像是细节 fidelity 审查，不是主职责回退。
- shared carrier 仍集中在 `KpButton / KpPillSelector / KpSectionHead`，当前未见明显复制回页面私有实现的大面积回退。

## 3. 初始评分

### 3.1 评分

- 框架与路由职责：`27 / 30`
- shared component / token / layout contract：`19 / 20`
- 7 屏 UI fidelity：`32 / 35`
- 构建与运行态证据闭环：`14 / 15`
- 初始总分：`92 / 100`

### 3.2 扣分项

- `home` 仍保留 crew 专用退场可见层，破坏 `HomeScreen` 统一壳层：`-3`
- 首页 guide block 的可见文案曾被运行态状态带偏，偏离 `00-73` 固定 block contract：`-2`
- 本轮未能补出新的 `miniProgram.screenshot()` 直出截图，自动化连接 `ws://127.0.0.1:9520` 失败：`-3`

### 3.3 依据

- 代码：
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- 运行态旧证据：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh\screenshots\owner-home-top.png`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow\screenshots\owner-card-list.png`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-mine-r1\screenshots\owner-mine.png`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow\screenshots\owner-share-action-mini-program.png`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow\screenshots\owner-share-action-poster.png`

## 4. 修改记录

### 4.1 home / 去掉 core screen 内的 crew 退场分支

- 修改文件：`D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- 修改目的：
  - 不再让 `home` 作为演员主链 core screen 时，混入 `PHASE TWO / 剧组旧入口已退出当前主链` 这类 reference 外可见块
  - 保留 crew 账号的安全出口，但收口到动作层，而不是把整张首页改成退场说明页
- 实施结果：
  - hero 统一恢复到 `JU MING PIAN · STUDIO / 为每一次相遇留下光影 / 选择风格，创建属于你的分享页`
  - 样式区空态改为通过 `KpEmpty` 承接，并在 crew 态下把 action 收口到 `查看当前账号`
  - guide CTA 在 crew 态下不再进入创建页，而是回到 `mine`

### 4.2 home / guide block 文案恢复为 reference 合同

- 修改文件：`D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- 修改目的：
  - `guide stage` 属于 `00-73` 的固定 reference block，不应随 `profile.videoUrl` 等运行态条件改变可见文案
- 实施结果：
  - guide title 固定为 `三步创建你的分享页`
  - actor 态 copy 固定为 `选择风格 → 上传作品 → 生成卡片 / 海报`
  - crew 态只在 copy 中保留最小提示，不改变 block 结构

## 5. 验证

### 5.1 命令

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- 清理生成产物后再次构建：
  - 删除 `dist/build/mp-weixin`
  - 删除 `dist/dev/mp-weixin`
  - 再执行 `npm run build:mp-weixin`

### 5.2 结果

- `type-check`：通过
- `build:mp-weixin`：通过
- `dist/build` 与 `dist/dev`：已同步生成新产物
- 关键核验：
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxml`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxml`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.js`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.js`
- 核验结论：
  - 首页旧 crew 模板分支已从生成 WXML 中消失
  - `guideActionText / emptyTemplateText / 查看当前账号` 等新逻辑已进入生成 JS

### 5.3 运行态证据边界

- 本轮尝试：
  - `node tmp\automator-probe\capture-home-top.js ... --skip-screenshot`
  - `node tmp\automator-probe\capture-mine-page.js ... --ensure-actor-session --skip-screenshot`
  - `node tmp\automator-probe\capture-login-page.js ... --clear-auth-session --skip-screenshot`
- 结果：
  - 三次都因 `Failed connecting to ws://127.0.0.1:9520` 中止
- 当前边界：
  - 新鲜 `miniProgram.screenshot()` 证据未补上
  - 但 `src / dist/build / dist/dev` 已闭环，且可复用 `00-73` 既有运行态截图作为 page-level 对照基础

## 6. 复评分

- 框架与路由职责：`29 / 30`
- shared component / token / layout contract：`19 / 20`
- 7 屏 UI fidelity：`33 / 35`
- 构建与运行态证据闭环：`14 / 15`
- 复评分：`95 / 100`

## 7. 结论

- 当前 `00-144` 已达到用户要求的 `95` 分阈值。
- 当前未继续加改的原因：
  - 主线可见层最大偏航点 `home` 已收口
  - 其余扣分主要来自运行态自动化通道未恢复，而不是继续改页面代码就能稳定提升
- 若后续要再冲更高分，优先级应是：
  1. 恢复 `9520` 自动化连接
  2. 重新抓取 `home / mine / create / preview` 新鲜运行态截图
  3. 再决定是否继续做 1-2 分级别的 frame-level 微调

## 8. TabBar 图标运行态修复记录

### 8.1 问题

- 用户反馈：微信开发者工具预览中底部三个 tabBar 图标显示为破图占位。
- 涉及路径：
  - `kaipai-frontend/src/pages.json`
  - `kaipai-frontend/src/static/tabbar/home.png`
  - `kaipai-frontend/src/static/tabbar/home-active.png`
  - `kaipai-frontend/src/static/tabbar/rank.png`
  - `kaipai-frontend/src/static/tabbar/rank-active.png`
  - `kaipai-frontend/src/static/tabbar/mine.png`
  - `kaipai-frontend/src/static/tabbar/mine-active.png`

### 8.2 核查结论

- `src/pages.json` 的 tabBar 仍指向 `static/tabbar/*.png`，路径语义正确。
- `dist/dev/mp-weixin/app.json` 与 `dist/build/mp-weixin/app.json` 均保留相同 iconPath / selectedIconPath。
- 六个 tabBar 图标文件在 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 均存在。
- 修复前图标尺寸不统一：
  - `home / mine` 为 `128x128`
  - `rank` 为 `96x96`
- 为降低微信原生 tabBar 对图标资源的兼容风险，本轮把六个 PNG 统一重采样为微信 tabBar 推荐的 `81x81` 尺寸。

### 8.3 修改

- 修改文件：
  - `kaipai-frontend/src/static/tabbar/home.png`
  - `kaipai-frontend/src/static/tabbar/home-active.png`
  - `kaipai-frontend/src/static/tabbar/rank.png`
  - `kaipai-frontend/src/static/tabbar/rank-active.png`
  - `kaipai-frontend/src/static/tabbar/mine.png`
  - `kaipai-frontend/src/static/tabbar/mine-active.png`
- 修改方式：
  - 保持文件名和 `pages.json` 配置不变
  - 仅把图标资源统一为 `81x81` PNG
  - 不改 tab 页路由、不改 tabBar 文案、不改业务页面

### 8.4 验证

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`：通过
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`：通过，且 `postbuild:mp-weixin` 已同步 `dist/build/mp-weixin` 到 `dist/dev/mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run audit:mp-package`：通过
  - main：`520.40 KB / 2.00 MB`
  - pkg-card：`201.87 KB / 2.00 MB`
  - pkg-tools：`28.31 KB / 2.00 MB`
- 构建产物核验：
  - `dist/build/mp-weixin/static/tabbar/*.png` 六个文件均存在，均为 `81x81`
  - `dist/dev/mp-weixin/static/tabbar/*.png` 六个文件均存在，均为 `81x81`
  - 像素检查确认六个 PNG 不是透明空图，均有非透明像素
- 微信开发者工具 CLI 验证：
  - `D:\AP\微信web开发者工具\cli.bat cache --clean all --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`：通过
  - `D:\AP\微信web开发者工具\cli.bat open --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --port 9420`：通过
  - `D:\AP\微信web开发者工具\cli.bat preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --port 9420 --qr-format terminal`：通过，开发者工具可基于当前产物生成预览码

### 8.5 剩余边界

- 本轮已通过微信开发者工具 CLI 到达预览打包层，但未在当前回合补到自动化截图级断言。
- 继续尝试使用 `@dcloudio/uni-automator` 连接开发者工具截图时，Windows 本地在 automator 启动阶段返回 `spawn EINVAL`，截图链路未形成可采信证据；因此本轮不把截图级验证标记为完成。
- 若开发者工具窗口仍显示破图，应优先确认它打开的是 `kaipai-frontend/dist/dev/mp-weixin`，并在清缓存后重新编译；本轮 CLI 已对该目录执行过缓存清理、打开和预览。
