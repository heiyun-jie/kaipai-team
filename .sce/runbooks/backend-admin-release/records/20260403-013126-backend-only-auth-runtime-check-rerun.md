# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`20260403-013126-backend-only-auth-runtime-check-rerun`
- 发布时间：`2026-04-03 01:31`
- 发布范围：`backend-only`
- 操作人：`codex`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 使用修正后的标准发布脚本执行第二次 `backend-only` 真实发布尝试

## 2. 发布前检查

- 目标环境：
  - 远端主机：`101.43.57.62`
  - 后端运行目录：`/opt/kaipai`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - helper 已补“同名容器清理”
  - compose 重建可执行
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 backend-only 脚本发布`

## 3. 执行摘要

- 本地构建：`mvn -q -DskipTests clean package`
- 本地 jar SHA256：`EA3E9EC2C0682B53493CB3848F7B9B22B835316005245ECD792EB03819854925`
- 远端执行：
  - 上传 jar 到 `/home/kaipaile/backend-release-uploads/20260403-013126-backend-only-auth-runtime-check-rerun/`
  - helper 已成功完成 compose build / up
- 是否执行回滚：`否`

## 4. 失败结果

- 最终结论：`中止`
- 失败原因：
  - helper 第二版仍使用固定 `sleep 8` 后立即探测 `/api/v3/api-docs`
  - 当前 Spring Boot + Nacos 冷启动实际耗时约 `20+ 秒`，导致 docs 探针过早触发 `connection reset by peer`
  - 同批回读容器日志后已确认服务随后正常启动，并不是业务运行时崩溃
- 影响判断：
  - 本次失败根因仍属于发布链路实现缺口，不是后端业务接口继续 `500`
  - 该次尝试证明需要把固定短等待升级为“带超时的就绪轮询”

## 5. 后续动作

- 已先更新 00-29 Spec / runbook 与 backend helper：
  - `R16.1` 明确基础入口探活必须带超时轮询
  - helper 改为对 `/api/v3/api-docs` 执行最多 `60s` 级别的就绪等待
- 后续同批继续按同一条标准脚本重跑，不回退手工发布
