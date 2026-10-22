# 登录页协议勾选框视觉对齐 - 任务清单

- [x] T0 对照截图、页面源码和 TDesign 1.16.0 内部结构确认双圆根因。  
  **Validates: Requirements 2.1**
- [x] T1 建立专项 Spec 和红灯门禁。  
  **Validates: Requirements 2.1-2.3**
- [x] T2 移除 checkbox 宿主圆框，改用 TDesign 本地 SVG 图标数组统一未选与选中态。  
  **Validates: Requirements 2.1, 2.2**
- [x] T3 构建测试产物并核对 src/build/dev。  
  **Validates: Requirements 2.3, 3**
- [x] T4 通过微信内部接口核验未选、选中和协议事件状态。  
  **Validates: Requirements 2.1, 2.2**
- [ ] T5 重新冻结测试产物并回填人工验收候选状态。  
  **Validates: Requirements 2.3, 3**

## 当前状态

- [x] 未选中态只显示一个 `32rpx` 浅蓝圆环。
- [x] 选中态显示 `32rpx` 蓝底白勾，协议文案位置不跳动。
- [x] 固定 `dist/dev/mp-weixin` 继续只访问 `https://test-api.kplyyk.com`。
- [ ] `20260826-1625-v3-draft` 已因本次小程序前端字节变化失效；下一版正式人工签收前需重新冻结候选。本项不影响当前测试环境或正式线上运行。
