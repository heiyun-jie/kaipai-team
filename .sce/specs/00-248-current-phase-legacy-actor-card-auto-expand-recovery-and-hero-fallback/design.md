# 历史演员卡自动扩图补偿与首图无畸变兜底 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 根因链路

```text
历史 source_image 素材绑定
  -> 自动扩图后端部署前已完成
  -> 新后端只监听步骤 1 保存 / source_image 替换
  -> 卡主随后只调用 actor_card_generate
  -> expand_image 任务数为 0
  -> expanded_image_url 为空
  -> Renderer 回退原首图并用 scaleToFill 填充 750 x 1334
  -> 人物纵向拉伸
```

测试库只读基线：`cardId=1` 当前来源为 `assetId=1`，当前来源指纹为 `05872e925e35d07fb73ba9cabc6c054e6202a88b7d243bd0f591e65208fc925e`；扩图 URL、扩图指纹为空，`expand_image` 任务数为 `0`。

## 2. 后端补偿触发

复用 `ActorCardExpandImageService.requestAutomaticExpansion(userId, cardId)`，不增加第二套任务服务：

1. `GET /api/actor-card/draft/{cardId}` 在完成所有权校验和 DTO 读取后调用内部自动扩图入口。
2. `POST /api/actor-card/draft/{cardId}/generate` 在提交结构化生成任务前调用同一入口，覆盖直接调用生成接口的旧客户端。
3. 步骤 1 保存和 `source_image` 替换的既有触发点保持不变。
4. 匿名 `GET /api/actor-card/public/{cardId}`、卡片列表和服务启动不调用该入口。

`requestAutomaticExpansion` 已捕获提交阶段异常；`enqueue` 已用 `actor_card_id + expand_image + source_fingerprint` 唯一键和查询实现幂等。补偿层只增加触发时机，不改变任务状态机、Provider、存储或来源指纹算法。

## 3. 异步一致性

- 草稿读取和生成接口不等待扩图完成，不新增演员可见状态。
- 正常新卡在步骤 1 后已有多步编辑时间完成扩图；历史卡首次访问时只保证任务被创建。
- 共享公开 DTO 每次通过 `ActorCardMainVisualResolver` 读取当前有效结果，因此任务稍后完成并回写后，重新读取生成页/公开页即可消费扩图。
- 旧来源任务完成时仍由 `ActorCardExpandResultService.applyIfCurrent` 拒绝回写。

## 4. Hero 无畸变兜底

`ActorCardRenderer.vue` 是生成页与公开页唯一共享渲染器。将 Hero 原生 `image` 的 `mode` 从 `scaleToFill` 改为 `aspectFill`：

- 原图保持宽高比，超出 9:16 画布的部分居中裁切；
- 已扩展为 9:16 的图片基本不发生裁切；
- 固定 Hero 高度、绝对定位信息层、照片/视频模式和正文结构不变；
- 不新增“扩图中”或“扩图失败”等可见状态。

## 5. 私有桶扩图读 URL

MCP 在 Candidate `20260901-174738-v3-draft` 上证明补偿任务已成功且指纹匹配，但 `expanded_image_url` 是测试私有桶的无签名稳定 URL，Renderer 收到资源错误并显示“主视觉资源暂不可用”。因此任务成功与浏览器可读是两个独立门禁。

1. `AiGeneratedImageStorage` 增加受管 COS URL 的短时读签名能力，仅接受当前配置 bucket/region 对应的对象路径。
2. `ActorCardPublicServiceImpl` 与 `ActorCardPublishService` 在响应组装阶段签名扩图；持久字段和任务结果保持无签名稳定 URL。
3. `ActorCardMainVisualResolver` 暴露“不含扩图”的来源图解析入口。签名异常时响应回退来源绑定/历史来源，不阻断详情与列表读取。
4. 签名只改变响应值，不修改数据库、Provider、异步任务状态或匿名触发边界。

## 6. 测试设计

### 6.1 后端

- Controller 合同测试：读取草稿后调用 `requestAutomaticExpansion`，且 DTO 原样返回。
- Controller 合同测试：生成前调用 `requestAutomaticExpansion`，并继续调用原生成服务。
- 公开服务/列表测试保持无扩图服务依赖，从结构上证明无匿名或批量触发。
- 私有桶读 URL 测试覆盖受管 URL 签名、非受管 URL 原样返回、详情/列表签名和签名异常来源回退。
- `ActorCardExpandImageServiceTest` 继续覆盖相同来源复用、失败重试和异步成功回写。

### 6.2 前端

- 新增 `verify-00248-actor-card-expand-recovery.mjs`，检查源码以及 build/dev Renderer：
  - Hero 使用 `aspectFill`；
  - Hero 不含 `scaleToFill`；
  - 生成页与公开页仍引用共享 Renderer；
  - build/dev WXML、WXSS、JS 字节一致，scoped `data-v` 一致。
- 执行类型检查、既有演员卡专项门禁、构建和包体审计。

## 7. Candidate 与运行验证

1. 代码和测试通过后冻结新 Candidate，不能覆盖 `20260901-150906-v3-draft`。
2. 冻结小程序完整物化到 `dist/build/mp-weixin` 和固定 `dist/dev/mp-weixin`。
3. 新后端只部署到 `kaipai-backend-test`，数据库仍为 `kaipai_test`。
4. 通过微信内部 MCP 打开 `pkg-actor-card/generate/index?cardId=1`，不操作可见桌面窗口。
5. 只读验证产生一个来源指纹匹配的 `expand_image / success` 任务；MCP 必须观察到扩图对象、`mode="aspectFill"` 且不存在主视觉资源占位，并核对控制台和网络状态。
6. 记录生产容器身份未变；不进入 `00-237`。

## 8. 回滚

- 后端回滚移除草稿读取和生成入口的两个补偿调用，不改变任务表或历史数据。
- 前端回滚恢复 Renderer 原始文件；回滚只在独立本地副本验证原始 SHA256。
- 测试部署回滚使用 Candidate 运行态记录；生产环境不进入本 Spec 的修改或回滚路径。
