# 00-65 执行记录

## 1. 调查结论

- 当前“新增分享卡片”不是真正 create
- 后端 `UserShareCardServiceImpl.createCard(...)` 通过：
  - `findOwnedCard(userId, sceneKey)`
  - `ensureOwnedCard(...)`
  把新增语义降级成了“同风格确保存在一张卡”
- 所以用户新增同风格卡时，最终仍会回到原实例，导致“新增”和“编辑”修改的是同一套存储

## 2. 本轮建档结论

- 新增 `00-65`，单独处理多实例模型重构
- 当前核心改造不是页面小修，而是模板资格与卡片实例解耦
- 编辑页旧会员 / 命理 / audience selector 清理不在本 Spec 中处理

## 3. 待后续实现验证

- 待实现后验证：
  - 同模板连续新增是否产生两个不同 `shareCardId`
  - 两张同模板卡是否能独立编辑与独立分享
  - 后台是否能正确展示同模板多实例

## 4. 本轮输出

- `requirements.md`
- `design.md`
- `tasks.md`
- `execution.md`
