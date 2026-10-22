# 00-234 隔离测试环境基础设施 - 技术设计

_Requirements: 3.1-3.6, 4, 5_

## 1. 目标拓扑

| 层 | 测试目标 | 生产保护 |
|---|---|---|
| API | `test-api.kplyyk.com -> :18080` | `api.kplyyk.com -> :8080` 不变 |
| Admin | `test.kplyyk.com -> html-test` | `kplyyk.com -> html` 不变 |
| Nacos | `kaipai-backend-test.yml` | prod dataId 不改 |
| DB | `kaipai_test` | `kaipai_prod` 不写 |
| Redis | test DB index | prod DB index 不 flush |
| COS | test private bucket | prod bucket 不写/删 |

生产和测试复用宿主机基础服务，但不复用任何业务写入命名空间。

## 2. 分阶段启用

```text
CONFIGURED -> INFRA_READY -> DATA_READY -> TEST_READY
```

- `CONFIGURED`：文件和配置已准备，服务未开放。
- `INFRA_READY`：DNS/TLS/Nginx/容器连通，使用非生产测试数据。
- `DATA_READY`：`00-235` 完成生产副本迁移和断言。
- `TEST_READY`：测试后端稳定、自动 smoke 通过，可交给 `00-236`。

基础设施配置完成不代表数据兼容已完成。

## 3. Nacos 与启动前检查

测试 dataId 必须显式包含或解析为：

```text
spring profile = test
server port = 18080
database = kaipai_test
redis namespace/db = test-specific
private bucket = test-specific
external side effects = disabled/allowlisted
```

启动脚本先通过安全 helper 回读上述非敏感目标。任何字段缺失或与 prod 相同都拒绝启动。

## 4. Nginx 与 TLS

- 测试 API server block 只代理测试 upstream。
- 测试管理端使用独立 document root。
- 修改前备份配置，`nginx -t` 成功后 reload。
- DNS 公网解析、证书 SAN/有效期和外部 HTTPS 请求均通过后才标 `INFRA_READY`。
- 公网验证拒绝本地 hosts、127.0.0.1 和代理保留地址污染。

## 5. Redis 隔离

预检同时回读 test/prod Redis instance + DB index 的安全摘要。两者完全相同时中止。测试环境禁止执行无 DB 限定的 `FLUSHALL`；清理测试缓存只针对精确 test DB/namespace。

## 6. COS 隔离

当前 `CosPrivateActorMediaStorage` 的对象 key 为 `actor-private/<userId>/...`，没有环境前缀，因此本阶段固定使用独立测试 private bucket。只配置前缀而复用生产 bucket不作为当前合格方案。

测试桶至少验证：上传、签名读取和删除一个专用探针对象；探针 key 不含用户数据。验证生产桶对象计数/时间戳未被改变。

## 7. 外部能力策略矩阵

| 能力 | 测试默认 | 放开条件 |
|---|---|---|
| 短信 | 固定码/白名单 | 明确测试号码与次数上限 |
| 实名 | 禁用真实提交 | provider sandbox 或指定测试身份 |
| AI 生图 | 禁用 | 测试 provider/额度和实名门禁均就绪 |
| DeepSeek | 禁用或低额度 | 独立配置、审计和限额 |
| 微信回调 | 测试域名 | 回调签名与环境标识一致 |

禁止配置缺失时回退到 prod provider。

## 8. 测试前端产物

- 管理端 test 构建使用 test API，产物部署到 `html-test`。
- 小程序 test 构建只用于开发/体验版，并扫描 test API 存在、prod/local URL 不符合预期时阻断。
- release 构建使用生产 API，走既有 `build:mp-weixin:release` 和包体审计。

## 9. 证据与回滚

证据只保存脱敏目标和结果。测试环境回滚仅撤销 test server block、test container、html-test 和 test dataId；不得重启、覆盖或删除生产容器/配置/Schema。
