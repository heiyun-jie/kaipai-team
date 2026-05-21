# 00-144 设计说明

## 1. 设计目标

本 Spec 的目标不是新增一条前台实现主线，而是为当前前台主链建立一个可执行的审查闭环：

1. 先按 `00-27 + 00-73` 审查当前框架与 UI
2. 给出带证据的分数
3. 若低于 `95`，立即转入最小必要修改
4. 修改后重新验证和重新评分

## 2. 审查对象

### 2.1 框架 carrier

- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpPillSelector.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpSectionHead.vue`

### 2.2 7 屏 core pages

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

### 2.3 参考基线

- `D:\XM\kaipai-team\_-_.html`
- `D:\XM\kaipai-team\output\playwright\reference-overview.png`
- `D:\XM\kaipai-team\output\playwright\reference-full.png`
- `00-73 execution.md` 中已记录的逐页 reference 和历史运行态证据

## 3. 评分设计

### 3.1 评分表

| 维度 | 分值 | 通过条件 |
|------|------|------|
| 框架与路由职责 | 30 | 7 屏 route ownership、tab 结构、preview/create 主链没有明显回退 |
| shared contract | 20 | button / pill / section head / token 仍由 shared carrier 承接，未被页面私有变体冲散 |
| UI fidelity | 35 | 7 屏核心可见块与 `00-73` 合同无明显 frame-level 漂移 |
| 证据闭环 | 15 | `src / dist/build / dist/dev / 运行态` 形成可信闭环 |

### 3.2 扣分原则

- 发现旧主线可见结构仍残留在 core screen 中：扣 `3-8`
- route ownership 明显漂移：扣 `5-10`
- shared component contract 被页面私有样式绕开：扣 `2-6`
- frame-level 明显不符合 `00-73`：按页面扣 `2-8`
- 缺运行态 / dist 证据：扣 `2-10`

### 3.3 继续修改策略

当总分 `<95`：

1. 只处理最高收益、最低歧义、与 core screens 直接相关的扣分项
2. 优先处理：
   - 旧主线可见结构残留
   - route ownership 回退
   - frame-level 明显偏差
3. 每轮只做窄改，不把审查任务扩成新的大重构

## 4. 验证设计

### 4.1 代码与构建验证

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

### 4.2 四层核验

对每个被修改的 UI 锚点，至少核验：

1. `src`
2. `dist/build/mp-weixin`
3. `dist/dev/mp-weixin`
4. 运行态截图、DevTools 活跃窗口截图或既有 automator 量化证据

### 4.3 运行态证据策略

- 优先复用仓库已有的小程序截图/automator脚本与 `00-73 execution.md` 的量化证据链
- 若本轮需要继续修改某个页面，则优先补该页的新鲜构建和运行态证据
- 若 `miniProgram.screenshot()` 再次阻断，则改走：
  - OS 级窗口截图
  - DevTools 活跃窗口截图
  - DOM / dist 双产物核查

## 5. 预期输出

- 一份带证据的初始评分
- 一组低于 `95` 分时的继续修改项
- 一份修改后的复评分
- 更新后的 `execution.md / README / mapping / CURRENT_CONTEXT`
