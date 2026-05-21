# 00-144 当前阶段小程序框架重构与 UI 审查（Current Phase Miniapp Framework Refactor And UI Review）

> 状态：进行中 | 优先级：最高 | 依赖：00-27 mini-program-frontend-architecture，00-69 current-phase-share-analytics-architecture-refactor，00-70 current-phase-share-prototype-ui-implementation，00-73 current-phase-reference-ui-architecture-rebuild
> 记录目的：把“审查当前框架重构和小程序 UI 修改，低于 95 分就继续修改”收口成独立 Spec，避免继续以口头标准给分或只做代码阅读不做运行态复核。

## 1. 背景

截至当前仓库状态：

1. 小程序前端主链已经由 `00-69 / 00-70 / 00-73` 连续推进，路由与可见层目标已明确收口到：
   - `pages/login/index`
   - `pages/home/index`
   - `pages/history/index`
   - `pages/mine/index`
   - `pkg-card/card-list/index`
   - `pkg-card/actor-card/index`
   - `pages/actor-profile/detail`
2. 当前前台重构不再只是“改样式”，而是同时包含：
   - route ownership 收口
   - shared component contract 收口
   - token / layout contract 收口
   - 参考稿 frame-level UI 收口
3. 用户已明确要求：
   - 必须创建 specs 承接本轮任务
   - 需要对“当前框架重构”和“小程序 UI 修改”进行审查
   - 若审查低于 `95` 分，则不能停在结论，必须继续修改

当前判断：

- 不能只做 code review，因为本轮对象明确包含运行态 UI。
- 也不能只做截图比对，因为用户同时要求审查“框架重构”。
- 因此本轮必须形成一套统一评分基线，同时覆盖：
  - 前台框架 carrier 是否按 `00-27 / 00-73` 收口
  - 7 屏主链 UI 是否达到 reference 合同
  - `src / dist/build / dist/dev / 运行态` 四层证据是否闭环

依据：

- `D:\XM\kaipai-team\.sce\specs\00-27-mini-program-frontend-architecture\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\design.md`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

置信度：

- 高

不确定边界：

- 当前仓库存在已有未提交改动和未登记 Spec 目录，本轮只审查并修改与小程序前台主链直接相关的代码与文档。
- 若运行态截图链路再次卡在 `miniProgram.screenshot()`，本轮允许采用 `DevTools / OS 级窗口截图 + dist 双产物核查` 作为补充证据，但必须在 `execution.md` 明示。

## 2. 范围

### 2.1 本轮必须处理

- 创建独立 `00-144` 审查 Spec，定义评分规则、通过阈值和低分后的继续修改规则。
- 审查当前小程序前台框架重构 carrier，包括：
  - `pages.json`
  - route ownership
  - shared component contract
  - token / layout contract
  - 7 屏核心路由职责
- 审查当前小程序主链 UI，包括：
  - `login`
  - `home`
  - `history`
  - `mine`
  - `create`
  - `card preview`
  - `poster preview`
- 对低于 `95` 分的差异执行继续修改。
- 至少执行：
  - `kaipai-frontend npm run type-check`
  - `kaipai-frontend npm run build:mp-weixin`
- 按 `mp-ui-change-verification` 要求核对：
  - `src`
  - `dist/build/mp-weixin`
  - `dist/dev/mp-weixin`
- 回填：
  - `execution.md`
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`

### 2.2 本轮不处理

- 后台 `00-140 ~ 00-143` 相关控制台页面
- 与当前前台主链无关的 runbook / release 文档
- 数据库 / Nacos / 发布链路问题
- support routes 的全面视觉重构，只在其影响 core screens 时处理

## 3. 需求

### 3.1 审查对象与基线

- **R1** 本轮框架审查必须以 `00-27` 的前端分层和 `00-73` 的 route ownership 为基线，不能自创另一套口径。
- **R2** 本轮 UI 审查必须以 `00-73` 的 7 屏 frame contract 为基线，不能只按“同风格”打分。
- **R3** 所有评分结论必须附带具体依据文件、截图或构建产物，不得给出无证据分数。

### 3.2 评分模型

- **R4** 总分为 `100` 分，固定拆分为四组：
  - 框架与路由职责：`30`
  - shared component / token / layout contract：`20`
  - 7 屏 UI fidelity：`35`
  - 构建与运行态证据闭环：`15`
- **R5** 任一组存在明显主线漂移、职责错位、reference 外结构混入、或证据链缺失时，必须扣分并记录原因。
- **R6** 总分低于 `95` 分时，不得停在评语；必须继续执行针对性修改，并在修改后重新评分。
- **R7** 重新评分可以多轮进行，但每轮必须说明：
  - 上一轮分数
  - 本轮修改项
  - 本轮提升依据
  - 剩余扣分项

### 3.3 框架审查要求

- **R8** `pages.json` 必须继续维持 `home / history / mine` 三 tab 主链，且 `create / preview` 路由职责不能回退到旧 desk 语义。
- **R9** `pkg-card/card-list/index` 必须继续表达 `CreateScreen` 主职责，而不是旧列表管理页。
- **R10** `pkg-card/actor-card/index` 必须继续统一承接 `CardPreviewScreen / PosterPreviewScreen`，不得再把 `pages/actor-profile/detail` 当 creator preview 主入口。
- **R11** shared component 必须继续由统一 carrier 承接，而不是把 pill/button/section title 复制回页面私有样式里。

### 3.4 UI 审查要求

- **R12** `login / home / history / mine / create / card preview / poster preview` 必须逐页对照 `00-73` 的 page-level contract。
- **R13** `home` 不得继续混入与当前演员分享主链无关的旧 crew 主线可见结构。
- **R14** `mine` 的信息架构必须继续向 reference `MyScreen` 收口，不能回退到“个人档案 + 杂项设置”旧形态。
- **R15** `create` 页必须同时满足步骤条、风格卡、素材区、artifact 选择和底部 CTA 的完整三段式合同。
- **R16** `card preview / poster preview` 必须继续按页级 reference 检查舞台、topbar、quick edit、底部动作和主次按钮关系。

### 3.5 证据闭环要求

- **R17** 每次 UI 修改后必须至少确认：
  - `src` 已改到正确视觉锚点
  - `dist/build/mp-weixin` 已生成对应类和值
  - `dist/dev/mp-weixin` 已同步对应类和值
  - 至少一种可信运行态证据已更新
- **R18** 若运行态截图链路受阻，不得继续盲改样式；必须先记录阻断点，再决定是否用替代证据推进。
- **R19** `execution.md` 必须记录最终评分、扣分项、修改项、验证命令和剩余边界。

## 4. 验收标准

- [ ] 已新增独立 `00-144` 审查 Spec
- [ ] 已定义固定 100 分评分模型和 `95` 分通过阈值
- [ ] 已对框架与 UI 做出带证据的初始评分
- [ ] 若初始评分低于 `95` 分，已继续修改并重新评分
- [ ] 已完成 `type-check` 与 `build:mp-weixin`
- [ ] 已核对 `src / dist/build / dist/dev`
- [ ] 已把审查和修改结论回填到 `execution.md`
- [ ] 已回填 `README / spec-code-mapping / CURRENT_CONTEXT`
