# 00-153 需求

## 目标

将当前分享页流程收敛为最小 MVP：

1. `pkg-card/card-list/index` 作为唯一创建分享页流程。
2. 创建分享页保留三步：选择风格、上传作品、命名并选择分享形式。
3. `pkg-card/actor-card/index` 只作为预览和分享页面，不再承载二次三步配置。

## 用户确认

用户确认三步 MVP 方向：

- 选择风格。
- 上传作品。
- 命名并选择分享形式。

## 必须修正的问题

- `card-list` 点击 `下一步` 不能跳回或停留在 `pkg-card/card-list/index`。
- `card-list` 点击 `下一步` 后不能再进入 `actor-card` 的二次三步配置流程。
- `actor-card` 在 `artifact=miniProgramCard` 时不能因为海报机构名称缺失阻塞页面。
- 当前 MVP 不需要配置化分享页，不展示 `卡片预览 / 快速调节 / 内容配置` 二次步骤。
- 当前 MVP 不展示 `保存配置`、`保存分享配置` 这类配置化主流程文案。

## 验收标准

- `pkg-card/card-list/index` 底部 `下一步`：
  - 已有分享卡：进入 `actor-card` 预览。
  - 没有分享卡且有作品：创建分享卡后进入 `actor-card` 预览。
  - 没有作品：停留本页并提示上传作品。
- `pkg-card/actor-card/index`：
  - 不显示编辑步骤条。
  - 不显示 `快速调节` 配置面板。
  - 不显示 `内容配置` 配置面板。
  - 不显示 `保存配置` 或 `保存分享配置`。
  - 保留卡片/海报预览、复制链接、发送给好友、保存海报。
- `artifact=miniProgramCard` 进入 `actor-card` 时不调用或不强制校验海报机构名称。
- `artifact=poster` 才需要海报相关机构名称。
- `npm run type-check`、`npm run build:mp-weixin`、`npm run audit:mp-package` 通过。
- 源码和构建产物审查通过，评分不得低于 95。
