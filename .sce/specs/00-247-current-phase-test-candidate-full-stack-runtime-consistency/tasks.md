# 测试候选全栈运行态一致性与演员卡生成约束修复 - 任务

- [x] T1 读取 `00-245/00-246/00-243`、错误登记、生成服务和数据库迁移。  
  **Validates: Requirements 3.1-3.2**
- [x] T2 通过微信内部 MCP 复现 `pkg-actor-card/generate/index?cardId=1` 页面错误。  
  **Validates: Requirements 3.1, 3.4**
- [x] T3 从测试后端日志取得精确 MySQL 异常，确认不是生成页前端问题。  
  **Validates: Requirements 3.1**
- [x] T4 读取 `kaipai_test` DDL、Candidate 内嵌迁移和测试容器 JAR 身份。  
  **Validates: Requirements 3.1-3.2**
- [x] T5 扩展人工验收准入脚本及测试，要求全栈运行证明。  
  **Validates: Requirements 3.2, 3.4**
- [x] T6 备份 `kaipai_test`，按顺序应用迁移并部署 Candidate 后端到测试容器。  
  **Validates: Requirements 3.3**
- [x] T7 通过 MCP 重试演员卡生成并核对测试日志、API 和生产未变。  
  **Validates: Requirements 3.4, 4, 5**
- [x] T8 更新 `00-236/00-243/00-247` 执行记录和完整验证证据。  
  **Validates: Requirements 4, 5**
