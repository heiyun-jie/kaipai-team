# 00-153 设计

## 页面职责

### `pkg-card/card-list/index`

唯一创建分享页页面。

保留三步：

1. 选择风格。
2. 上传作品。
3. 命名并选择分享形式。

点击 `下一步` 后进入预览，不进入二次配置。

### `pkg-card/actor-card/index`

预览和分享页面。

只保留：

- 卡片/海报预览。
- 复制链接。
- 发送给好友。
- 保存海报。
- 返回。
- 卡片/海报切换。

移除或隐藏当前 MVP 不需要的配置化能力：

- 编辑步骤条。
- 快速调节。
- 内容配置。
- 保存配置。
- 联系方式申请处理区。

## 路由模式

使用显式 `mode` 参数：

- `mode=preview`：预览分享页，隐藏所有配置流程。
- `mode=edit`：保留给未来配置化版本，当前 MVP 不从用户主流程进入。

当前 MVP 中，`card-list` 只生成：

```text
/pkg-card/actor-card/index?mode=preview&shareCardId=xxx&artifact=miniProgramCard
```

或：

```text
/pkg-card/actor-card/index?mode=preview&shareCardId=xxx&artifact=poster
```

## 海报机构名称

`actor-card` 只有在 `selectedArtifact === 'poster'` 时加载和校验机构名称。

卡片预览不依赖机构名称，不能被 `companyName` 缺失阻塞。

## 不做事项

- 不改后端 API。
- 不新增旧逻辑兜底。
- 不保留用户可见的二次三步编辑入口。
- 不继续扩展配置化分享页。
