# 00-66 当前阶段分享主题映射请求事实调查（Current Phase Share Theme Request-Fact Investigation）

> 状态：调查中 | 优先级：最高 | 依赖：00-63 current-phase-share-card-latest-state-alignment，00-64 current-phase-actor-card-editor-boundary-alignment
> 记录目的：把“`pkg-card/actor-card/index` 中配置的颜色 / 代表照片 / 高亮经历，与 `pages/actor-profile/detail` 的真实展示不一致”的问题，先收口为**请求事实调查 Spec**，在拿到接口请求与返回证据前，不再继续拍脑袋修改实现。

## 1. 背景

当前用户已经明确指出两类问题：

- `pkg-card/actor-card/index` 当前页的主题预览映射错误
- `pages/actor-profile/detail` 公开页的颜色映射和内容映射错误

此前在未先抓取请求事实的情况下，直接根据代码和截图推断根因并修改实现，违反了当前项目“先建 Spec，再调查，再实现”的规则。

因此本轮必须先停下继续修改，转为**请求事实优先**的调查流程。

## 2. 范围

### 2.1 本轮必须处理

- 建立独立调查 Spec
- 固定调查对象：
  - `pkg-card/actor-card/index`
  - `pages/actor-profile/detail`
  - `/api/card/config`
  - `/api/card/personalization`
- 明确请求抓取、返回比对、页面消费链比对方法
- 在没有拿到请求事实前，不得继续根据猜测修改映射逻辑

### 2.2 本轮不处理

- 直接修复颜色算法
- 直接修复代表照片 / 高亮经历算法
- 多实例模型改造
- 大幅调整 UI

## 3. 需求

### 3.1 调查原则

- **R1** 本问题必须先拿到真实请求与返回证据，再决定是否修改实现。
- **R2** 禁止继续根据截图直觉、代码推断或单侧实现阅读直接下结论。
- **R3** 在调查未完成前，只允许补调查 Spec、调查脚本、调查记录，不允许继续改业务映射逻辑。

### 3.2 必查请求链

- **R4** 必须调查 `pkg-card/actor-card/index` 保存时发出的 `/api/card/config` 请求体。
- **R5** 必须调查 `/api/card/config` 的响应体中，是否真实回写了：
  - `primaryColor`
  - `accentColor`
  - `backgroundColor`
  - `highlightedPhotos`
  - `highlightedExperiences`
  - `tagOrder`
- **R6** 必须调查 `pages/actor-profile/detail` 打开时发出的 `/api/card/personalization` 请求与响应。
- **R7** 必须调查 `/api/card/personalization` 返回中的：
  - `profile.customConfig`
  - `profile.sharePreferences`
  - `theme.primary`
  - `theme.accent`
  - `theme.background`
- **R8** 必须调查 `detail.vue` 最终实际消费的是哪组字段，而不是只看“理论应该消费什么”。

### 3.3 结论边界

- **R9** 若 `/api/card/config` 保存值就已经错误，结论应归因于保存链，不得继续把问题归咎给公开页映射。
- **R10** 若 `/api/card/config` 保存正确，但 `/api/card/personalization` 聚合错误，结论应归因于后端主题 / 个性化聚合链。
- **R11** 若 `/api/card/personalization` 返回正确，但 `detail.vue` 展示错误，结论应归因于前端页面消费链。
- **R12** 必须明确区分“请求值错”“聚合值错”“页面消费错”三种责任层级，不得把它们混成一句“映射错了”。

### 3.4 输出要求

- **R13** 本 Spec 必须产出调查执行记录，至少包含：
  - 请求样本
  - 响应样本
  - 页面消费点
  - 结论
  - 下一步修复建议
- **R14** 在调查执行记录完成前，不得继续推进新的映射修复。

## 4. 验收标准

- [ ] 已新增独立 `00-66` 调查 Spec
- [ ] 已明确本轮调查对象和禁止项
- [ ] 已固定 `/api/card/config` 与 `/api/card/personalization` 为必查请求链
- [ ] 已明确三层责任边界：保存链 / 聚合链 / 页面消费链
- [ ] 已在执行记录中沉淀真实请求事实后，才允许进入下一步修复
