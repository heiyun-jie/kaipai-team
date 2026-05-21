# 00-157 执行记录

## 2026-04-27 任务建立

触发原因：

- 用户在 `pkg-card/actor-card/index` 海报预览中发现 `海报机构名称缺失`。
- 用户要求全面审查，禁止当前框架之外的遗留内容存在，覆盖后端/后台/小程序/数据库。

当前状态：已通过内部审查，等待人工 5 分验收。

## 2026-04-27 修复范围

缺陷原因：

- `pkg-card/actor-card/index` 海报绘制仍依赖旧 `company/studio` 数据，导致点击海报时出现 `海报机构名称缺失`。
- 上轮审查没有把构建产物、后台路径名和数据库迁移脚本纳入同一套零残留口径。

已处理内容：

- 小程序海报逻辑删除 `getCompanyInfo` 依赖，海报品牌固定为当前产品名，不再读取机构/公司资料。
- 小程序移除可见 `STUDIO` 眉标，并将历史列表类名 `history-page__studio` 改为 `history-page__intro`。
- 后端包、类、API、DTO、字段从 `company` 物理迁移到 `crew`，接口路由从 `/company` 改为 `/crew`。
- 后台招募字段改为 `crewName/crewProfileId/crewId/crewUserId`，后台用户页文案删除组织域残留。
- 后台模板编辑组件从 `TemplateEditorStudio` 改为 `TemplateEditorPanel`，样式类改为 `template-editor-*`，surface 枚举从 `studio` 改为 `softlight`。
- 删除空旧目录 `kaipai-admin/src/views/membership`。
- 数据库基线迁移改为当前 `capability_*` 表和字段，不再从旧会员表名开始建表。
- 数据库旧会员域、旧权限、旧模板 surface、旧评分表、旧报告域均采用备份后物理清理脚本，不保留兼容字段或旧别名。
- 新增 `V20260427_026__template_surface_key_physical_cleanup.sql`，备份并物理更新历史模板 JSON 中的旧 surface key。

## 2026-04-27 验证记录

构建验证：

- `kaipaile-server`: `mvn -q clean package` 通过。仅有 commons-logging/JVM/test warning，无编译失败。
- `kaipai-admin`: `npm run type-check` 通过；`npm run build` 通过；`scripts/sanitize-dist.ps1` 通过。仅有 Sass legacy API 和 Vite chunk warning。
- `kaipai-frontend`: `npm run type-check` 通过；`npm run build:mp-weixin` 通过；`npm run audit:mp-package` 通过。
- 小程序包体审查：总包 `627.45 KB`，主包 `501.25 KB`，`pkg-card 97.99 KB`，`pkg-tools 28.21 KB`，全部低于 `2 MB`。

最终零命中复审：

- 小程序范围：`kaipai-frontend/src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin`。
- 后台范围：`kaipai-admin/src`、`kaipai-admin/dist`。
- 后端范围：`kaipaile-server/src/main/java`、`src/main/resources/db/migration`、`target/classes`。
- 路径范围：三端源码、构建产物、迁移脚本路径名。
- 审查词：`海报机构|机构名称|机构|组织|企业|公司|company|Company|organization|Organization|studio|Studio|STUDIO|credit|Credit|信用|积分|fortune|Fortune|命理|会员|membership|Membership|member|Member|vip|VIP|Vip|ORG USERS|剧组/剧组|剧组 / 剧组`。
- 结果：源码、构建产物、target/classes、迁移脚本、路径名全部零命中。

## 2026-04-27 审查评分

内部审查评分：`95/95`。

扣分项：无阻断项。保留风险只剩 Sass legacy API、Vite chunk size、commons-logging/JVM warning，均不是本规格旧域残留问题。

结论：本规格允许进入人工 `5/100` 验收，不再在未完成状态下收尾。
## 2026-04-27 线上发布推进记录

当前结论：线上发布未完成，审查不得标记通过。

已完成的本地门禁：

- `kaipaile-server`: `mvn -q clean package` 通过。
- `kaipai-admin`: `npm run build` 通过，已改为跨平台 `node scripts/sanitize-dist.mjs`，发布快照脚本已包含 `scripts/` 目录。
- `kaipai-frontend`: `npm run build:mp-weixin` 通过；`npm run audit:mp-package` 通过。
- 三端源码、构建产物、后端 `target/classes`、迁移脚本旧域关键词复查零命中。

线上阻断证据：

- 本机 `hosts` 当前存在 `127.0.0.1 kplyyk.com # kplyyk-local-https-proxy`，环境不允许提权清理，不能把本机 `https://kplyyk.com` 结果作为线上证据。
- 本机 DNS/外部解析 `kplyyk.com`、`api.kplyyk.com` 返回 `198.18.0.x`，属于代理/保留网段，不能作为公网发布审查依据。
- `curl --resolve kplyyk.com:80:101.43.57.62 http://kplyyk.com/api/v3/api-docs` 返回 `302` 到 `https://dnspod.qcloud.com/static/webblock.html?d=kplyyk.com`。
- `curl --resolve api.kplyyk.com:80:101.43.57.62 http://api.kplyyk.com/v3/api-docs` 返回 `302` 到 `https://dnspod.qcloud.com/static/webblock.html?d=api.kplyyk.com`。
- `curl --resolve kplyyk.com:443:101.43.57.62 https://kplyyk.com/` TLS 握手失败。
- `http://101.43.57.62:8080/*` 对公网返回 `Empty reply from server`，不能作为业务域名健康通过证据。

