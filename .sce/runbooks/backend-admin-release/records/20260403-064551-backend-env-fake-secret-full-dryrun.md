# 后端运行时配置来源同步记录

## 1. 基本信息

- 配置批次号：`20260403-064551-backend-env-fake-secret-full-dryrun`
- 执行时间：`2026-04-03 06:46:01 +0800`
- 操作人：`codex`
- 范围：`backend-compose-env-sync`
- dry-run：`是`
- 关联 Spec：
  - `00-29 backend-admin-release-governance`
  - `00-28 invite wxacode execution card`

## 2. 目标

- 将后端 compose / env source 的运行时变量变更收口到标准脚本
- 本次仅同步 `docker-compose.yml` 的后端环境变量来源，不执行后端发版与容器重建

## 3. 变更项

- `WECHAT_MINIAPP_APP_ID`: `<missing>` -> `wxd38339082a9cfa4e`
- `WECHAT_MINIAPP_APP_SECRET`: `[REDACTED]` -> `[REDACTED]`

## 4. 目标值预览

- `WECHAT_MINIAPP_APP_ID` => `wxd38339082a9cfa4e`
- `WECHAT_MINIAPP_APP_SECRET` => `[REDACTED]`

## 5. 当前结论

- 当前容器运行时是否已生效：`否，当前仅做 dry-run 预览`
- 后续必须动作：
  - 通过标准 `backend-only` 脚本重建后端容器
  - 再通过标准诊断确认 compose 来源摘录与容器 env 都包含目标变量

## 6. 远端回读

- 本次为 dry-run，本地仅完成 compose 更新预演，未写入远端
