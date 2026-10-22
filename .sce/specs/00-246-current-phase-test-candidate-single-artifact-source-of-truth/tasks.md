# 测试小程序候选单一事实源与人工验收准入 - 任务

- [x] T1 读取 `00-231/00-236/00-243` 与错误登记，确认候选、build、dev 和缓存的现有职责。  
  **Validates: Requirements 3.1-3.4**
- [x] T2 建立 requirements/design，固定 Candidate ID 和状态机。  
  **Validates: Requirements 3.1, 3.4**
- [x] T3 实现只读人工验收准入脚本。  
  **Validates: Requirements 3.1-3.4**
- [x] T4 新增一致、输入漂移、build/dev 漂移、运行证明和篡改测试。  
  **Validates: Requirements 3.1-3.4**
- [x] T5 接入标准发布手册、Spec 索引、代码映射和 errorbook。  
  **Validates: Requirements 3.4, 4, 5**
- [x] T6 运行基线/修改测试，验证当前旧候选返回重冻要求，完成副本回滚证据。  
  **Validates: Requirements 3.2, 3.4, 5**
- [x] T7 生成新 Candidate，从冻结 `mini-program-test` 同源物化 build/dev，并取得真实准入 exit `0`。
  **Validates: Requirements 3.1-3.4, 5**
- [x] T8 由 00-252 将日常构建、审计、MCP 和人工验收收口到固定 `dist/dev/mp-weixin`；隔离 `dist/build` 仅显式诊断或发布使用。
  **Validates: Requirements 3.1-3.4, 4**
