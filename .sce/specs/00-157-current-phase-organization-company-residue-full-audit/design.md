# 00-157 设计

## 审查策略

分层审查：

1. 小程序：`kaipai-frontend/src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin`。
2. 后端：`kaipaile-server/src/main/java`、`src/main/resources/db/migration`、`target/classes`。
3. 后台：`kaipai-admin/src`、`kaipai-admin/dist`。
4. 数据库：仓库内 SQL、migration、schema、seed。
5. 路径名：小程序、后台、后端源码和构建目录中的旧域路径。

## 当前分享 MVP 边界

分享页 MVP 不需要机构/公司绑定：

- 选择风格
- 上传作品
- 命名并选择分享形式
- 保存并预览
- 卡片/海报预览与分享

因此海报名称只允许使用产品品牌或演员/用户数据，不允许依赖 `companyName`。

## 处理原则

- 不做旧字段兼容。
- 不保留用户可见旧入口。
- 不用默认机构名兜底来掩盖依赖。
- 不保留旧域命名路径、组件名、CSS 类名或构建产物字符串。
- 数据库旧线上值只通过备份后物理清理迁移处理，不通过兼容字段或别名处理。
- 对仍属于其他当前框架能力的内容，必须在审查记录中说明保留原因；否则删除或改名。
