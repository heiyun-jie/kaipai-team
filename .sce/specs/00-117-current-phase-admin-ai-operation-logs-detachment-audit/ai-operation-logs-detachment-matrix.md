# 00-117 AI / operation-logs 脱钩矩阵

| 对象 | 路径 / 文件 | 当前职责 | 与 AI 主链关系 | 当前判断 | 下一步口径 |
|------|-------------|----------|----------------|----------|------------|
| AI 管理接口 | `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\ai\AdminAiResumeController.java` | AI 治理 runtime API | 直接依赖 `page.system.ai-resume-governance` 与 `action.system.ai-resume.*` | **AI runtime direct dependency** | 保留；不涉及 operation-logs 退场 |
| AI 矩阵后端 | `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java` | 统计 AI 权限与历史耦合 | 仅用 `page.system.operation-logs` 做历史耦合维度 | **AI historical coupling display** | 保留；继续作为审计维度 |
| AI 矩阵前端 | `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` | 展示 AI 权限矩阵与权限包提示 | 只展示 operation-logs 历史耦合，不承接 runtime fallback | **AI historical coupling display** | 保留；若后续继续精修，可再清理 stage enum 命名 |
| 系统设置 AI 摘要 | `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue` | 聚合 AI 治理入口摘要 | 读取 AI 矩阵中的历史耦合计数 | **AI historical coupling display** | 保留；不构成 AI runtime 依赖 |
| 操作留痕审计页 | `D:\XM\kaipai-team\kaipai-admin\src\views\system\OperationLogsView.vue` | 独立审计 hidden tooling 页 | 不承担 AI runtime，但仍是独立审计页 | **Operation-logs independent hidden tooling** | 保留；若继续推进，应单独围绕事实源修复或保留策略建切片 |
| 操作留痕路由 | `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts` -> `/system/operation-logs` | hidden tooling route | 与 AI 主链已脱钩 | **Operation-logs independent hidden tooling** | 保留；不可因 AI 脱钩而顺手删除 |
| 操作留痕菜单项 | `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts` -> `system-operation-logs` | hidden tooling 菜单库存 | 与 AI 主链已脱钩 | **Operation-logs independent hidden tooling** | 保留；不可因 AI 脱钩而顺手删除 |

## 当前总判断

1. AI runtime：**已脱钩**
2. AI 对 operation-logs 的剩余关系：**只剩历史耦合审计**
3. operation-logs 当前地位：**独立 hidden tooling**
