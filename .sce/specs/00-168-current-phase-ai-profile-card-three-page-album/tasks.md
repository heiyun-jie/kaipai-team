# AI 分享图固定三页资料册 Tasks

## Phase 1: 需求收口与规格

- [x] 评估单页 AI 分享图对完整演员资料的承载上限。
- [x] 确认固定 3 页比任意页数更适合作为当前产品边界。
- [x] 创建本 spec 的 `requirements.md`、`design.md`、`tasks.md`。
- [ ] 把本 spec 纳入后续实现排期。

## Phase 2: 数据模型与接口

- [x] 新增页面级资产表 `actor_ai_profile_card_page`。
- [x] 新增页面级 entity / mapper / DTO。
- [x] 扩展 task / artifact 响应，返回有序 `pages`。
- [x] 保持旧单页 artifact 兼容。

## Phase 3: 三页 Agent 与生成编排

- [x] 扩展 prompt agent，输出 `cover / resume / gallery` 三页合同。
- [x] 为三页定义独立 background-only prompt。
- [x] 主任务固定创建 3 个 page 记录。
- [x] 实现三页生成汇总状态与失败原因。
- [x] 保持 provider 路由、多厂商配置和 Tencent prompt rewrite 默认关闭。

## Phase 4: 前端三页详情页

- [x] 扩展前端 AI artifact 类型。
- [x] 把单页 preset registry 扩展为三页 album preset。
- [x] 在详情页渲染 `cover / resume / gallery` 连续三页。
- [x] 为 `resume` / `gallery` 补齐确定性前景模块。
- [x] 保持旧单页 fallback。
- [x] 为非首屏页增加懒加载或等价优化。

## Phase 5: 分享、作品集与兼容

- [x] 作品集卡片继续使用 `cover` 作为封面。
- [x] 分享路径继续进入 AI 详情页。
- [x] 默认分享图继续使用 `cover`。
- [x] 明确当前阶段不做三页拼接导出。

## Phase 6: 自动化验证

- [x] 后端测试：固定 3 页、页序、页面级 prompt、旧单页兼容。
- [x] 前端测试 / audit：三页 preset、旧单页 fallback、首屏加载不退化。
- [x] 类型检查和构建验证。

## Phase 7: 真人 E2E

- [ ] 使用真实账号完整提交一次三页生成。
- [x] 截图验证 `cover`。
- [x] 截图验证 `resume`。
- [x] 截图验证 `gallery`。
- [ ] 截图验证作品集入口与详情页跳转。
- [x] 验证分享仍进入三页详情页。
- [x] 记录三页视觉审查结论和失败项。

## Current Status

- 产品边界已收敛为固定 3 页：
  - `cover`
  - `resume`
  - `gallery`
- 后端已实现固定三页 page 表、DTO、生成编排和页面级 prompt。
- 小程序详情页已支持 `pages` 三页连续渲染，并保留旧单图兜底。
- H5 渲染脚本已用 mock artifact 截图验证 `cover / resume / gallery`，微信小程序目标构建通过。
- 当前方案明确保留：
  - AI 背景-only；
  - `750 x 1334` 设计坐标主合同；
  - `cover` 作为默认分享封面；
  - 旧单页 artifact 兼容；
  - 不开放任意页数配置。
