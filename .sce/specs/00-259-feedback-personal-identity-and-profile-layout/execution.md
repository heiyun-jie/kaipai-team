# 执行记录

## 2026-10-13 本地交付

来源为用户提供的 `问题反馈.xlsx`，只读提取六张截图，未改动原工作簿。用户授权创建 Spec 并开始修复。保持三个仓库当前 V3.0 分支与原有未提交工作。

### 实现与兼容

- `pages/mine/index` 每次 onShow 读取本人档案，以 avatarAssetId 现签展示照片；无档案头像或加载失败回退账号头像。签名只在页面内存保存；账号、会话 token、请求序号保护异步回写。图片错误回调绑定当次 URL，旧图片重复错误不影响回退头像。
- `pages/actor-profile/edit` 新增账号昵称，独立于公开名称，加入草稿、dirty baseline、回填与保存。成功后更新账号昵称缓存。
- 取消 `mine-v2__role-badge`；实名认证徽标继续根据事实源显示。年龄、身高、体重为三个 `profile-edit__measurement` 标准行，沿用岁 / cm / kg 与现有字段。
- 后端 GET/PUT `/api/actor/profile/mine` 增加可选 nickname。账号昵称写既有 `user.user_name`，公开名继续写 `actor_profile.nick_name`；旧请求不传 nickname 不更新账号。档案版本/头像归属校验与昵称写入处于同一事务。
- 零数据库迁移。新前端昵称必须同批后端部署；旧后端没有该字段，不能单独发布新前端后宣称昵称持久化已生效。

### 验证

| 检查 | 结果 |
|------|------|
| `npm run verify:feedback-october` | 11/11；含新签名、游客零请求、异账号晚到响应、重复旧图片 error 与 COS 缩略回退 |
| `npm run type-check` | 通过 |
| `npm run verify:v3-mine` | 20 项通过 |
| 后端 `mvn '-Dtest=ActorProfileWriteServiceImplTest,ActorProfileControllerContractTest' package` | 16 项通过，JAR 打包成功 |
| `npm run build:mp-weixin` | `RUNTIME_BUILD=PASS`；直接更新固定 dist/dev，无 build/dev 镜像 |
| TDesign / 素材网格 / 游客门禁 | 865 / 34 / 13 项通过，核对固定 dev |
| 单运行入口 / steering audit | 通过 |
| `npm run audit:mp-package` | 通过，主包 1,409,185 B，全部四个分包低于 2 MB |

完整 `mvn package` 执行 745 项，0 assertion failure、46 error；八组 Docker/MySQL 集成测试因 `Could not find a valid Docker environment` 或后续上下文初始化错误失败。专项打包通过不等于完整套件通过；后续有 Docker 时需补跑完整套件。

固定 dev 的 WXML/WXSS/JS 已核对：昵称与公开名称两输入、三个独立测量行、100% 输入宽度、无演员徽标、档案头像与签名调用。全量 scoped 哈希归一化一致，dev es6/postcss/minified 均关闭。

### 工具启动纠偏

最初固定构建被四个微信工具进程拦截。用户说明未启动工具后，进程证据确认它们均在 17:03:37 由本次 MCP runtime_info 查询的 `wechatide://skill/auth?clientName=Codex` 启动。已使用固定项目的正常 quit 命令退出，随后构建成功；未强杀任意进程、未置顶或控制用户桌面。查询返回找不到 runtimeid，不作为页面运行验收证据。后续未经用户授权不再通过该调用触发授权窗口。

### 待验

- 资料完整度与三项统计是否移除尚无裁决，暂保留。
- 尚未完成新 Candidate 冻结、后端部署、真机视觉与持久化回归。本轮旧 Candidate 不代表新代码输入，发布前需重新冻结并完成同批全栈验收。
- 未上传体验版、未操作生产环境。

复跑专项：在 kaipai-frontend 执行 `npm run verify:feedback-october`。

## 2026-10-20 完整度与统计区删除

用户裁决红框区“直接删除”。

- 删除个人页“资料完整度”卡片与“演员卡 / 素材 / 浏览”统计行、加载逻辑、跳转函数与样式；前端 `getProfileCompleteness` / `ProfileCompletenessDTO` 无其它消费方，一并删除。后端完整度接口保留（旧前端兼容），零后端/DB 变更。
- `verify-v3-mine.mjs` 将三条旧断言替换为反向断言，18/18 通过。

| 检查 | 结果 |
|------|------|
| `npm run verify:feedback-october` | 14/14 |
| `npm run verify:v3-mine` | 18/18 |
| `npm run verify:v3-home` | 17/17 |
| `npm run type-check` | 通过 |
| `npm run build:mp-weixin` | `RUNTIME_BUILD=PASS`，scoped 哈希一致 |
| 固定 dist/dev `pages/mine/index.{wxml,js,wxss}` | “资料完整度” / `mine-v2__stat` / `completeness` 均为 0 |
| `audit:mp-package` / `audit:steering` | 通过 |

未部署、未上传体验版；新 Candidate 与真机验收仍待 T5。