已新增发布流程防线：

- `run-backend-only-release.py`、`run-admin-only-release.py` 新增 `require_public_smoke_dns`，当公网审查域名解析到 `127.0.0.1` 或 `198.18.0.0/15` 等本地/代理地址时直接阻断，禁止本地代理结果冒充线上审查通过。
- `run-admin-only-release.py` 新增 `--allow-domain-blocked-deploy`，用于远端静态替换成功但公网域名审查阻断时写入阻断记录并返回非 0。

## 2026-04-27 后台静态发布与根域名路由修正

已完成：

- 远端 admin helper 完成后台静态构建与替换，静态目录 `/opt/kaipai/nginx/html` 更新时间为 `2026-04-27 14:52 +0800`。
- 补写发布记录：`.sce/runbooks/backend-admin-release/records/20260427-143015-admin-only-organization-company-residue-runtime-cleanup.md`。
- 同步新版 backend helper，并执行 `run-domain-api-proxy-sync.py --label kplyyk-root-static-api-split --operator codex`。
- 根域名 Nginx 内网路由已修正：`Host: kplyyk.com /` 返回后台静态首页 `200 OK`；`Host: kplyyk.com /api/v3/api-docs` 返回后端 OpenAPI `200`。
- 远端后台静态目录、内网首页回包、内网 OpenAPI 回包按旧域关键词复查，结果零命中。

阻断记录：

- `.sce/runbooks/backend-admin-release/records/20260427-145609-domain-api-proxy-kplyyk-root-static-api-split.md`。
- `kplyyk.com` 未在远端 DNS 解析到 `101.43.57.62`。
- 根域名证书缺失：`/etc/letsencrypt/live/kplyyk.com/fullchain.pem`。
- 真实公网 `http://kplyyk.com` 经 `--resolve kplyyk.com:80:101.43.57.62` 仍返回 DNSPod webblock `302`。
- 真实公网 `https://kplyyk.com` 经 `--resolve kplyyk.com:443:101.43.57.62` 仍 TLS handshake failed。

当前评分：

- 本地源码/构建/数据库迁移/远端内网运行态：`95/95`。
- 线上公网发布审查：`0/95`，原因是业务域名 DNS/证书/公网入口未通过。
- 项目主线状态：`未完成`，禁止收尾为完成。

补充内网 API smoke：

- `Host: kplyyk.com POST http://127.0.0.1/api/auth/sendCode` 返回 HTTP `200`，业务 `code=200`，`data` 返回验证码。
- `Host: kplyyk.com POST http://127.0.0.1/api/admin/auth/login` 返回 HTTP `200`，业务 `code=200`，后台登录成功。
- `https://kplyyk.com/api/auth/sendCode` 经 `--resolve kplyyk.com:443:101.43.57.62` 仍 TLS handshake failed。
- 结论：后端和后台在远端内网 Host 路由下已可用；未通过点仍是公网 HTTPS 域名入口，不是 API 业务 500。

## 2026-04-27 发布后流程 / 操作 / 数据审查

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260427-172000-post-release-flow-operation-data-review.md`

本轮继续修复并发布：

- `V20260427_027__runtime_schema_residue_physical_cleanup.sql`
  - 记录：`.sce/runbooks/backend-admin-release/records/20260427-165334-backend-schema-runtime-schema-residue-physical-cleanup.md`
  - 结果：运行库 `zz_bak/zz_backup` 清理影子表已导出到 MySQL secure-file 存储，并从当前业务 schema 物理删除；当前业务字段旧注释已修正。
- `V20260427_028__operation_log_payload_archive_cleanup.sql`
  - 记录：`.sce/runbooks/backend-admin-release/records/20260427-170716-backend-schema-operation-log-payload-archive-cleanup.md`
  - 结果：历史操作日志 payload 已导出到 MySQL secure-file 存储；运行表 `before_snapshot_json`、`after_snapshot_json`、`extra_context_json` 已清空。
- `V20260427_029__runtime_data_residue_value_cleanup.sql`
  - 记录：`.sce/runbooks/backend-admin-release/records/20260427-171248-backend-schema-runtime-data-residue-value-cleanup.md`
  - 结果：历史 UA、能力日志 remark、`crew_profile.extended_field` 的旧值 token 已清理。
- `V20260427_030__runtime_text_value_residue_cleanup.sql`
  - 记录：`.sce/runbooks/backend-admin-release/records/20260427-171519-backend-schema-runtime-text-value-residue-cleanup.md`
  - 结果：业务文本剩余旧值 token 已清理。

数据审查结果：

- `BACKUP_TABLE_COUNT = 0`。
- 旧表名 / 旧表注释：无返回。
- 旧字段名 / 旧字段注释：无返回。
- 关键迁移记录计数：`REQUIRED_MIGRATION_COUNT = 9`。
- `admin_operation_log` payload 运行字段：`before_non_null = 0`、`after_non_null = 0`、`extra_non_null = 0`。
- 全量文本 / JSON 数据残留扫描：无返回。
- 结论：数据审查通过。

内网运行态审查结果：

- `Host: kplyyk.com GET http://127.0.0.1/` 返回 HTTP `200 OK`，后台静态首页可用。
- `Host: kplyyk.com GET http://127.0.0.1/api/v3/api-docs` 返回 HTTP `200`，当前 OpenAPI 旧域关键词扫描无返回。
- `Host: kplyyk.com POST http://127.0.0.1/api/auth/sendCode` 返回 HTTP `200`，业务 `code=200`，`data` 返回验证码。
- `Host: kplyyk.com POST http://127.0.0.1/api/admin/auth/login` 返回 HTTP `200`，业务 `code=200`。
- `Host: kplyyk.com OPTIONS http://127.0.0.1/api/admin/auth/login` 返回 HTTP `200`，CORS 预检包含 `Access-Control-Allow-Origin: http://127.0.0.1:5100`。
- 结论：内网运行态 API / 后台 / CORS 审查通过。

