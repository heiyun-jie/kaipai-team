# 技术设计

## 1. 根因证据
- mine/index.vue 只取 currentUser.avatar；edit.vue 取 avatarAssetId 并调用现签 API。saveProfile 只保存档案，未同步个人页照片。
- 账号会话 nickName 来自 user.user_name，档案 publicName 来自 actor_profile.nick_name，两者已有独立存储。

## 2. 实现
- ActorProfileMineUpdateDTO 增加可选 nickname（1..64、不可全空）；ActorProfileRespDTO 增加 nickname。
- ActorProfileWriteServiceImpl 读账号昵称，saveMine 在档案乐观锁与头像归属校验通过后同事务更新账号昵称。旧请求 null 不写账号。失败不返回成功。
- edit.vue 输入绑定 draft.nickname，纳入 dirty/baseline 和回填；保存成功只更新昵称缓存，不持久化头像签名。
- mine 页每次 onShow 获取本人档案并现签头像，序号+账号ID+会话token保护异步回写，退出清空；图片失败可回退账号头像。
- 测量节点移到三个标准 cell 行，删除旧三列专用布局。

_Requirements: 2.1, 2.2, 2.3_

## 3. 验证
昵称独立存储/旧请求不写/空昵称/账号更新失败测试；前端 type-check、mine和TDesign既有门禁、build:mp-weixin 与固定 dev 检查；发版风险写入 execution.md。

## 4. 2026-10-20 完整度与统计区退场
- 删除 mine/index.vue 中 completeness 卡片、stats-row 模板、loadCompleteness / goCardList / goAssets 及对应样式；资料卡下边距由 24rpx 调为 36rpx，与分组间距一致。
- 删除前端死代码 `getProfileCompleteness` 与 `ProfileCompletenessDTO`（全仓仅个人页消费）。后端接口不删，避免旧前端 500。
- `verify-v3-mine.mjs` 原“统计跳转 / 完整度重试 / 统计卡尺寸”三条断言改为“完整度与统计不得出现”的反向断言。

_Requirements: 2.3_
