# 00-202 任务拆解

- [x] 建立生产到本地恢复 Spec
- [x] 只读预检生产 `kaipai_prod` 与林夏锚点
- [x] 导出并校验当前本地 `kaipai_dev` 回滚备份
- [x] 通过远程 helper 导出生产 `kaipai_prod`
- [x] 下载并比对远程/本地 SHA256，执行 gzip 校验
- [x] 恢复并验证本地暂存 `kaipai_prod`
- [x] 停止本地后端，重建 `kaipai_dev`
- [x] 验证结构、关键计数和林夏实名资产
- [x] 重启本地后端并执行 HTTP smoke
- [x] 生成 gitignored 执行清单并回填 execution

说明：恢复完成门禁以数据库镜像一致性和 `/api/doc.html=200` 为准。附加业务 smoke 发现当前本地后端源码需要的 12 个职业档案列尚未进入生产 schema，故 `/api/actor/profile/mine` 返回业务码 500；该兼容缺口已记录，但未混入本次原样镜像事务。
