# 当前阶段后端分层包结构重构调查 Tasks

## 1. 调查基线

- [x] 确认当前 SCE 编号与新增 Spec 名称为 `00-179-current-phase-backend-layered-package-refactor-investigation`。  
  **Validates: Requirements 6**
- [x] 复核后端当前分支、HEAD 和远端同步状态。  
  **Validates: Requirements 3.6**
- [x] 记录远端重构范围 `670aeed..bd598a0`、提交列表和 diff 规模。  
  **Validates: Requirements 3.1, 3.6**
- [x] 统计旧 `module` 路径 rename 数量和当前顶层包 Java 文件数。  
  **Validates: Requirements 3.1, 3.2**

## 2. 重构映射文档

- [x] 沉淀旧 `module/controller` 到新 `controller/admin`、`controller/api` 的迁移规则。  
  **Validates: Requirements 3.2**
- [x] 沉淀旧 `module/server` 到新 `service`、`mapper`、`integration` 的迁移规则。  
  **Validates: Requirements 3.2**
- [x] 沉淀旧 `module/model` 到新 `model` 的迁移规则。  
  **Validates: Requirements 3.2**
- [x] 记录 MapperScan、MyBatis aliases 和腾讯云配置的新运行态。  
  **Validates: Requirements 3.1, 3.3**

## 3. 关键业务影响

- [x] 记录 `00-178` 腾讯云实名二要素接入在新包结构下的代码落点。  
  **Validates: Requirements 3.3**
- [x] 记录 actor profile 本地 stash 的旧路径和推荐新路径。  
  **Validates: Requirements 3.4**
- [x] 记录后端 `.agents` 文档仍引用旧路径的事实和后续治理边界。  
  **Validates: Requirements 3.5**

## 4. 文档交付

- [x] 创建 `requirements.md`。  
  **Validates: Requirements 6**
- [x] 创建 `design.md`。  
  **Validates: Requirements 6**
- [x] 创建 `tasks.md`。  
  **Validates: Requirements 6**
- [x] 创建 `execution.md`。  
  **Validates: Requirements 3.6, 6**
- [x] 创建 `refactor-audit.md`。  
  **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
- [x] 更新 `.sce/specs/README.md` 增量登记。  
  **Validates: Requirements 6**

## 5. 后续治理任务

- [x] 按新分层结构更新 `kaipaile-server/.agents/*.md` 中的旧 `module` 路径。  
  **Validates: Requirements 3.5**
- [ ] 如继续 actor profile 修复，基于 `stash@{0}` 手工迁移到 `controller/api`、`model`、`service`、`service/support` 新路径。  
  **Validates: Requirements 3.4**
- [x] 如后续需要全局映射可视化，再更新 `.sce/specs/spec-code-mapping.md` 的后端路径说明。  
  **Validates: Requirements 3.1, 3.2**
- [ ] 在下一次后端业务开发前，检查新代码没有重新引入 `src/main/java/com/kaipai/module` Java 文件。  
  **Validates: Requirements 3.1**
