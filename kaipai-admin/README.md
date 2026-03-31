# KaiPai Admin

平台后台管理端独立 Web 工程，服务 `00-11-platform-admin-console` 的 P0 范围。

## 开发命令

```bash
npm install
npm run dev
npm run type-check
npm run build
```

默认本地开发地址为 `http://localhost:5174`，通过 Vite 代理转发到 `http://127.0.0.1:8080/api`。

## 当前已接入

- 后台登录 `/admin/auth/login`
- 登录态查询 `/admin/auth/me`
- 工作台概览 `/admin/dashboard/overview`
- 实名认证列表、详情、通过、拒绝
- 异常邀请列表、详情、通过、作废、标记复核完成
- 会员产品列表、新建
- 会员账户列表、开通、延期、关闭
- 退款单列表、详情、通过、拒绝
- 场景模板列表、新建、基础编辑、发布、回滚
- 后台账号列表、详情、新建、编辑、启停用、重置密码、绑定角色

## 当前已知缺口

- 支付域与退款日志页仍未补前端页面
- 系统管理的角色页与操作日志页尚未补前端页面
- 当前打包后 `index` 主 chunk 超过 Vite 的 `500 kB` 预警线，后续应继续做手动分包或按需拆分 Element Plus
