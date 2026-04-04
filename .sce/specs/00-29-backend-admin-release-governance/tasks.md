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
- [x] T31 已把后端标准只读诊断入口扩展为同时回读 compose 原始后端服务来源摘录与 `docker compose config` 渲染结果，避免环境变量来源继续靠人工猜测
- [x] T32 已为后端 compose / env source 建立标准同步脚本 `run-backend-compose-env-sync.py`，并要求运行时变量变更先留档、后重建
- [x] T33 已为 `dev + Nacos` 运行时建立标准只读配置源回读脚本 `read-backend-nacos-config.py`，避免继续只查 compose 而漏掉 Nacos 覆盖层
- [x] T34 已为后端 Nacos dataId 建立标准同步脚本 `run-backend-nacos-config-sync.py`，并要求配置写入先留档、后重建
- [x] T35 已为后端 DB 结构变更建立标准 schema 发布脚本 `run-backend-schema-migration.py`，避免再次出现“jar 已发、schema 未发”
- [x] T36 已为 `backend-only` 增加 schema 门禁，目标库未建立 `schema_release_history` 或存在未执行 migration 时，标准发布必须直接中止
- [x] T37 已为微信配置补齐前置输入建立本地只读检查入口 `read-local-wechat-config-inputs.py`，避免继续停留在“远端缺值，但本地是否真的有合法输入无人能证明”的口头阶段
- [x] T38 已为微信配置来源补齐建立总控脚本 `run-backend-wechat-config-sync-pipeline.py`，固定 `local-input -> remote-gate -> compose sync -> nacos sync` 顺序并在前置失败时中止
- [x] T39 已以真实当前环境执行 `run-backend-wechat-config-sync-pipeline.py --dry-run`，并生成阻塞记录 `20260403-063339-backend-wechat-config-pipeline-invite-login-wechat-sync.md`，确认总控会在本地缺 secret 时第 1 步标准中止
- [x] T40 已为微信配置补齐建立本地 secret 文件模板与忽略规则，并让 `read-local-wechat-config-inputs.py` / `run-backend-wechat-config-sync-pipeline.py` 默认支持 `.sce/config/local-secrets/wechat-miniapp.env`
- [x] T41 已按默认 secret 文件路径执行 `read-local-wechat-config-inputs.py` 与 `run-backend-wechat-config-sync-pipeline.py --dry-run`，并生成 `20260403-063829-secret-file-default-check`、`20260403-063830-backend-wechat-config-pipeline-secret-file-default-pipeline.md`，确认“默认路径缺文件”时也会标准中止
- [x] T42 已让 `run-backend-compose-env-sync.py` 与 `run-backend-nacos-config-sync.py` 也默认支持 `.sce/config/local-secrets/wechat-miniapp.env`，避免总控和原子脚本在本地输入来源上再次分叉
- [x] T43 已实际验证 `run-backend-compose-env-sync.py` 与 `run-backend-nacos-config-sync.py --dry-run` 在默认 secret 文件缺失时会返回统一报错，明确指出“本地 env 不存在，且已检查 `.sce/config/local-secrets/wechat-miniapp.env`”
- [x] T44 已通过临时 fake secret 文件完成 `run-backend-wechat-config-sync-pipeline.py --dry-run` 全链路验证，并生成 `20260403-064540-backend-wechat-config-pipeline-fake-secret-full-dryrun.md`、`20260403-064551-backend-env-fake-secret-full-dryrun.md`、`20260403-064601-backend-nacos-fake-secret-full-dryrun.md`，确认总控可完整穿过 `local-input -> remote-gate -> compose dry-run -> nacos dry-run`
- [x] T45 已新增 `init-local-wechat-secret-file.py` 作为标准本地输入位初始化入口，自动创建 gitignored 的 `.sce/config/local-secrets/wechat-miniapp.env` 并预填当前小程序 `appId`
- [x] T46 已把微信输入门禁升级为“合法输入门禁”：`read-local-wechat-config-inputs.py`、`run-backend-compose-env-sync.py`、`run-backend-nacos-config-sync.py` 与 `run-backend-wechat-config-sync-pipeline.py` 当前都会拒绝 placeholder / fake secret
- [x] T47 已新增单页 runbook `wechat-config-gate-runbook.md`，固定 `init local secret -> local-input -> total pipeline -> backend-only -> post-release precheck -> real sample` 顺序
- [x] T48 已按默认本地 secret 文件路径执行合法性门禁与总控，并生成 `20260403-083329-continue-wechat-local-gate-local-input`、`20260403-083329-backend-wechat-config-pipeline-continue-wechat-local-gate.md`，确认“文件已存在但 secret 仍是 placeholder”时总控会以 `local_input_not_ready` 标准中止
- [x] T49 已为 `backend-only` 补齐“脏工作树隔离”门禁：存在非 `target/` 脏改时，脚本默认拒绝直接从当前工作树构建；只有显式 `--overlay-path` 才允许切到 `HEAD` 干净快照 + overlay 构建模式
- [x] T50 已为 `run-backend-schema-migration.py` 补齐 `schema_release_history.release_id` 长度保护：当发布批次号超过库宽时，标准脚本会自动归一化并在记录中显式回写，避免 schema 发布脚本自身再因 `Data too long` 中断
- [x] T51 已修正 `backend-only` 的 overlay schema 门禁：当标准发布切到 `HEAD` 干净快照 + overlay 模式时，migration 检查改为基于实际构建源执行，不再被无关脏工作树 SQL 误阻断
- [x] T52 已修正 `run-backend-nacos-config-sync.py` 的 YAML dotted key 写入：标准 Nacos 同步入口现在可精确写入任意 dotted key path，不再把非微信配置误写到固定业务块下
- [x] T53 已为 AI 治理真实通知配置补齐本地 secret 输入位、只读输入检查与总控脚本：`init-local-ai-notification-secret-file.py`、`read-local-ai-notification-config-inputs.py`、`run-backend-ai-notification-config-sync-pipeline.py`
- [x] T54 已将 AI 通知配置来源补齐流程并入 `00-29` runbook，固定为 `local-input -> remote nacos precheck -> nacos sync -> backend-only -> 00-60 validation`
- [x] T54-A 已按标准入口执行 `init-local-ai-notification-secret-file.py`、`read-local-ai-notification-config-inputs.py` 与 `run-backend-ai-notification-config-sync-pipeline.py --dry-run`，并生成 `20260404-060356-backend-ai-notification-config-pipeline-continue-ai-notification-local-gate.md`，确认 placeholder callback token 会把总控标准阻断
- [x] T54-B 已新增单页 runbook `ai-notification-config-gate-runbook.md`，固定 `init local secret -> local-input -> total pipeline -> backend-only -> 00-60 validation` 顺序，并把 blocked 记录中的本地校验问题显式化
- [x] T55 已在真实环境拿到合法 callback token 后，按标准总控完成 AI 通知配置同步、schema 发布、`backend-only` 重建与 `run-ai-resume-notification-foundation-validation.py` 验证；首轮样本 `20260404-073450-continue-ai-notification-random-token` 暴露 `adminUserId=2` 联系方式缺失，修正后 `20260404-073638-continue-ai-notification-random-token-after-admin-contact` 全量通过，并已回写 `20260404-072827-backend-ai-notification-config-pipeline-continue-ai-notification-random-token.md`、`20260404-073019-backend-schema-continue-ai-notification-random-token.md`、`20260404-073310-backend-only-continue-ai-notification-random-token.md`