公网阻断复审：

- 本机 hosts 仍存在 `127.0.0.1 kplyyk.com # kplyyk-local-https-proxy`。
- 外部 DNS `kplyyk.com` 仍解析到 `198.18.0.31`。
- `/etc/letsencrypt/live/kplyyk.com/fullchain.pem` 缺失。
- `/etc/letsencrypt/live/api.kplyyk.com/fullchain.pem` 缺失。
- 服务器本机 HTTPS SNI `https://kplyyk.com/` 返回 HTTP `404`，未进入当前根域名静态+API server block。
- 公网强制解析 `https://kplyyk.com/` 和 `https://kplyyk.com/api/v3/api-docs` 仍 TLS handshake failed。
- 公网强制解析 `http://kplyyk.com/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`；但 `http://kplyyk.com/api/v3/api-docs` 仍 `302` 到 DNSPod webblock。

当前评分：

- 数据审查：`95/95`。
- 内网 API / 后台静态 / CORS 审查：`95/95`。
- 公网 HTTPS 流程审查：`0/95`。
- 总结论：`未完成`，不能标记审查通过，不能进入收尾完成响应。

## 2026-04-28 公网 HTTPS 域名阻断复审

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260428-141525-domain-api-proxy-kplyyk-https-recheck-20260428.md`
- `.sce/runbooks/backend-admin-release/records/20260428-142000-public-https-domain-block-review.md`

实时结论：

- `run-domain-api-proxy-sync.py --label kplyyk-https-recheck-20260428 --operator codex` 返回 `blocked`，不是 `passed`。
- helper 阻断原因：`kplyyk.com does not resolve to 101.43.57.62 on remote DNS`，且 `TLS certificate for kplyyk.com is missing`。
- 远端 helper 认为 `api.kplyyk.com` 证书存在；根域名 `kplyyk.com` 证书缺失。

DNS 证据：

- 本机 `nslookup kplyyk.com 119.29.29.29` 与 `223.5.5.5` 返回 `198.18.0.144`。
- 本机 `nslookup api.kplyyk.com 119.29.29.29` 与 `223.5.5.5` 返回 `198.18.0.145`。
- DoH 查询 `kplyyk.com A` 无 Answer，仅返回 SOA；`api.kplyyk.com A` 返回 `101.43.57.62`。
- 服务器直连权威 NS：`dig @dns23.hichina.com +short A kplyyk.com` 与 `dns24` 均为空。
- 服务器直连权威 NS：`dig @dns23.hichina.com +short A api.kplyyk.com` 与 `dns24` 均返回 `101.43.57.62`。

Nginx / 证书证据：

- 服务器内网 `Host: kplyyk.com GET http://127.0.0.1/` 返回 HTTP `200`。
- 服务器内网 `Host: kplyyk.com GET http://127.0.0.1/api/v3/api-docs` 返回 HTTP `200`。
- 本机公网强制解析 `http://kplyyk.com/api/v3/api-docs` 到 `101.43.57.62` 返回 `302` 到 DNSPod webblock。
- 本机公网强制解析 `https://kplyyk.com/api/v3/api-docs` 到 `101.43.57.62` 仍 TLS handshake failed。
- 当前 443 证书 SAN 只有 `DNS:api.kplyyk.com`，不覆盖根域名 `kplyyk.com`。

继续推进前置条件：

