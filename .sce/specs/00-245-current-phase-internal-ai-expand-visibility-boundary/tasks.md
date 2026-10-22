# 任务

- [x] T1 阅读 SCE、共享约定、错误手册及 `00-241/00-242/00-243/00-244`，确认扩图可见性与运行环境边界。  
  **Validates: Requirements 3.1-3.3**
- [x] T2 记录步骤页原始 SHA256，并运行源码/类型基线门禁。  
  **Validates: Requirements 3.4, 4**
- [x] T3 建立专项门禁并收窄步骤页可见 UI，保留隐藏历史字段兼容语义。  
  **Validates: Requirements 3.1, 3.2, 4**
- [x] T4 实现后端自动扩图、稳定来源任务、来源变化失效和失败内部可观测。  
  **Validates: Requirements 3.3, 3.4**
- [x] T5 新增幂等迁移和真实 MySQL 合同测试，验证私有素材任务不持久化签名 URL。  
  **Validates: Requirements 3.3, 3.4, 4**
- [x] T6 构建小程序并核对 `src`、`dist/build`、`dist/dev` 三侧及 scoped hash。  
  **Validates: Requirements 3.5, 4**
- [x] T7 生成新 Candidate、统一物化 build/dev、刷新固定工程运行缓存并取得准入 `exit 0`。  
  **Validates: Requirements 3.5, 4, 5**
- [x] T8 在另一个副本执行回滚脚本并回填验证证据；实际工作区保持修改态。  
  **Validates: Requirements 3.5, 4, 5**
