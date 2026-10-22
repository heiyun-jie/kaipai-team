# 名片夹草稿发布准备度与操作入口收口 - 技术设计

## 1. 影响范围

- 后端 DTO：`ActorCardListItemDTO.java`
- 后端组装：`ActorCardPublishService.java`
- 后端测试：`ActorCardPublishServiceTest.java`
- 前端类型：`src/api/actor-card.ts`
- 前端页面：`src/pages/card-list/index.vue`
- 专项门禁：`scripts/verify-00254-card-list-draft-publish-actions.mjs`

不修改数据库、发布接口、生成任务状态机、公开详情页和已发布卡操作。

## 2. 后端状态派生

`ActorCardPublishService.toListItem()` 对每张卡读取主视觉绑定和真实作品数，并派生：

```text
hasRequiredInputs = hasMainVisual
                 && profileSnapshotJson 有值
                 && actor_card_work 行数 > 0
                 && settingsJson 有值

generateReady = status == draft && hasRequiredInputs
publishReady  = status == draft && generatedPreviewUrl 有值
```

`publishReady` 优先于 `generateReady` 决定前端动作。作品数同时进入完成度计算，消除列表中“作品默认完成”的历史简化。

_Requirements: 3.1, 3.3_

## 3. 向后兼容

- Java DTO 新增 `Boolean generateReady`、`Boolean publishReady`，JSON 响应只增加字段。
- TypeScript DTO 使用可选字段，旧后端缺失时表达式严格比较 `=== true`，不会误开放生成或发布入口。
- 旧小程序忽略新字段；新小程序配旧后端仍显示“继续编辑 / 删除草稿”。
- 不需要 Schema 迁移，后端可先部署或与小程序同批次进入新 Candidate。

_Requirements: 3.1, 5_

## 4. 前端操作状态

页面新增纯函数：

```text
hasDraftStageAction(card) = card.publishReady === true || card.generateReady === true
draftStageActionText(card) = publishReady ? 预览并发布 : 生成预览
```

点击阶段动作时：

```text
publishReady -> generate/index?cardId={id}&preview=1
generateReady -> generate/index?cardId={id}
```

页面不导入、不调用 `publishActorCard`。发布仍由生成页在用户确认后执行。

_Requirements: 3.2, 3.3_

## 5. 布局

- 普通草稿继续使用两列等宽 Grid。
- 存在阶段动作的草稿使用三列等宽 Grid。
- “生成预览 / 预览并发布”使用品牌蓝主操作样式；继续编辑为描边次操作，删除为危险描边操作。
- 三列按钮继续固定 `64rpx` 高度并禁止换行。

_Requirements: 3.2_

## 6. 验证

1. 后端定向测试：`mvn -Dtest=ActorCardPublishServiceTest test`
2. 前端类型检查：`npm run type-check`
3. 专项门禁：`npm run verify:card-list-draft-actions`
4. 既有回归：`npm run verify:card-list-layout`、`npm run verify:v3-card-list`
5. 项目级 MCP 退出固定工程后执行 `npm run build:mp-weixin`
6. 重新执行专项门禁并核验固定 `dist/dev` 三件套

## 7. 发布兼容与回滚

- 本次无数据库变化、无数据清理，回滚只需恢复 DTO、组装逻辑、测试、前端类型和页面，并删除专项脚本入口。
- 测试环境后端与小程序必须来自同一新 Candidate；只更新一侧不得进入人工验收。
- 不执行生产迁移、生产容器重建、正式 Nginx 切流或正式小程序上传。
