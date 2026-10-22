# 当前阶段小程序单一测试运行入口 - 任务

- [x] T1 读取 SCE、00-216/219/243/246/251 与共享约定，确认现行双目录链路和入口分叉根因。
  **Validates: Requirements 3.1-3.4**
- [x] T2 创建单一测试运行入口 requirements/design，并登记到 Spec 索引和代码映射。
  **Validates: Requirements 3.1-3.4**
- [x] T3 实现 RuntimeOnly 同步与测试构建前置保护。
  **Validates: Requirements 3.1, 3.2**
- [x] T4 将 package scripts、启动脚本和 MCP 收口到 `dist/dev/mp-weixin`。
  **Validates: Requirements 3.1, 3.3**
- [x] T5 新增单一入口静态门禁，运行类型检查、业务门禁和构建脚本测试。
  **Validates: Requirements 4**
- [x] T6 在副本验证回滚，记录基线/修改/回滚证据；确认生产边界未改变。
  **Validates: Requirements 3.4, 5**