- 在权威 DNS 管理侧为 `kplyyk.com` 新增根记录：主机记录 `@`，类型 `A`，值 `101.43.57.62`，TTL 建议 `600`。
- 清除 DNSPod/webblock 或运营商侧拦截，确保公网不再跳转 `https://dnspod.qcloud.com/static/webblock.html?d=kplyyk.com`。
- 根域名解析生效后签发真实 `kplyyk.com` 证书；不得使用自签证书，不得使用 `api.kplyyk.com` 证书冒充通过。
- 证书存在后重新执行 `run-domain-api-proxy-sync.py` 生成根域名 443 server block，并再跑真实 `https://kplyyk.com` 公网全流程审查。

当前评分：

- 内网 Nginx / API / 后台路由：`95/95`。
- 公网 HTTPS 域名流程：`0/95`。
- 项目主线状态：`未完成`，禁止切到完成收尾。

## 2026-04-28 API 域名更正为 api.kplyyk.com

用户更正：

- API 主链路目标不是根域名 `kplyyk.com`，而是 `api.kplyyk.com`。

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260428-144500-api-domain-switch-review.md`

已完成本地修改：

- 小程序 `VITE_API_BASE_URL` 改为 `https://api.kplyyk.com`。
- 后台生产 `VITE_API_BASE_URL` 改为 `https://api.kplyyk.com/api`。
- 小程序包审查脚本允许 `api.kplyyk.com`。
- 后台 dist sanitizer 允许 `api.kplyyk.com`。
- API runtime 审查脚本默认目标 host 改为 `api.kplyyk.com`，并修复单 A 记录被拆成字符的脚本缺陷。
- 后端 CORS 配置补充 `https://api.kplyyk.com`。
- 后端发布 runbook / backend-only 脚本的 API smoke 默认目标改为 `https://api.kplyyk.com`。

验证结果：

- `kaipai-frontend npm run type-check`：通过。
- `kaipai-frontend npm run build:mp-weixin`：通过。
- `kaipai-frontend npm run audit:mp-package`：通过。
- `kaipai-admin npm run build`：通过。
- `kaipaile-server mvn -q -DskipTests package`：通过。
- 构建产物中，小程序请求 base 为 `https://api.kplyyk.com`。
- 构建产物中，后台 axios base 为 `https://api.kplyyk.com/api`。

API 域名事实：

- DoH 查询 `api.kplyyk.com A` 返回 `101.43.57.62`。
- 远端真实域名 `GET https://api.kplyyk.com/api/v3/api-docs` 返回 HTTP `200`。
- 远端真实域名 `POST https://api.kplyyk.com/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`，并返回验证码 `data`。
- 远端真实域名后台 CORS 预检返回 HTTP `200`，包含 `Access-Control-Allow-Origin: http://127.0.0.1:5100`。

当前阻断：

- 本机仍通过 `Meta Tunnel` 访问，`api.kplyyk.com` 系统解析到 `198.18.0.145`，`SourceAddress=198.18.0.1`。
- 本机 `npm run audit:api-runtime` 仍失败：`curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed`。
- 本机强制 HTTP 到 `101.43.57.62` 仍返回 DNSPod webblock：`https://dnspod.qcloud.com/static/webblock.html?d=api.kplyyk.com`。
- 尝试执行 `admin-only api-domain-switch` 发布时，本地命令 304 秒超时；已停止本地残留发布进程，但远端发布状态因 SSH banner exchange 超时暂无法确认。

当前结论：

- `api.kplyyk.com` 作为 API 域名的代码配置和构建审查已通过。
- `api.kplyyk.com` 远端真实域名 API 样本已通过。
- 后台静态发布状态未确认，不能标记发布完成。
- 本机公网 runtime 审查受 `Meta Tunnel / 198.18.0.x` 污染阻断，不能标记 95 分通过。

## 2026-04-29 API 子域名服务器配置与公网路径复审

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260429-154915-domain-api-proxy-api-only-nginx-sync.md`
- `.sce/runbooks/backend-admin-release/records/20260429-161215-api-domain-online-simulation-review.md`

本轮方向修正：

- 主线目标锁定为 `api.kplyyk.com`，不再以根域名 `kplyyk.com` 作为 API 子域名通过条件。
- 本机 Clash/Mihomo/TUN 只作为客户端路径污染证据，不作为服务器配置修复主线。
- 使用账号密码补足 sudo 后，直接审查服务器 Nginx、证书、监听、API 反代和线上 API 模拟。

服务器配置结果：

- `sudo` 密码验证通过。
- `nginx -t` 通过。
- `/etc/letsencrypt/live/api.kplyyk.com/fullchain.pem` 为 Let's Encrypt 证书，SAN 只包含 `DNS:api.kplyyk.com`，符合当前 API 子域名目标。
- 生效 Nginx 配置包含：
  - `server_name api.kplyyk.com` 的 80 server block，统一 `301` 到 HTTPS。
  - `server_name api.kplyyk.com` 的 443 ssl server block。
  - `location /` 反代到 `http://127.0.0.1:8080`。
- `ufw` 为 inactive。
- 监听端口包含 `0.0.0.0:80`、`0.0.0.0:443`、`0.0.0.0:8080`。

服务器侧线上 API 模拟结果：

