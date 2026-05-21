# 00-145 设计说明

## 1. 设计目标

本 Spec 的设计目标是把“后端 API、后台管理、数据库重构完成度”从分散判断，变成一条统一但可分解的审查闭环：

1. 先并行取证
2. 再分线评分
3. 对低分线做最小补改
4. 最后统一复评分和回填

## 2. 审查对象

### 2.1 后端 API

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\**`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\**`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\**`
- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\**`

### 2.2 后台管理

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\**`
- `D:\XM\kaipai-team\kaipai-admin\src\views\user\**`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\**`
- `D:\XM\kaipai-team\kaipai-admin\src\views\operate\**`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\**`

### 2.3 数据库重构

- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\**`
- 与正式链路直接相关的 entity / DTO / service / controller

## 3. 评分设计

### 3.1 后端 API

按以下四项给分：

- 正式接口覆盖与收口：`35`
- DTO / service / controller 一致性：`25`
- 历史 fallback / wrapper / 旧语义退场完成度：`20`
- 编译与调用链验证：`20`

### 3.2 后台管理

按以下四项给分：

- 正式导航与 IA 一致性：`30`
- 页面 carrier 与真实接口绑定完成度：`30`
- 历史入口 / fallback / 旧页面退场完成度：`20`
- 构建与运行态证据：`20`

### 3.3 数据库重构

按以下四项给分：

- migration 覆盖与主线匹配：`35`
- 表 / 字段 / entity / DTO 对齐度：`30`
- 历史字段 / fallback 语义退场完成度：`20`
- 编译与消费链验证：`15`

## 4. 并行推进设计

本轮允许并行，但职责必须分开：

- 线程 A：后端 API 审查
- 线程 B：后台管理审查
- 线程 C：数据库与 migration 审查
- 主线程：建 spec、汇总扣分项、落最小补改、统一回填

## 5. 验证设计

- `kaipai-admin`
  - `npm run type-check`
  - `npm run build`
- `kaipaile-server`
  - `mvn -q -DskipTests compile`

若补改触及 DTO / migration / page carrier，则必须重跑相应验证。
