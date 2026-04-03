# 微信配置门禁 Runbook

> 对应 Spec：
> - `00-29 backend-admin-release-governance`
> - `00-28 invite wxacode execution card`
> - `00-28 login-auth status`

## 1. 目的

把 invite / login-auth 的微信配置门禁收口成一页固定流程，避免再出现以下误判：

- 只因为本地存在 secret 文件，就误判“已具备合法输入”
- 只因为 dry-run 跑过，就误判“远端已可验证”
- 只因为二维码接口返回了图片，就误判“官方 `wxacode` 已闭环”

## 2. 当前固定输入位

- 本地 gitignored secret 文件：
  - `D:\XM\kaipai-team\.sce\config\local-secrets\wechat-miniapp.env`
- 前端固定 appId 来源：
  - `D:\XM\kaipai-team\kaipai-frontend\project.config.json`
- 目标环境：
  - `101.43.57.62`
  - `NACOS_ENABLED=true`
  - `SPRING_PROFILES_ACTIVE=dev`

## 3. 标准顺序

1. 初始化本地 secret 文件
2. 判定本地输入是否合法
3. 跑微信配置总控
4. 执行标准 `backend-only` 重建
5. 复跑远端微信门禁预检查
6. 跑 invite / login-auth 微信真实样本

## 4. 第一步：初始化本地 secret 文件

若本机还没有 gitignored secret 文件，执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/init-local-wechat-secret-file.py
```

结果：

- 会创建 `.sce/config/local-secrets/wechat-miniapp.env`
- 会自动预填当前小程序 `appId`
- 会写入 placeholder secret

注意：

- 这一步只负责建立输入位
- 这一步完成后，门禁通常仍然是 `blocked`
- 未替换真实 `WECHAT_MINIAPP_APP_SECRET` 前，不允许继续宣告“可验证”

## 5. 第二步：判定本地输入是否合法

执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-local-wechat-config-inputs.py --label <label>
```

看以下结论：

- `Release Ready: yes`
- `WECHAT_MINIAPP_APP_ID valid: yes`
- `WECHAT_MINIAPP_APP_SECRET valid: yes`

当前脚本会拒绝以下输入：

- `replace-with-real-app-secret`
- `fake-*`
- `example`
- `dummy`
- `sample`
- 过短 secret

只要命中 `placeholder_secret` 或其他 invalid issue，就仍然属于 `not ready`。

## 6. 第三步：跑微信配置总控

本地输入合法后，执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label>
```

总控固定顺序：

1. `read-local-wechat-config-inputs.py`
2. `read-backend-wechat-config-precheck.py`
3. `run-backend-compose-env-sync.py`
4. `run-backend-nacos-config-sync.py`

说明：

- 第 2 步远端门禁用于固化“同步前事实”
- 不要求同步前远端就已经通过
- 若第 1 步本地输入不合法，总控会直接中止

若只想先看当前阻塞点，再执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label> --dry-run
```

## 7. 第四步：执行标准重建

微信配置来源同步完成后，必须继续执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>
```

原因：

- compose / Nacos 同步不等于运行时已生效
- 当前后端运行时仍需要标准 `backend-only` 重建后，容器 env 与运行 jar 才能统一

## 8. 第五步：复跑远端门禁预检查

重建完成后执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-wechat-config-precheck.py --label <label>
```

目标结论：

- compose source 不再缺 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`
- compose rendered 不再缺
- container env 不再缺
- `kaipai-backend` / `kaipai-backend.yml` / `kaipai-backend-dev.yml` 不再缺对应微信键

只有这一轮通过后，invite / login-auth 才能进入真实微信样本验证。

## 9. 第六步：跑真实微信样本

invite 方向：

- 先按 `wxacode` 执行卡补官方码验证
- 再补“扫码打开 -> 登录页恢复 `inviteCode` -> 注册 / 登录 -> 邀请主链继续闭环”

login-auth 方向：

- 验证 `POST /api/auth/wechat-login`
- 验证老用户登录
- 验证新用户自动注册
- 验证 `inviteCode` 透传

## 10. 当前禁止事项

- 不允许把 placeholder secret 当成真实输入继续总控
- 不允许跳过 `read-local-wechat-config-inputs.py` 直接写 compose / Nacos
- 不允许只做 compose 同步，不做 Nacos 同步就宣告“微信配置已补齐”
- 不允许只做同步，不做 `backend-only` 重建就宣告“线上已生效”
- 不允许只看 `/api/invite/qrcode` 返回 `200` 就宣告“官方 `wxacode` 已闭环”

## 11. 当前最短路径

1. 把真实 `WECHAT_MINIAPP_APP_SECRET` 写入：
   `D:\XM\kaipai-team\.sce\config\local-secrets\wechat-miniapp.env`
2. 执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label>`
3. 执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>`
4. 执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-wechat-config-precheck.py --label <label>`
5. 再跑 invite / login-auth 微信真实样本
