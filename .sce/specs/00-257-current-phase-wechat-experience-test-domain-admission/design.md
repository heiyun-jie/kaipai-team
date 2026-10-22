# 微信体验版测试域名准入修复 - 技术设计

_Requirements: 3.1-3.5, 4, 5_

## 1. 问题判定

手机体验版的 `request:fail url not in domain list` 由微信客户端在请求发出前拦截。`project.private.config.json` 的 `urlCheck=false` 只影响开发者工具，不能作为真机体验版修复。

## 2. 执行目标

```text
AppID: wx4dcc4e1066fd0fb9
Candidate: 20260902-145540-v3-draft
Target domain: https://test-api.kplyyk.com
Changed fields: requestdomain, uploaddomain, downloaddomain
Unchanged fields: wsrequestdomain and every other baseline domain field
```

## 3. 安全调用顺序

1. 从受控 secret file 在进程内解析凭据，校验 AppID；不打印凭据。
2. 获取短时 access token，只保存在进程内存。
3. 调用 `wxa/modify_domain` 的 `get` 动作，将域名响应规范化为排序 JSON。
4. 对每个目标列表计算缺失项；只有存在缺失时才调用 `add`，请求体只包含目标测试域名与对应字段。
5. 再次执行 `get`，逐字段断言目标存在、基线集合没有任何缺失、非目标字段未变化。
6. access token 和临时敏感变量随进程结束释放，不落盘。

## 4. 证据结构

证据目录：

```text
.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-257/
  ORIGINAL_FILE.json
  MODIFIED_FILE.json
  DIFF_FILE.patch
  VERIFICATION.txt
  ROLLBACK.sh
```

JSON 只包含微信 API 返回的服务器域名字段和非敏感状态。diff 使用结构化、排序后的 JSON 生成。`ROLLBACK.sh` 接受原始/修改后 JSON 路径并以本地副本恢复演练为默认行为；真实远端恢复需要显式环境开关，防止误触。

## 5. 保护断言

- `baseline[field] - modified[field]` 对所有数组字段均为空。
- `modified[requestdomain|uploaddomain|downloaddomain]` 均包含测试 API。
- `modified[wsrequestdomain] == baseline[wsrequestdomain]`。
- 生产数据库、容器、Nginx 和正式小程序均不在调用路径内。

## 6. Candidate 与验收状态

域名白名单是 AppID 外部网络配置，不改变 Candidate manifest，因此不重新构建或重冻 Candidate。修复完成前，`00-236` 状态为 `BLOCKED_BY_WECHAT_DOMAIN_ADMISSION`；远端读回通过后转为 `AWAITING_MOBILE_RETEST`，由用户在手机体验版重新加载完成最终真机验收。
