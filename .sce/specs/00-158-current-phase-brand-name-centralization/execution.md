# 00-158 执行记录

## 2026-05-08 调查

用户要求：

- 分享卡片标题更换为 `开拍了名片`。
- 小程序名称更换为 `开拍了演员卡`。
- 小程序简称为 `开拍了`。
- 创建 specs 调查整个项目哪里需要修改。
- 建议封装为统一取值，便于后续更改。

## 初始结论

代码侧需要处理三类位置：

1. 小程序运行态分享链路：影响微信分享弹窗中的标题、小程序卡片预览、海报品牌、能力中心和认证引导。
2. 后台管理壳层：登录页、侧边栏、系统设置。
3. 后端 API：个性化分享产物返回给前端的 label/title。

微信公众平台侧需要单独处理：

- 微信分享面板底部的小程序官方名称不是本地代码控制。
- 即使本地 `manifest.json` 和 `project.config.json` 修改为 `开拍了演员卡`，正式名称仍需在微信公众平台提交名称/简称变更并通过审核。

## 搜索命令

```powershell
rg -n "剧名片|演员名片|小程序卡片|分享小程序|关于开拍了|开拍了优先|名片能力中心" .\kaipai-frontend\src .\kaipai-admin\src .\kaipaile-server\src -S --hidden --glob '!**/node_modules/**'
rg -n "projectname|\""name\""\s*:" .\kaipai-frontend\project.config.json .\kaipai-frontend\project.private.config.json .\kaipai-frontend\dist\dev\mp-weixin\project.config.json .\kaipai-frontend\dist\build\mp-weixin\project.config.json .\kaipai-frontend\src\manifest.json -S
```

## 待验证

- `npm run build:mp-weixin`
- `npm run type-check` 或按当前项目约束进行最小 TypeScript 校验
- 后端编译或定点 Java 编译检查

## 2026-05-08 实施

新增集中配置：

- 小程序：`kaipai-frontend/src/config/brand.ts`
- 后台：`kaipai-admin/src/constants/brand.ts`
- 后端：`kaipaile-server/src/main/java/com/kaipai/module/server/card/support/BrandCopySupport.java`

主要运行态替换：

- 小程序分享页 `pkg-card/actor-card/index.vue`：微信分享标题从动态拼接的 `...小程序卡片` 改为统一 `开拍了名片`。
- 小程序分享产物、认证提示、能力中心、关于页等核心文案改为读取 `MINI_PROGRAM_BRAND`。
- 后台登录页、侧边栏、系统设置、分享产物配置页改为读取 `ADMIN_BRAND`。
- 后端个性化分享产物 label/title 改为读取 `BrandCopySupport`。
- 小程序 `manifest.json` 名称改为 `开拍了演员卡`，AppID 保持 `wx4dcc4e1066fd0fb9`。
- 构建产物 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 已通过构建同步，`projectname` 为 `开拍了演员卡`。

## 2026-05-08 验证

通过：

```powershell
cd kaipai-frontend
npm run build:mp-weixin
npm run type-check

cd ..\kaipai-admin
npm run type-check
npm run build

cd ..\kaipaile-server
mvn -q -DskipTests compile
```

旧文案残留搜索：

```powershell
rg -n '剧名片|小程序卡片|分享小程序|演员名片|开拍了后台|开拍了平台后台' .\kaipai-frontend\src .\kaipai-frontend\dist\build\mp-weixin .\kaipai-frontend\dist\dev\mp-weixin .\kaipai-admin\src .\kaipai-admin\dist .\kaipai-admin\index.html .\kaipai-admin\.env.development .\kaipai-admin\.env.production .\kaipai-admin\.env.test .\kaipaile-server\src\main\java -S --hidden --glob '!**/node_modules/**' --glob '!**/*.map'
```

结果：无命中。

## 平台侧待办

代码已更新本地运行态和构建产物名称，但微信分享面板底部的小程序官方名称仍取决于微信公众平台账号资料。正式显示 `开拍了演员卡` / 简称 `开拍了` 需要在微信公众平台提交名称/简称变更并通过审核。
