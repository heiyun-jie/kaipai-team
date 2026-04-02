# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`20260403-012801-backend-only-auth-runtime-check`
- 发布时间：`2026-04-03 01:28`
- 发布范围：`backend-only`
- 操作人：`codex`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 使用标准发布脚本执行第一次 `backend-only` 真实发布尝试

## 2. 发布前检查

- 目标环境：
  - 远端主机：`101.43.57.62`
  - 后端运行目录：`/opt/kaipai`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本地已切换 `JDK 17`
  - 远端 backend helper / sudoers 已通过 bootstrap 安装
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 backend-only 脚本发布`

## 3. 执行摘要

- 本地构建：`mvn -q -DskipTests clean package`
- 本地 jar SHA256：`7395F5CA3A54044CF2FDD663BDC2D8593C3D4D40E817EF3DAC69F0275EEF08F9`
- 远端执行：
  - 上传 jar 到 `/home/kaipaile/backend-release-uploads/20260403-012801-backend-only-auth-runtime-check/`
  - 调用 `sudo -n /usr/local/bin/kaipai-backend-release-helper.sh`
- 是否执行回滚：`否`

## 4. 失败结果

- 最终结论：`中止`
- 失败原因：
  - helper 首版在 `docker compose up -d --force-recreate kaipai` 前未清理当前线上残留的同名旧容器
  - 远端 `docker compose` 返回：`Conflict. The container name "/kaipai-backend" is already in use`
- 影响判断：
  - 本次未完成容器重建，正式 smoke 未执行完成
  - 失败根因属于发布链路实现缺口，不是业务代码结论

## 5. 后续动作

- 已先更新 00-29 runbook 与 backend helper：
  - 在 compose 重建前自动清理残留同名旧容器
- 后续同批继续按同一条标准脚本重跑，不回退手工发布
