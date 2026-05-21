# 00-143 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`
- 已确认当前主线继续沿后台模板配置闭环推进

## 2. 实现前证据

- `TemplatesView.vue` 已支持 `pageConfig` 可视化编辑，但此前仍直接把 `pageConfig.layoutPreset` 写回 `editorForm.layoutVariant`，未做旧运行时兼容映射。
- `ActorSceneTemplateRespDTO` 已有 `pageConfig` 字段，`CardSceneTemplateServiceImpl` 也已开始解析 `artifactPresetJson.pageConfig`，但此前后端存在 `resolveRuntimeLayoutVariant(...)` 符号错误，编译失败。
- `CURRENT_CONTEXT / README / spec-code-mapping` 此前均未把 `00-143` 回填为当前阶段运行时闭环线。

## 3. 本轮实施

- 后端：
  - `ActorSceneTemplateRespDTO` 保持 `pageConfig` 合同承接。
  - `CardSceneTemplateServiceImpl` 修正 `layoutPreset -> layoutVariant` 兼容归一调用，消除编译阻断。
- 后台管理：
  - `kaipai-admin/src/views/content/TemplatesView.vue` 新增 `mapLayoutPresetToRuntimeVariant(...)`，将 `portfolio / casting / magazine` 收口到旧运行时可承接的 `spacious / compact / magazine`。
  - 所有 `editorForm.layoutVariant = pageConfig.layoutPreset` 的直写点均改为兼容映射。
- 运行时闭环治理：
  - `README / spec-code-mapping / CURRENT_CONTEXT` 补登记 `00-143`。
  - `00-110 formal-page-backend-binding-matrix` 同步到当前正式页事实，不再把 `/users/orgs` 记作正式页，也不再把 `operation-logs` 写成事实源异常。

## 4. 验证结果

- `D:\XM\kaipai-team\kaipai-admin`
  - `npm run type-check`：通过
  - `npm run build`：通过
- `D:\XM\kaipai-team\kaipaile-server`
  - `mvn -q -DskipTests compile`：通过
- 关键代码核查：
  - `TemplatesView.vue` 已命中 `mapLayoutPresetToRuntimeVariant(...)`
  - `AdminSystemController.java` 与 `kaipai-admin/src/api/system.ts` 已统一使用 `/admin/system/users`
  - 新增 migration：`V20260424_010__share_card_runtime_instance_backfill.sql`

## 5. 结论

- `00-143` 当前可以视为已完成“后台配置器 -> 后端 DTO -> 运行时 pageConfig 合同”这一条闭环。
- 当前剩余边界主要不再是代码缺口，而是：
  - 新 migration 需要在目标库实际执行后，才能完全验证 legacy `share_card_id` 数据是否已清零
  - 若后续发现运行时 page-level 显示仍有偏差，应回到 `00-144 / 00-145` 分线继续审查，而不是回退 `00-143` 的合同层
