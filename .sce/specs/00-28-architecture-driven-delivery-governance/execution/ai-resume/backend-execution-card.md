# AI 简历润色闭环后端执行卡

## 1. 执行卡名称

AI 简历润色闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/ai-resume-polish-capability-slice.md`

## 3. 负责范围

- AI 配额、上下文组装、字段级 patch 生成、历史回滚的后端协议
- AI 调用封装、超时控制、失败兜底、敏感内容过滤
- 档案字段 patch 的服务端校验、配额扣减与审计日志
- AI 历史、回滚与异常样本的持久化设计
- 小程序侧 AI 能力查询与执行接口

## 4. 不负责范围

- 编辑页弹窗、diff 预览和字段应用的前端交互
- 后台 AI 运维页面的具体 UI 布局
- 前端直连模型
- 没有结构化协议约束的自由文本返回

## 5. 关键输入

- 上位 Spec：
  - `00-03 shared-utils-api`
  - `05-04 ai-resume-polish`
  - `05-04 ai-resume-polish/contract.md`
  - `05-11 fortune-driven-share-personalization`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/fortune/FortuneController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/fortune/service/impl/FortuneReportServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumePolishReqDTO.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumePolishRespDTO.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumeHistoryItemDTO.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumeApplyMetaDTO.java`
  - `kaipai-frontend/src/api/level.ts`
  - `kaipai-frontend/src/types/level.ts`
  - 备注：当前仓库虽已补最小 AI DTO 骨架，但独立的 `/ai` controller / service / entity 仍未形成完整闭环

## 6. 目标交付物

- 后端具备真实的 AI 模块，而不是只有前端假定的 `/api/ai/quota` 与 `/api/ai/polish-resume`
- 能基于整份演员档案上下文输出可解析的字段级 patch
- 配额扣减、失败回滚、敏感内容处理、超时兜底都以后端为准
- AI 历史、回滚、异常样本可追溯
- 前端可消费统一、稳定的 AI 契约，不再依赖 mock

## 7. 关键任务

1. 新建独立 AI 模块
   - 当前仓库没有专门的 `/ai` controller / service / dto / entity
   - 需要补齐 AI quota、resume polish、history、rollback 的模块边界
2. 定义结构化 patch 协议
   - 输入是整份演员档案上下文
   - 输出必须是字段级 patch，而不是自由文本
   - 明确哪些字段允许 AI 修改，哪些字段只能建议不能写回
   - patch 只能覆盖 `intro` 与 `work_experience_description`
   - 拍摄经历必须使用稳定 `fieldKey`，不能使用数组下标
3. 组装上下文与执行策略
   - 聚合演员基础资料、经历、自我介绍、技能、照片摘要等字段
   - 接入实名认证、等级能力、配额信息作为执行前置
   - 需要时接入命理或模板相关上下文时也必须有边界
4. 固化配额与失败处理
   - 配额查询
   - 成功后扣减
   - 超时 / 敏感词 / 不可解析响应回滚
   - 日志中记录失败原因与调用结果
5. 固化历史与回滚
   - 返回本次 patch 的 `draftId`
   - 提供历史列表与回滚能力
   - 审计应用动作与回滚动作
6. 对齐档案真实写库入口
   - `/ai/polish-resume` 只产出草稿，不直接写演员档案
   - `PUT /api/actor/profile` 需要接收 `aiResumeApplyMeta`
   - 历史只在演员档案保存成功后固化

## 8. 依赖项

- 编辑页字段模型和允许 AI 修改的字段边界要先冻结
- 等级 / 配额 / 会员态如果共同影响 AI 能力，需要确定唯一权威来源
- 后台至少要预留异常样本和配额策略的治理入口，否则后端难以长期运营
- actor 档案保存链路与 AI 草稿固化链路必须一起设计，避免形成 `/ai/*` 与 `/actor/profile` 双写

## 9. 验证方式

- `GET /api/ai/quota?type=resume_polish` 或最终等效接口返回服务端权威配额
- `POST /api/ai/polish-resume` 返回可解析的字段级 patch，而非自由文本
- `POST /api/ai/polish-resume` 只返回草稿，不直接修改演员档案
- 超时、敏感内容、不可解析响应能返回明确错误并不误扣配额
- `GET /api/ai/resume-polish/history` 可查看历史
- `POST /api/ai/resume-polish/history/{id}/rollback` 可回滚并记录日志

## 10. 完成定义

- 后端存在独立 AI 模块与稳定契约
- 配额、patch、失败兜底、历史回滚都由后端权威控制
- 前端不再依赖 mock 接口模拟 AI 成功
- AI 调用和写回动作可追溯
- 后端可以支撑编辑页真实 AI 协作闭环

## 11. 风险与备注

- 当前后端没有任何独立 AI controller / service，这不是“缺一点”，而是整条后端 AI 主线尚未落地
- 现有 `ActorProfileController`、`FortuneController` 本身也是空壳，说明档案上下文和命理数据都还没有可直接复用的演员端聚合接口
- 若先让前端假定 patch 协议、配额规则和错误码，后续真实后端接入时会产生整层返工
- 若让 `/ai/polish-resume` 直接写档案，再保留 `PUT /actor/profile` 保存入口，会形成双写与历史错账
