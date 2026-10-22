# 执行记录

## 2026-10-13 本地修复

反馈红框定位“修改分类”，具体“点后无选项 / 保存不生效 / 修改分类名称”仍待用户补充。已修复源码与组件事件序列证明的缺陷，不据截图重造分类字典。

TDesign 1.16.0 ActionSheet onSelect 依次发出 `selected → close(trigger=select) → visible-change(false)`。原页面在 selected 回调里重开同一弹层，随后的 close 与 visible-change 把分类菜单立刻关掉。

现在素材操作菜单与分类选择菜单各持独立 visible、items 与回调；上一级关闭事件只关闭上一级。分类保存增加 busy 锁、成功 toast 与列表刷新、失败 toast 与可重试；游客/退出后的旧请求不产生成功提示。没有定时器延迟，也没有修改分类 code 或 API。

| 检查 | 结果 |
|------|------|
| 真实页面脚本按组件事件顺序回归 | 上级三个事件发完后分类弹层仍显示 |
| 保存失败后重试 / 防双提交 / 退出后旧响应 | 通过（合并 10 项专项） |
| TDesign / 三列网格 / 游客状态门禁 | 固定 dev 865 / 34 / 13 项通过 |
| type-check / 固定 dev 构建 / 单入口门禁 | 通过 |
| 固定 dev assets WXML | 两个独立 t-action-sheet，回调分别绑定 |
| 包体 / steering 审计 | 通过 |

保留预览、重命名、删除、PDF 管理分支与三列照片布局；这些分支的静态合同通过，不代替本轮真机逐项点击验收。

只改前端交互，零数据库/接口变更。详细分类预期、真机管理操作、新 Candidate 验收待补；未部署、上传或发布。

## 2026-10-20 “修改后没有生效”根因与修复

用户补充现象：修改分类后没有生效。

- 证据：测试环境冻结产物 `.sce/runbooks/backend-admin-release/records/20260901-221652-v3-draft/00-231/artifacts/mini-program-test/pages/assets/index.js` 的 `changeCategory` 仍复用同一 ActionSheet（`actionSheetMode = "category"`），`applyCategory` 无 toast。用户测试的是该旧版本，本地 10-13 修复未进入测试环境。
- 后端写入链路核对无缺陷（见 design §4），不改后端。
- 新增修复：照片分类角标、弹层“当前分类”说明与当前项标记、同值选择不提交。

| 检查 | 结果 |
|------|------|
| `npm run verify:feedback-october` | 14/14（新增：当前分类标记 + 保存后照片标签跟随新值；同值不提交） |
| 反向注入：删除角标与同值守卫 | 新增 2 项均失败；还原后 14/14 |
| `npm run type-check` | 通过 |
| `npm run build:mp-weixin` | `RUNTIME_BUILD=PASS`，assets wxml/wxss 哈希均 `80c30605` |
| 固定 dist/dev assets | wxml 含 `assets-page__photo-category`；js 含 `description: categorySheetDescription.value`、“当前分类”“（当前）”；wxss 含角标样式 |
| `audit:mp-package` / `audit:steering` / `verify:v3-home` | 通过 / 通过 / 17 项 |

零后端/DB/API 变更。真机验收必须在新 Candidate 部署测试环境后进行；未部署、未上传。
