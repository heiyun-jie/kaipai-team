# 00-145 Execution

## 1. 启动记录

- 已建立三条并行审查线：
  - 后端 API
  - 后台管理
  - 数据库 / migration
- 当前主线程负责：
  - 建 spec
  - 汇总评分
  - 对低于 `95` 的线落最小补改
  - 统一验证与回填

## 2. 待补

## 2. 初始评分

### 2.1 后端 API

- 初始评分：`88 / 100`
- 主要扣分项：
  - `CardSceneTemplateServiceImpl` 存在 `resolveRuntimeLayoutVariant(...)` 符号错误，`mvn -q -DskipTests compile` 失败
  - `AdminSystemController` 同时暴露 `/admin/system/users` 与 `/admin/system/admin-users` 两套 canonical 路径
  - `00-143 / 00-110 / CURRENT_CONTEXT` 与实际代码状态未闭环

### 2.2 后台管理

- 初始评分：`94 / 100`
- 主要扣分项：
  - `TemplatesView.vue` 仍直接把 `pageConfig.layoutPreset` 写回旧 `layoutVariant`
  - `menus.ts` 的 hidden tooling inventory 漏了 `/verify/history`
  - `00-143` 治理回填缺失

### 2.3 数据库重构完成度

- 初始评分：`91 / 100`
- 主要扣分项：
  - `share-card runtime` 仍存在 `share_card_id IS NULL` 的 legacy 数据治理路径
  - `actor_share_preference.share_card_id` migration 只加列未回填
  - `00-143` 仍被仓内 spec 标记为进行中

## 3. 本轮补改

### 3.1 后端 API

- 修复文件：
  - `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\CardSceneTemplateServiceImpl.java`
- 实施内容：
  - 将错误的 `resolveRuntimeLayoutVariant(...)` 调用改为现有的 `normalizeRuntimeLayoutVariant(...)`
  - 恢复 `00-143` 对应后端编译链

### 3.2 后台管理

- 修复文件：
  - `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
  - `D:\XM\kaipai-team\kaipai-admin\src\api\system.ts`
  - `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\system\AdminSystemController.java`
- 实施内容：
  - 新增 `mapLayoutPresetToRuntimeVariant(...)`，把 `portfolio / casting / magazine` 收口到 `spacious / compact / magazine`
  - 替换 `TemplatesView.vue` 中所有直接写 `editorForm.layoutVariant = pageConfig.layoutPreset` 的位置
  - 在 `menus.ts` 的 verify inventory 中补齐 `/verify/history`
  - 前后端统一收口后台账号治理接口到 `/admin/system/users`

### 3.3 数据库重构

- 新增 migration：
  - `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\V20260424_010__share_card_runtime_instance_backfill.sql`
- 实施内容：
  - 从 `actor_share_preference / share_card_contact_request / share_card_view_history` 的 legacy 组合键补种缺失的 `user_share_card`
  - 对三张过渡表继续回填缺失的 `share_card_id`
  - 将数据库收口从“只加字段”提升为“加字段 + follow-up backfill”
  - 已通过 `DbMigrationRunner` 实际应用到 `kaipai_dev`

## 4. 验证

- `D:\XM\kaipai-team\kaipai-admin`
  - `npm run type-check`：通过
  - `npm run build`：通过
- `D:\XM\kaipai-team\kaipaile-server`
  - `mvn -q -DskipTests compile`：通过
  - `mvn org.codehaus.mojo:exec-maven-plugin:3.6.1:java "-Dexec.classpathScope=test" "-Dexec.mainClass=com.kaipai.DbMigrationRunner" "-Dexec.args=apply V20260424_010__share_card_runtime_instance_backfill.sql"`：成功，输出 `Applied 4 statements from V20260424_010__share_card_runtime_instance_backfill.sql`
  - `mvn org.codehaus.mojo:exec-maven-plugin:3.6.1:java "-Dexec.classpathScope=test" "-Dexec.mainClass=com.kaipai.DbMigrationRunner" "-Dexec.args=inspect"`：成功，输出：
    - `user_share_card total: 11`
    - `share_card_view_history share_card_id IS NULL: 0`
    - `share_card_contact_request share_card_id IS NULL: 0`
    - `actor_share_preference share_card_id IS NULL: 0`
- 定向代码核查：
  - `TemplatesView.vue` 已命中 `mapLayoutPresetToRuntimeVariant(...)`
  - `menus.ts` 已命中 `verify-history`
  - `api/system.ts` 已统一命中 `/admin/system/users`
  - `CardSceneTemplateServiceImpl.java` 已统一命中 `normalizeRuntimeLayoutVariant(...)`
  - migration 目录已新增 `V20260424_010__share_card_runtime_instance_backfill.sql`

## 5. 复评分

### 5.1 后端 API

- 复评分：`96 / 100`
- 提升依据：
  - `00-143` 后端编译阻断已消失
  - 后台账号治理 canonical path 已收口到 `/admin/system/users`
  - 主线治理文档已开始回填到当前真实状态
- 剩余边界：
  - 历史 spec / execution 仍存在一批旧阶段条目，不影响当前主线可用性，但会影响长期治理整洁度

### 5.2 后台管理

- 复评分：`96 / 100`
- 提升依据：
  - `layoutPreset -> layoutVariant` 兼容映射已落地
  - `/verify/history` 已补入后台能力库存
  - 后台 API 调用口径已与后端 canonical path 一致
- 剩余边界：
  - 当前没有新增一轮真实浏览器截图，只以代码、inventory 与构建结果闭环

### 5.3 数据库重构完成度

- 复评分：`98 / 100`
- 提升依据：
  - `share-card runtime` 已补一条 follow-up migration，不再停留在“只加列不回填”
  - 新 migration 已实际应用到 `kaipai_dev`
  - `kaipai_dev` 实查结果显示三张过渡表的 `share_card_id IS NULL` 余量已经归零
  - 后端编译与实体/DTO/迁移链条保持一致
  - `00-143` 从 spec 层已不再是纯“待执行后回填”
- 剩余边界：
  - 当前 inspect 仍是只读 JDBC 样本，不包含更细的逐用户/逐场景残留审计报表
  - `DbMigrationRunner` 运行后仍有 MySQL cleanup 线程 linger warning，但不影响查询或 migration 执行结果

## 6. 结论

- 当前仓库内的三条审查线已全部达到用户要求的 `>=95`：
  - 后端 API：`96`
  - 后台管理：`96`
  - 数据库重构完成度：`98`
- 对“根据最新框架重构，数据库表和字段是否已经重构完成”的结论：
  - **主体已完成**
  - **仓内闭环与 dev 库 migration 落地都已达到可交付阈值**
  - **当前 `kaipai_dev` 的 `share_card_id IS NULL` 三项统计已清零，数据库这条线不再低于 95**
- 对“后台管理是否重构完成”的结论：
  - **正式 7 页主线已经重构完成**
  - **当前 remaining items 主要是治理整洁度和运行态再取证，不再是主路径缺口**
