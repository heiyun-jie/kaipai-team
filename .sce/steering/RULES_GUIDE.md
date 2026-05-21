# Steering 规则索引

**职责边界**:
- `CORE_PRINCIPLES.md`：长期原则
- `ENVIRONMENT.md`：项目级规则
- `CURRENT_CONTEXT.md`：当前阶段上下文
- `RULES_GUIDE.md`：迁移与维护规则

**迁移原则**:
- 长期有效 -> `CORE_PRINCIPLES.md`
- 项目运行约束 -> `ENVIRONMENT.md`
- 当前阶段状态 -> `CURRENT_CONTEXT.md`
- 详细制度与示例 -> 项目文档
- 任务、证据、历史 -> 对应 Spec

**治理动作**:
- 定期运行 `cd kaipai-frontend && npm run audit:steering`
- 审计失败时，优先合并重复、迁移错层、归档历史、删除失效内容

## 治理基线（非最高原则）

- 所有需求先落 Spec；所有由 Agent 生成的脚本、报告、诊断、调试日志、测试脚本、临时分析和验证产物默认归档到当前 `.sce/specs/<spec>/` 的对应子目录；没有明确 Spec 时先使用通用 Spec 承接。
- 连续两轮以上仍未成功定位或验证问题时，先在 `errorbook` 记录或更新 incident，再用二分法配合 debug 日志/埋点快速收敛范围，不继续盲改。
- 业务场景未知时先澄清，不得把未知范围直接变成一刀切禁用；修改问题前先建立问题契约和证据，不得靠猜测碰运气。
- 代码、测试、文档必须同步闭环；重要功能、命令、配置变化必须同步更新说明，发布前不得带着失败验证前进。
- Steering 变更先评估；已有机制优先复用，不得在 steering 中平行造轮子，尤其不得再造一套独立于 `errorbook` 的问题沉淀机制。
- 可复用执行经验、阈值、案例和策略，优先写入 `docs/steering-governance.md` 或 `.sce/knowledge/lessons/`，不要回灌到最高原则层。