- `GET https://api.kplyyk.com/api/v3/api-docs` 返回 HTTP `200`。
- `POST https://api.kplyyk.com/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`message=验证码发送成功`、`data` 返回验证码。
- `POST https://api.kplyyk.com/api/auth/login` 返回 HTTP `200`、业务 `code=200`、token 有返回。
- `OPTIONS https://api.kplyyk.com/api/admin/auth/login` 返回 HTTP `200`，包含 `Access-Control-Allow-Origin: http://127.0.0.1:5100`、`Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS`、`Access-Control-Allow-Headers: content-type, authorization`。
- `POST https://api.kplyyk.com/api/admin/auth/login` 返回 HTTP `200`、业务 `code=200`、后台 token 有返回。

本机客户端公网复审结果：

- 停止 Clash 后，`Resolve-DnsName api.kplyyk.com` 返回 `101.43.57.62`。
- 停止 Clash 后，`Test-NetConnection 101.43.57.62 -Port 443` 返回 `TcpTestSucceeded=True`，出网接口为物理网卡 `192.168.1.59 / 以太网 2`。
- `npm run audit:api-runtime` 仍失败：`curl: (35) Recv failure: Connection was reset`。
- `curl -vk https://api.kplyyk.com/api/v3/api-docs` 仍在 TLS 握手阶段 reset。
- `curl -v http://api.kplyyk.com/api/v3/api-docs` 客户端收到 `HTTP/1.1 302 OK`，`Location: https://dnspod.qcloud.com/static/webblock.html?d=api.kplyyk.com`。
- 同时服务器 Nginx access log 记录该客户端 HTTP 请求为 `301`，不是 `302`：`223.166.32.218 - - [29/Apr/2026:16:12:59 +0800] "GET /api/v3/api-docs HTTP/1.1" 301 178 "-" "curl/8.18.0"`。

当前判定：

- 服务器 Nginx / 证书 / 后端反代 / API / 后台 CORS 已通过服务器侧审查。
- 客户端公网路径仍被 DNSPod/WebBlock 或腾讯云域名安全/备案策略拦截改写；HTTP 响应从服务器 `301` 被客户端路径改写成 DNSPod `302`，HTTPS 在握手前 reset。
- 该阻断不能通过继续修改 Spring API、后台前端或 Nginx `proxy_pass` 解决；需要 DNSPod/Tencent Cloud 控制台侧解除 WebBlock、核查 ICP/备案、域名安全策略、WAF/CDN/安全组或更换可用已备案域名/非大陆入口。

当前评分：

- 服务器配置审查：`95/95`。
- 服务器侧线上 API 模拟：`95/95`。
- 客户端公网 HTTPS 全流程：`0/95`。
- 项目主线状态：`未完成`，禁止标记整体审查通过，禁止切到完成收尾。

后续阻断项：

- 当前仓库与环境未发现可直接用于 DNSPod/Tencent Cloud 控制台操作的自动化凭据或脚本。
- 需要在 DNSPod/Tencent Cloud 控制台核查并解除 `api.kplyyk.com` 的 WebBlock/域名安全策略拦截。
- 需要核查 `kplyyk.com` / `api.kplyyk.com` ICP/备案是否满足大陆服务器公网 80/443 访问要求。
- 需要核查 CDN/WAF/安全防护产品是否对 `api.kplyyk.com` 做了拦截或回源阻断。
- 控制台侧解除后必须重新执行 `npm run audit:api-runtime`，只有该公网 HTTPS 审查通过后才能把整体状态改为完成。

## 2026-04-30 小程序 sendCode ERR_CONNECTION_CLOSED 复审

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260430-174301-miniapp-sendcode-err-connection-closed-sni-review.md`

用户现场报错：

- 页面：`pages/login/index`
- 请求：`POST https://api.kplyyk.com/api/auth/sendCode`
- 微信开发者工具错误：`net::ERR_CONNECTION_CLOSED`

复审结果：

- 本机 DNS 正确：`api.kplyyk.com -> 101.43.57.62`。
- 本机 TCP 443 可连：`TcpTestSucceeded=True`，出网接口为 `192.168.1.59 / 以太网 2`。
- `curl -vk https://api.kplyyk.com/api/auth/sendCode` 在 TLS 握手阶段 reset。
- `curl -vk --tlsv1.2 https://api.kplyyk.com/api/v3/api-docs` reset。
- `curl -vk --tlsv1.3 https://api.kplyyk.com/api/v3/api-docs` reset。
- `curl -vk https://101.43.57.62/` 可以建立 TLS 并返回 Nginx/Tomcat `404`。
- `curl -vk -H "Host: api.kplyyk.com" https://101.43.57.62/api/v3/api-docs` 可以建立 TLS 并返回 HTTP `200`。

判定：

- 服务器 443、Nginx、证书落点、后端反代均可用。
- 直接域名访问失败，按 IP 访问并只使用 HTTP Host 头成功，唯一关键差异是 TLS SNI。
- 微信开发者工具访问 `https://api.kplyyk.com` 必然携带 SNI：`api.kplyyk.com`，因此在当前公网链路被 reset，表现为 `ERR_CONNECTION_CLOSED`。
- 该错误不是前端路径错误、不是 CORS、不是验证码接口业务 400/500；请求未进入后端业务层。

