# 00-243 测试候选发布与人工测试就绪 - 技术设计

_Requirements: 3.1-3.5, 4, 5_

## 1. 候选链路

```text
commit + explicit overlays
  -> candidate-manifest.json
  -> isolated artifact build
  -> artifact-evidence.json
  -> refreshed candidate manifest
  -> test-only remote staging
```

测试发布只消费 `backend-jar`、`admin-dist` 和 `mini-program-test`。`mini-program-release` 只用于证明生产目标构建自洽，不执行上传。

## 2. 测试侧发布边界

远端候选暂存目录固定为 `/home/kaipaile/test-release/{candidateId}`。root 入口执行前校验 JAR、后台文件数量/字节、部署脚本 SHA256，并记录生产与测试容器指纹。

`provision-test-environment.sh` 只允许修改：

- `/opt/kaipai/test`
- `/opt/kaipai/nginx/html-test`
- `/etc/nginx/conf.d/kaipai-test.conf`
- `kaipai-backend-test`

生产 `kaipai-backend` 只读回查，指纹变化立即失败。

## 3. Bash 捕获值生命周期

`BASH_REMATCH` 是最近一次 `[[ value =~ regex ]]` 的全局匹配结果。COS bucket 捕获值必须在该匹配分支中立即复制到 `prod_cos_appid`，然后才能执行微信 AppID 正则。回归测试以源码顺序断言该约束，并执行 `bash -n`。

## 4. 小程序切换

候选测试产物先做 API 目标扫描和目录树校验，再更新固定工程 `kaipai-frontend/dist/dev/mp-weixin`。微信开发者工具运行时不调用会终止进程、清全局缓存、前台激活或键鼠控制的操作。

文件级切换不能单独作为运行态已切换的证明。切换后必须按顺序执行：

1. 使用微信 CLI 对固定 `dist/dev/mp-weixin` 工程执行项目级 `cache --clean compile`，不得清理其他工程或全局缓存。
2. 通过内部模拟器接口重新打开目标页并刷新，不操作桌面窗口。
3. 扫描该工程新生成的 `WeappCompileCache`：测试 API 至少命中一次，本地 API 和正式 API 均为 `0`。
4. 触发一个需要鉴权的实时接口，并从页面状态或服务端证据确认响应来自测试环境。

如果磁盘产物已是测试地址，但编译缓存仍命中本地地址，则状态保持 `RUNTIME_NOT_SWITCHED`，不得进入人工验收。

完成目录切换、项目级缓存清理、内部刷新和实时请求后，必须生成 `records/<candidateId>/00-243/runtime-readiness.json`，字段合同见 `00-246 design`。随后执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/verify-test-miniapp-acceptance.py --candidate-id <candidateId>
```

只有输出 `READY_FOR_MANUAL_ACCEPTANCE` 且退出码为 `0`，本 Spec 才能记录 `PASSED / AWAITING_MANUAL_ACCEPTANCE`。`dist/build` 新于候选、`dist/dev` 仍是旧候选或仅有缓存文字记录时均不能继续验收。

## 5. 验证与回滚

- 基线：记录旧测试容器指纹、正式容器指纹、旧测试 JAR 和本地固定工程摘要。
- 修改态：验证候选 JAR、容器配置、公网三入口、双环境预检和小程序目录树。
- 回滚测试：在另一个副本执行补丁反向应用，确认恢复旧捕获顺序及原始 SHA256；实际部署保持修改态。
- 运行态回滚使用 `rollback-test-environment.sh` 和候选备份目录，只作用于测试侧。
