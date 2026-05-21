# 00-147 Design

## 1. 主线策略

本轮采用“总 spec + 三条并行审查线 + 主线程统一改动与复审”的方式推进：

1. 后端与数据库严格审查
2. 小程序逐页 UI / API 审查
3. 后台逐页 UI / API 审查

主线程负责：

- 建立总评分模型
- 汇总三条线的扣分项
- 优先处理会直接拖低机器审查分的项目级残留
- 统一执行编译、构建、产物核验与回填

## 2. 评分模型

### 2.1 机器审查 95 分

- 后端 API 与数据库：`35`
- 小程序 UI 与 API：`30`
- 后台 UI 与 API：`30`

### 2.2 评分门禁

- 任一主线存在严重 legacy/fallback/兼容链残留，直接判定该线不通过。
- 任一主线存在逐页 API 未接真实事实源、页面大面积重复 UI 未组件化、或运行态产物与源码不一致，直接扣到 `95` 以下。

## 3. 审查方法

### 3.1 后端与数据库

- 查 controller/service/entity/dto/migration 引用链
- 查 `legacy / fallback / compat / transitional / repair` 关键词
- 查数据库 migration 是否只是“加列不收口”
- 判断哪些能立即删除，哪些仍是主链阻塞

### 3.2 小程序

- 以 `pages.json` 为入口审页面范围
- 逐页核对：
  - 页面 UI 结构
  - 页面 API 请求
  - 是否有 mock、兜底、旧链路
  - 是否有重复 UI 可抽组件
- 严格按 `src + dist/build + dist/dev` 三层核对

### 3.3 后台

- 以 `router/index.ts + menus.ts + admin-information-architecture.ts` 为入口审页面范围
- 逐页核对：
  - 页面 UI 与架构归属
  - API 请求与权限合同
  - 是否还有旧 route/meta/menu/fallback 暴露
  - 是否已有可抽象却未复用的 UI 模式

## 4. 实施原则

- 先列证据，再给分，再修改。
- 修改必须优先去掉残留，不做“保留兼容层以后再说”。
- 任何“完成”结论都必须建立在重新验证通过之后。
