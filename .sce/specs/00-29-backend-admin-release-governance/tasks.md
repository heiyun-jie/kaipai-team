# 00-29 发布治理任务

## Workstream A — 治理入口

- [x] T1 新建 `00-29 backend-admin-release-governance` Spec
- [x] T2 补齐 `requirements.md`
- [x] T3 补齐 `design.md`
- [x] T4 补齐 `tasks.md`
- [x] T5 登记到 `.sce/specs/README.md`
- [x] T6 登记到 `.sce/specs/spec-code-mapping.md`

## Workstream B — 运维文档

- [x] T7 新建独立运维文档目录 `.sce/runbooks/backend-admin-release/`
- [x] T8 补齐标准发布手册 `backend-admin-standard-release.md`
- [x] T9 补齐发布证据模板 `backend-admin-release-evidence-template.md`
- [x] T10 建立发布记录目录 `records/`

## Workstream C — 流程固化

- [x] T11 已为 `backend-only` 建立标准发布脚本入口，且脚本仍受 00-29 的阶段门禁和证据要求约束
- [x] T12 已完成一次 `admin-only` 实发布，并落档发布记录
- [ ] T13 后续每次 `backend+admin` 联合发布，都按 runbook 执行并落一份记录
- [ ] T14 若目标环境启动方式、nginx 目录或反代规则变化，先更新 00-29 Spec 与 runbook，再允许继续发版
- [x] T15 已为 `admin-only` 建立标准发布脚本入口，且脚本仍受 00-29 的阶段门禁和证据要求约束
- [x] T16 已补充管理端 Windows -> Linux 发布归档规则，固定为 `tar.gz`
- [x] T17 已补充“执行链路与 runbook 不一致时，必须先更新文档再继续发布”的门禁规则
- [x] T18 已建立 `admin-only` 一次性引导脚本，负责 key auth、helper 与 sudoers 基线安装
- [x] T19 历史阶段：已将 `admin-only` 正式发布链路从 `Paramiko` 收口到 `OpenSSH key auth + scp/ssh + 远端 helper`
- [x] T20 已使用新版标准 `admin-only` 发布脚本完成真实发布，并生成发布记录 `20260403-001021-admin-only-admin-script-publish.md`
- [x] T21 已在目标服务器安装 `Node.js v22.22.2` 与 `npm 10.9.7`，作为后续服务端构建能力增强基线
- [x] T22 历史阶段：已将 `admin-only` 标准主链路切换到“源码归档上传 + 服务端构建 + helper 发布”
- [x] T23 已使用服务端构建版 `admin-only` 标准脚本完成真实发布，并生成发布记录 `20260403-002330-admin-only-admin-server-build.md`
- [x] T24 已为 `admin-only` 建立远端 bare repo，支持 git snapshot 发布
- [x] T25 已使用 git snapshot + bare repo + 服务端检出构建版标准脚本完成真实发布，并生成发布记录 `20260403-004234-admin-only-admin-git-snapshot-clean.md`
- [x] T26 已将 00-29 Spec、runbook、记录模板统一收口到当前 `git snapshot -> bare repo -> 服务端检出构建 -> helper 发布` 主链路
- [x] T27 已为本地后端构建补齐 JDK 17 基线，并验证 `kaipaile-server` 可在该基线下通过 `mvn -q -DskipTests compile`
- [x] T28 已为 `backend-only` 建立远端 helper、sudoers 引导安装与标准发布脚本 `run-backend-only-release.py`
- [x] T29 已使用 `backend-only` 标准发布脚本完成一次真实发布，并生成发布记录 `20260403-013415-backend-only-auth-runtime-check-final.md`
- [x] T30 已补充后端发布后异常排查的标准只读诊断入口 `read-backend-runtime-logs.py`，并要求真实环境 `400/500` 先走 runbook 诊断再继续修复
