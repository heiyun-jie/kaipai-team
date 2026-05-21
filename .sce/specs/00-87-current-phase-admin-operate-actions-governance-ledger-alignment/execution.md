# 00-87 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md` 与 `00-86`
- 已把当前主线继续收窄到 `operate/actions` 下方治理动态区

## 2. 修复前证据

### 2.1 修复前截图

- reference：`D:\XM\kaipai-team\output\playwright\00-86\operate-actions-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-87\operate-actions-governance-before.png`

### 2.2 修复前量化

`2026-04-22` 当前轮次真实浏览器量化结果：

- 整卡尺寸：`1134 × 279`
- 标题顶部：`y ≈ 805`
- 提示宽度：`320px`
- 空态高度：`158px`
- 空态 padding：`32px 16px 36px 16px`
- 当前 `recentItems`：`0`

## 3. 设计判断

当前最合理的下一手是继续留在 `operate/actions` 单页，只处理治理动态区。

原因：

- `00-86` 已把首屏主表达收口
- reference 差异现在只剩下方轻量台账表达
- 当前 `recentItems` 为空，更适合先把空态 ledger 壳层收口

## 4. 本轮实施

### 4.1 代码改动

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue`

已实施内容：

1. 把治理动态区从 `campaign-list / campaign-item / table-empty` 厚卡片表达，切换为新的 `governance-ledger`
2. 新增 ledger 结构：
   - `governance-ledger__head`
   - `governance-ledger__body`
   - `governance-ledger__row`
   - `governance-ledger__empty-row`
3. 非空时按真实 `recentItems` 输出列式表达：
   - 动态
   - 业务线
   - 状态
   - 发生时间
   - 处理入口
4. 空态时不再使用厚空盒，而改为保留列头 + 跨列空态行
5. 新增 ledger 的局部桌面 / 移动端样式，不触碰首屏工具卡、动作推荐与 overview 辅助摘要

### 4.2 边界确认

本轮未改动：

- 顶部工具卡
- 动作推荐区
- overview 辅助摘要区
- 真实 `recentItems` 事实源
- route query 跳转逻辑
- 任何伪 campaign 数据

## 5. 验证结果

### 5.1 真实浏览器复核

会话：

- 当前运行态：Playwright `layout-shell`

运行态路径：

- `http://127.0.0.1:5100/operate/actions`

修复前后截图：

- reference：`D:\XM\kaipai-team\output\playwright\00-86\operate-actions-reference.png`
- 修复前：`D:\XM\kaipai-team\output\playwright\00-87\operate-actions-governance-before.png`
- 修复后：`D:\XM\kaipai-team\output\playwright\00-87\operate-actions-governance-after.png`

### 5.2 修复后量化

`2026-04-22` 当前轮次真实浏览器量化结果：

- 整卡尺寸：`1134 × 273`
- 标题顶部：`y ≈ 1237`
- ledger 尺寸：`1084 × 152`
- ledger 列头高度：`48px`
- 空态行高度：`102px`
- 空态 padding：`26px 18px 28px 18px`
- 当前 `recentItems`：`0`

### 5.3 修复前后对比

| 项目 | 修复前 | 修复后 | 结论 |
|------|--------|--------|------|
| 整卡高度 | `279px` | `273px` | 略收紧 |
| 空态高度 | `158px` | `102px` | 已明显收紧 |
| 空态 padding | `32px 16px 36px 16px` | `26px 18px 28px 18px` | 已收紧 |
| 列式结构 | 无 | 有列头 + 空态行 | 已建立 ledger 感 |

### 5.4 运行态判断

当前修复后运行态已更接近 reference 的治理台账表达：

- 保留了轻量列头
- 空态不再是厚空盒
- 即使 `recentItems` 为空，也有清晰的 ledger 壳层

仍保留的 reference 差异：

- reference 是概念活动台账
- 当前运行态只认真实 `recentItems`，因此不会伪造 campaign 行

### 5.5 静态构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

## 6. 结论

`00-87` 已完成本轮目标：

- `ActionsView.vue` 治理动态区已完成独立局部收口
- 运行态已通过真实浏览器复核
- 修复前后截图、量化结果与构建验证已回填

若继续后台 reference UI 主线，最自然的下一条应离开 `operate/actions`，转去尚未独立 page-level 精修的正式页，例如 `system/settings`。