当前评分：

- 小程序请求代码路径：`95/95`，URL 生成正确。
- 服务器 API 业务链路：`95/95`，绕过 SNI 后可达。
- `api.kplyyk.com` 真实域名 HTTPS/SNI 公网链路：`0/95`。
- 项目主线状态：`未完成`，禁止标记整体审查通过。

## 2026-04-30 API 子域名根路径 404 修复

问题：

- 用户访问 `https://api.kplyyk.com/` 时看到 `HTTP Status 404 - Not Found`。
- 原因是 API 子域名 443 server block 的 `location /` 直接反代到后端，根路径 `/` 落到后端 Tomcat，后端没有根路由，因此返回 Tomcat 404。

修改：

- 修改 `.sce/runbooks/backend-admin-release/scripts/kaipai-backend-release-helper.sh` 的 API-only Nginx 生成模板。
- 在 `server_name api.kplyyk.com` 的 443 server block 中新增精确匹配：
  - `location = /` 返回 `application/json`。
  - 响应体为 `{"code":200,"message":"api service ok","data":{"service":"kaipai-api","docs":"/api/v3/api-docs"}}`。
- 保留原 `location /` 反代到 `http://127.0.0.1:8080`，不改变 `/api/**` 业务接口行为。
- 同步 helper 到服务器并执行：
  - `python .sce/runbooks/backend-admin-release/scripts/run-domain-api-proxy-sync.py --label api-root-health --operator codex --host 101.43.57.62 --api-only --api-domain api.kplyyk.com --domain kplyyk.com`

发布记录：

- `.sce/runbooks/backend-admin-release/records/20260430-174917-domain-api-proxy-api-root-health.md`

审查结果：

- `nginx -t`：通过。
- 服务器生效配置已包含 `location = /`。
- 服务器内网 SNI：`https://api.kplyyk.com/` 返回 HTTP `200` 与健康 JSON。
- 本机绕过 SNI：`curl -k -H "Host: api.kplyyk.com" https://101.43.57.62/` 返回 HTTP `200` 与健康 JSON。
- 服务器内网 `GET /api/v3/api-docs` 返回 HTTP `200`。
- 服务器内网 `POST /api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。
- 本机绕过 SNI `POST https://101.43.57.62/api/auth/sendCode` 且 `Host: api.kplyyk.com` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。

剩余阻断：

- 本机真实域名 `https://api.kplyyk.com/` 仍在 TLS/SNI 阶段 reset。
- PowerShell `Invoke-WebRequest https://api.kplyyk.com/` 返回 `基础连接已经关闭: 发送时发生错误。`
- 因此根路径 404 已在服务器侧修复，但真实域名公网 HTTPS/SNI 阻断仍未解除。

当前评分：

- API 子域名根路径 404 修复：`95/95`。
- `/api/**` 业务接口回归：`95/95`。
- `api.kplyyk.com` 真实域名 HTTPS/SNI 公网链路：`0/95`。
- 项目主线状态：`未完成`，禁止标记整体公网审查通过。

## 2026-04-30 真实域名公网阻断抓包复核

补充记录：

- `.sce/runbooks/backend-admin-release/records/20260430-174301-miniapp-sendcode-err-connection-closed-sni-review.md`

抓包结论：

- 本机访问 `https://api.kplyyk.com/` 时，服务器能收到 TCP 三次握手和 TLS ClientHello。
- 服务器只 ACK 了 ClientHello，还未回 TLS 证书，随后收到客户端方向的 RST。
- 本机访问 `https://101.43.57.62/` 并设置 `Host: api.kplyyk.com` 时，同一服务器、同一 443 端口可以完成 TLS 与 HTTP 响应。
- 因此阻断条件不是服务器 IP、443 端口、Nginx 监听、证书文件或后端反代，而是 `api.kplyyk.com` 真实域名/SNI。

HTTP 复核：

- `curl http://api.kplyyk.com/` 返回 `HTTP/1.1 302 OK`，`Location: https://dnspod.qcloud.com/static/webblock.html?d=api.kplyyk.com`。
- `curl http://api.kplyyk.com/api/v3/api-docs` 返回同样 DNSPod WebBlock。

当前可修改项状态：

- 服务器 Nginx 已修复 `https://api.kplyyk.com/` 根路径 404，服务器侧和绕过 SNI 验证均返回健康 JSON。
- `/api/**` 业务接口服务器侧回归通过。
- 剩余失败为 DNSPod/Tencent Cloud/备案/域名安全策略级公网阻断，当前仓库和 SSH 服务器侧无法直接解除。

继续推进要求：

- 必须进入 DNSPod/Tencent Cloud 控制台解除 `api.kplyyk.com` WebBlock/域名安全阻断，或完成 ICP/备案/域名接入要求。
- 解除后重新跑 `npm run audit:api-runtime` 和微信开发者工具 `sendCode`。
- 在真实 `https://api.kplyyk.com/api/auth/sendCode` 通过前，整体公网 API 审查仍是 `0/95`。

