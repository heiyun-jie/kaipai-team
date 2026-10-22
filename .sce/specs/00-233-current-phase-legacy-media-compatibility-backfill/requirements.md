# 00-233 历史媒体数据兼容回填

> 状态：Spec 完成，实施未开始
>
> 上游：`00-230`、`00-231`、`00-232`；下游：`00-235`、`00-236`、`00-237`

## 1. 概述

本 Spec 负责把历史用户保存在 `user.avatar_url`、`actor_profile.avatar_url`、`actor_profile.photo_urls`、`actor_profile.video_url` 的媒体兼容到 `actor_media_asset` 和 `actor_profile_asset`，同时保留旧字段，保证旧、新小程序版本都可继续使用已有数据。

## 2. 用户故事

作为老用户，我希望升级后原头像、生活照片和视频仍可见、可选、可继续编辑，不需要重新上传。

作为运维人员，我希望回填可 dry-run、可中断续跑、可审计且不会重复复制或删除旧对象。

## 3. 功能需求

### 3.1 完整盘点历史来源

**验收标准**：

- WHEN 执行 dry-run THEN 扫描 user/profile 两处头像、照片 JSON 和视频 URL。
- WHEN 同一 URL 在多个来源重复 THEN 按用户、来源类型和 URL SHA256 去重，同时保留需要建立的关系。
- WHEN 照片 JSON 无效、URL 非 HTTPS 或 host 不受信任 THEN 进入异常清单，不静默跳过。
- WHEN 生成报告 THEN 只记录哈希、类型、计数和内部 id，不记录完整 URL 或 PII。

### 3.2 验证并复制媒体对象

**验收标准**：

- WHEN 处理历史 URL THEN 验证对象存在、媒体类型、大小和可读取性。
- WHEN 在测试环境执行 THEN 对象只能写测试 private bucket。
- WHEN 在生产执行 THEN 对象只能写正式 private bucket。
- WHEN 复制完成 THEN 新对象 key 可由稳定迁移键追溯，且不与普通用户上传冲突。

### 3.3 创建新素材及关系

**验收标准**：

- WHEN 对象复制成功 THEN 创建 `actor_media_asset`，状态为 `ready`、来源为 `migration`。
- WHEN 来源是头像 THEN 设置 `actor_profile.avatar_asset_id`，头像优先级为 profile URL 高于 user URL。
- WHEN 来源是照片/视频 THEN 创建 `actor_profile_asset` 的 `public_photo` / `public_video` 关系并保留原排序。
- WHEN 原记录无 actor profile THEN 不伪造 profile，进入可解释异常清单。

### 3.4 保证幂等与可恢复

**验收标准**：

- WHEN 同一批次重跑 THEN 不重复复制对象、不重复创建 asset、不重复创建关系。
- WHEN 单项处理中断 THEN 下次从状态记录继续，已完成项不回滚。
- WHEN asset 已存在但关系缺失 THEN 只补关系。
- WHEN 关系已存在但目标对象不可访问 THEN 输出 drift 并阻断正式发布。

### 3.5 保留旧客户端兼容

**验收标准**：

- WHEN 回填完成 THEN 旧 URL 字段保持原值，不删除、不清空、不替换。
- WHEN 旧客户端读取资料和旧分享页 THEN 继续得到原合同。
- WHEN 新客户端读取素材库和资料编辑页 THEN 得到对应 ready asset 和短时访问地址。
- WHEN 用户后续删除新素材 THEN 不得删除仍由旧 URL 指向的原公有对象。

### 3.6 输出可签收证据

**验收标准**：

- WHEN dry-run 完成 THEN 输出总数、可迁移数、异常数、重复数和预计字节数。
- WHEN apply 完成 THEN 输出创建对象、asset、关系、跳过和失败计数。
- WHEN 任一有效历史媒体未兼容 THEN 阶段结论为 `NO-GO`。

## 4. 非功能需求

- 处理日志不得泄漏 URL 查询参数、COS 签名、手机号或用户姓名。
- 支持限速、重试和断点续跑，避免占满服务器带宽。
- 回填不会调用素材删除接口，不修改旧分享卡快照。

## 5. 约束条件

- 不能只向 `actor_media_asset` 写原公有 bucket/object key；否则新素材删除可能删除旧字段仍引用的对象。
- 不允许纯 SQL 根据 URL 字符串猜测对象有效性和 MIME。
- 测试通过后，生产必须使用同一工具版本和同一规则配置。
