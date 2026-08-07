# 00-204 任务拆解

- [x] 建立体重常驻展示、单一数据字段和禁止改动其他内容的书面合同。
- [x] 只读确认 `actor_profile.weight` 真实存在，并把它加入本地启动 schema 门禁。
- [x] 补齐 `career.weight -> response.weight` 接口合同和持久化映射断言。
- [x] 将既有体重输入移到核心资料年龄 / 身高行，复用 `draft.career.weight`，不保留重复输入。
- [x] 执行后端专项测试、前端 type-check 和小程序构建。
- [x] 核对 `src / dist/build / dist/dev` 三层体重入口一致。
- [x] 执行 steering 与包体审计并记录结果。

## 验证记录

- 数据库只读核验：`actor_profile.weight` 为 `INT NULL`，默认值为 `NULL`。
- Schema 门禁：`3 / 3` 通过。
- 后端专项测试：`12 / 12` 通过，覆盖 PUT 请求反序列化、GET / PUT 响应和 Service 映射。
- 前端：`npm run type-check`、`npm run build:mp-weixin` 通过，postbuild 已同步到 `dist/dev/mp-weixin`。
- 三层核验：源码、`dist/build`、`dist/dev` 均只有一个体重编辑器，并显示 `kg`。
- Steering 审计通过。
- 包体审计已执行，但被既有 `dist/build/mp-weixin/api/actor-asset.js` 本地 API 地址拦截；遵循范围约束，未修改无关 API 配置。
