# 会员能力与模板配置闭环执行卡

本目录用于承接 `slices/membership-template-capability-slice.md` 的下一层拆分。

## 目标

把“会员能力与模板配置闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡

补充一组用于真实环境验收收口的执行资产：

5. `real-env-runtime-inventory.md`
6. `real-env-validation-checklist.md`
7. `real-env-evidence-pack.md`
8. `validation-sample-ledger-template.md`
9. `collect-membership-evidence.ps1`
10. `new-membership-validation-sample.ps1`
11. `run-membership-validation.ps1`
12. `validation-execution-example.md`
13. `preview-overlay-governance-baseline.md`
14. `verify-card-config-first-save.py`
15. `run-admin-template-rollback-chain.py`
16. `capture-admin-membership-template-screenshots.py`
17. `run-admin-template-rollback-mini-program-chain.py`
18. `run-preview-overlay-static-audit.py`
19. `run-admin-template-rollback-mini-program-no-fortune-theme.py`
20. `preview-overlay-decision-record.md`

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/membership-template-capability-slice.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前必须把“后台管理端比前台更完整、演员端控制器为空、前端 resolver 过重”明确写入执行卡，避免把局部能力误判成闭环

## 工具补充

- `run-membership-validation.ps1` 会自动创建一次 membership 联调样本目录，并调用 `collect-membership-evidence.ps1` 预填运行时台账、样本台账和验证报告
- 自动回填只覆盖仓内可直接抽取的运行时与阻塞事实；真实后台发布记录、小程序页面截图和数据库结果仍需要人工补回同一份样本目录
- 如果小程序证据因为 DevTools / 微信账号授权阻塞而无法生成，也必须把阻塞事实落到样本 `captures`，不能只在状态卡里口头描述“截图待补”
- 当 `cli auto --project ... --auto-port ...` 已恢复后，可用 `capture-mini-program-screenshots.js` 对同一份样本补 `membership / actor-card / detail / invite / fortune` 五页截图，并同步生成 `captures/mini-program-screenshot-capture.json`
- 当会员链路已经收敛到 `level_required` 业务 gating 时，可用 `run-membership-level-unlock.py` 直接补足 `Lv5` 验证样本，并在同一样本目录沉淀 `level.info / card.personalization / DB` 证据
- 当 `/card/config` 曾暴露“首次保存缺 `template_id`”问题时，可用 `verify-card-config-first-save.py` 在同一份样本目录执行“删配置 -> 真登录 -> 首存 -> DB 回读”闭环，并把成功证据与历史失败证据并存
- 当模板已经存在真实发布版本时，可用 `run-admin-template-rollback-chain.py` 在同一份样本目录执行“回滚 -> 前台摘要变化 -> 恢复发布”的成组验证
- 当模板 rollback 的 API / DB 证据还需要映射到真实小程序页面时，可用 `run-admin-template-rollback-mini-program-chain.py` 在同一份样本目录补 `before / after-rollback / after-restore` 三段截图；当前 `Lv5 + fortune theme` 样本里，已证实 `actor-card` 会切换模板文案，但 `detail / invite` 仍会被 `general-member-fortune` 主题覆盖
- 当需要排除 `general-member-fortune` 遮罩并继续验证 rollback 可见性时，可用 `run-admin-template-rollback-mini-program-no-fortune-theme.py` 统一执行“强制关闭 fortune theme -> rollback / restore -> 恢复原偏好”的标准样本；最新样本 `20260403-121415-dev-template-rollback-no-fortune-theme` 已证明 `actor-card / detail / invite` 三页哈希都会随 rollback 改变并在 restore 后恢复，且摘要已直接列出分阶段 `page-data` 文件
- 当同一样本还缺后台 UI 证据时，可用 `capture-admin-membership-template-screenshots.py` 通过本地 `kaipai-admin` + 远端 `/api` 代理补会员账户页、模板页与回滚弹窗截图
- `preview-overlay-governance-baseline.md` 用于固定“未保存 preview overlay”当前允许保留在前端的边界，避免后续再次把它写回分散页面逻辑
- `preview-overlay-decision-record.md` 用于固定当前 overlay 继续保留为 session-only 的决策依据，避免后续没有新证据就反复在“是否立即后端化”之间摇摆
- 当 overlay 边界需要继续确认“query key 是否外溢、session key 是否越界、helper 是否新增到非白名单页面”时，可用 `run-preview-overlay-static-audit.py` 生成一份标准静态审计样本
- `capture-mini-program-screenshots.js` 现已同步保留 `before / after-rollback / after-restore` 三段 `page-data-*.json`，后续 membership 页面级证据不再只有截图哈希和路由
- `run-admin-template-rollback-mini-program-chain.py` 现应在摘要里直接列出各阶段 `page-data` 文件，避免后续人工翻样本目录确认页面数据快照