## 2026-04-30 小程序本机 API 代理联调

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260430-181253-miniapp-local-api-proxy-review.md`

目的：

- 在真实 `api.kplyyk.com` 公网 HTTPS/SNI 被阻断期间，先恢复本机微信开发者工具页面流程验证能力。
- 该链路只用于本机联调，不计入公网 API 通过。

工具修改：

- `.sce/tools/start-kplyyk-local-https-proxy.ps1`
  - 支持按域名生成独立本地证书。
  - 新增 `-SkipHosts`，允许高端口模式不写 hosts、不需要管理员权限。
- `.sce/tools/kplyyk-local-https-proxy.js`
  - 代理 Host 不再硬编码 `kplyyk.com`。
  - `/` 与 `/__proxy_health` 返回本地代理健康 JSON。

本机启动链路：

- 本地 HTTPS 代理：`https://localhost:18443`。
- 本地 SSH 隧道：`127.0.0.1:18080 -> 服务器 127.0.0.1:8080`。
- 小程序本机覆盖配置：`kaipai-frontend/.env.local`，内容为 `VITE_API_BASE_URL=https://localhost:18443`。
- 小程序 dev watch 已重启，`dist/dev/mp-weixin` 产物中的 `request.js`、`runtime.js`、`upload.js` 均已使用 `https://localhost:18443`。

审查结果：

- `curl -k https://localhost:18443/` 返回 HTTP `200` 与本地代理健康 JSON。
- `curl -k https://localhost:18443/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。
- 该链路可用于微信开发者工具继续验收登录页获取验证码流程。

限制：

- 该链路不代表生产配置变更。
- 生产 `.env` 仍为 `VITE_API_BASE_URL=https://api.kplyyk.com`。
- 如果微信开发者工具未启用“不校验合法域名、TLS 版本以及 HTTPS 证书”，本机自签 `localhost` 证书可能被拒绝。
- 真实公网通过仍必须以 `https://api.kplyyk.com/api/auth/sendCode` 直接通过为准。

当前评分：

- 本机小程序联调链路：`95/95`。
- 真实公网 `api.kplyyk.com` HTTPS/SNI 链路：`0/95`。
- 项目整体公网 API 状态：`未完成`，禁止标记公网审查通过。

## 2026-04-30 18:18 公网 API 与本机代理复核

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260430-181805-public-api-sni-and-local-proxy-followup.md`

复核结果：

- 本机 `.env.local` 仍指向 `VITE_API_BASE_URL=https://localhost:18443`。
- 小程序 `dist/dev/mp-weixin/utils/request.js` 已编译为 `https://localhost:18443`。
- 本机代理 `127.0.0.1:18443` 和 SSH 隧道 `127.0.0.1:18080` 均在监听。
- 本机代理 `GET https://localhost:18443/` 返回 HTTP `200` 与代理健康 JSON。
- 本机代理 `POST https://localhost:18443/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。
- 公网 `GET https://api.kplyyk.com/` 仍在 TLS 握手阶段 `Recv failure: Connection was reset`。
- 公网 `POST https://api.kplyyk.com/api/auth/sendCode` 仍返回 `ECONNRESET`，请求未进入后端业务层。
- HTTP 明文 `http://api.kplyyk.com/api/auth/sendCode` 当前已到达服务器 Nginx，并返回 `301` 到 HTTPS；该点较前一轮 DNSPod WebBlock 状态已有变化。
- 绕过 SNI 直连 `https://101.43.57.62/api/auth/sendCode` 并设置 `Host: api.kplyyk.com` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。
- 服务器生效 Nginx 配置包含 `server_name api.kplyyk.com` 的 443 server block、`location = /` 健康 JSON 和 `/api/**` 后端反代。
- 服务器证书 CN/SAN 均为 `api.kplyyk.com`，有效期为 `2026-04-22` 至 `2026-07-21`。
- 项目内置生产审查 `npm run audit:api-runtime` 失败：`API 运行态请求失败：curl: (35) Recv failure: Connection was reset`。

判定：

- 本机联调通道可继续用于微信开发者工具验收页面流程，但不计入公网 API 通过。
- 服务器 Nginx、证书、443 监听、后端反代、验证码接口均已排除为当前失败原因。
- 当前真实阻断仍集中在 `api.kplyyk.com` 的公网 HTTPS/SNI 链路。
- 整体公网 API 审查仍为 `0/95`，禁止标记完成。

下一步：

- 需要在 DNSPod/Tencent Cloud/备案/WAF/CDN/域名安全侧解除 `api.kplyyk.com` HTTPS/SNI 阻断。
- 解除后必须重新跑真实公网 `GET https://api.kplyyk.com/` 与 `POST https://api.kplyyk.com/api/auth/sendCode`。
- 只有真实公网 HTTPS 直接返回 HTTP `200` 且业务 `code=200` 后，才能重新进入小程序和后台公网全流程审查。

## 2026-04-30 22:24 服务器是否启动专项定位

