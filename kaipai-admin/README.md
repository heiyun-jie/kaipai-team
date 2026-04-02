# KaiPai Admin

平台后台管理端独立 Web 工程，服务 `00-11-platform-admin-console` 的 P0 范围。

## 开发命令

```bash
npm install
npm run dev
npm run type-check
npm run build
```

默认本地开发地址为 `http://localhost:5174`，前端请求路径固定为相对路径 `/api`。
本地 `vite dev` 默认通过 `VITE_API_PROXY_TARGET=http://127.0.0.1:8010` 代理到本机后端；如需改连其他环境，只改 `VITE_API_PROXY_TARGET`，不要把页面代码里的 `/api` 改成公网绝对地址。
线上构建不走 `5174 -> 127.0.0.1:8010` 这条本地代理链，而是由 nginx 统一承接站点与 `/api` 反代。

## 当前已接入

- 后台登录 `/admin/auth/login`
- 登录态查询 `/admin/auth/me`
- 工作台概览 `/admin/dashboard/overview`
- 实名认证列表、详情、通过、拒绝
- 异常邀请列表、详情、通过、作废、标记复核完成
- 会员产品列表、新建
- 会员账户列表、开通、延期、关闭
- 支付订单列表、详情
- 支付流水列表、详情
- 退款单列表、详情、通过、拒绝
- 退款日志列表
- 场景模板列表、新建、基础编辑、发布、回滚
- 后台账号列表、详情、新建、编辑、启停用、重置密码、绑定角色
- 角色列表、详情、新建、编辑、启停用、复制
- 操作日志列表、详情

## 当前已知缺口

- 角色权限编辑当前按权限码多选维护，尚未做树形权限编排
- 当前打包后 `index` 主 chunk 超过 Vite 的 `500 kB` 预警线，后续应继续做手动分包或按需拆分 Element Plus
