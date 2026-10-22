# 测试环境小程序微信登录配置 - 任务清单

- [x] T0 建立专项 Spec 并确认测试容器缺少两项微信变量。  
  **Validates: Requirements 2.1, 2.2**
- [x] T1 更新测试 provisioning，固化微信配置成组注入与脱敏门禁。  
  **Validates: Requirements 2.1, 2.2**
- [x] T2 备份并配置测试 Nacos 与 test-secrets.env。  
  **Validates: Requirements 2.1, 2.2**
- [x] T3 只重建测试容器并验证运行时哈希。  
  **Validates: Requirements 2.2, 2.4**
- [x] T4 运行无效 code、API docs、双环境不变量 smoke。  
  **Validates: Requirements 2.3, 2.4**
- [x] T5 生成脱敏证据和可执行回滚工件，回填 `00-236`。  
  **Validates: Requirements 3**