用户问题：

- “直接定位，服务器没有启动吗？”

定位结果：

- 服务器不是未启动。
- Nginx：`active (running)`，服务启动时间 `2026-04-22 17:19:30 CST`。
- 80/443：由 Nginx 监听。
- 后端 8080：由 Docker proxy 监听，映射到容器 `kaipai-backend`。
- Docker 容器：
  - `kaipai-backend`：`Up 3 days`，端口 `0.0.0.0:8080->8080/tcp`。
  - `nacos`：`Up 8 days`。
  - `kaipai-redis`：`Up 8 days`。
  - `kaipai-mysql`：`Up 2 days`。
- 后端进程：容器内 `java -jar app.jar`，PID `1354667`，启动时间 `2026-04-27 10:28:32 CST`，工作目录 `/app`。

接口探活：

- `http://127.0.0.1:8080/` 返回 Tomcat `404`，这是后端无根路由，不代表服务未启动。
- `http://127.0.0.1:8080/api/v3/api-docs` 返回 HTTP `200`。
- `http://127.0.0.1:8080/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。
- 服务器本机经 Nginx 443 + `api.kplyyk.com` SNI：
  - `https://api.kplyyk.com/` 返回 HTTP `200` 与健康 JSON。
  - `https://api.kplyyk.com/api/auth/sendCode` 返回 HTTP `200`、业务 `code=200`、`data` 返回验证码。

判定：

- 当前问题不是服务器未启动。
- 当前问题不是后端 8080 未监听。
- 当前问题不是 Nginx 未启动。
- 当前问题不是验证码接口业务不可用。
- 公网 `api.kplyyk.com` 的失败仍应按 HTTPS/SNI 公网链路 reset 继续处理，不能误归因为服务器未启动。

## 2026-04-30 22:37 ECONNRESET 根因专项定位

审查记录：

- `.sce/runbooks/backend-admin-release/records/20260430-223720-api-domain-econnreset-rst-injection-root-cause.md`

用户问题：

- 需要定位为什么会 `ECONNRESET / ERR_CONNECTION_CLOSED`。

定位结果：

- Docker 容器 `kaipai-backend`、`kaipai-mysql`、`kaipai-redis`、`nacos` 均在运行。
- MySQL 返回 `mysqld is alive`。
- 后端日志显示 `sendCode` 已正常执行并打印开发模式验证码。
- UFW 为 `inactive`。
- iptables/nft 未发现针对 `443` 的 `REJECT`、`DROP`、`RST` 规则。
- Nginx 生效配置中 `api.kplyyk.com` 的 443 server block 存在，`proxy_pass http://127.0.0.1:8080` 正确。
- Nginx 配置未发现 `ssl_reject_handshake`、`return 444`、`reset_timedout_connection`。

同一 IP 只改变 SNI 的测试：

- 目标 IP 固定：`101.43.57.62`。
- 目标端口固定：`443`。
- HTTP Host 固定：`api.kplyyk.com`。
- `servername=api.kplyyk.com`：返回 `ECONNRESET`。
- `servername=''`：返回 HTTP `200` 与 API 健康 JSON。

抓包关键证据：

- 带 `api.kplyyk.com` SNI 时，服务器收到客户端 ClientHello 后，立即收到声称来自客户端 IP 的 RST。
- 真实客户端正常包特征：`ttl 251`、`flags [DF]`、IP ID 连续递增。
- RST 包特征：`ttl 249`、`flags [none]`、IP ID 跳变为 `3405/3406`。
- RST 包与真实客户端同一 TCP 流的连续发包特征不一致，符合链路中设备伪造成客户端注入 RST 的特征。
- 不带 SNI 时，同一客户端、同一服务器、同一 443 端口可以完成 TLS 并返回 HTTP `200`。

判定：

- `ECONNRESET / ERR_CONNECTION_CLOSED` 的直接原因是公网 HTTPS 握手阶段出现基于 `api.kplyyk.com` SNI 的 RST 注入。
- 失败点在 Nginx 业务反代前，不是后端、数据库、Nginx 反代、CORS 或小程序请求代码。
- 不应把 `proxy_pass http://127.0.0.1:8080` 改成 `http://101.43.57.62:8080`；该修改不会解决 SNI reset，反而会引入公网回环和安全风险。

下一步：

- 进入 DNSPod/Tencent Cloud 检查 `api.kplyyk.com` 的 WebBlock、风险拦截、备案/接入/实名、WAF/CDN/高防/边缘安全策略。
- 若有 CDN/WAF，确认 `api.kplyyk.com` 的证书、源站 `101.43.57.62`、回源协议和回源 Host 均正确。
- 云侧解除后重新跑 `npm run audit:api-runtime`，并用微信开发者工具重新验证 `pages/login/index` 获取验证码。

当前评分：

- 服务器/后端/数据库运行态：`95/95`。
- Nginx 反代配置：`95/95`。
- 真实公网 `api.kplyyk.com` HTTPS/SNI 链路：`0/95`。
- 项目整体公网 API 审查：`未完成`。
