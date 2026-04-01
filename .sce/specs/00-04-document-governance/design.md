# 文档治理 - 技术设计

_Requirements: 00-04 全部_

## 1. 文档分层策略

| 文档层 | 作用 | 处理策略 |
|------|------|------|
| `docs/product-design.md` | 当前产品主文档 | 重写为现行主线 |
| `docs/archive/*` | 历史产品资料 | 归档旧版本，禁止继续作为当前实现依据 |
| `docs/dev-playbook.md` | 开发经验和治理经验 | 更新主线约束和归档规则 |
| `.sce/specs/README.md` | Spec 索引入口 | 新增文档治理 Spec 并校正主线描述 |
| `.sce/specs/spec-code-mapping.md` | Spec ↔ 代码事实映射 | 修正已漂移的数量和状态 |

## 2. 归档策略

### 2.1 归档目录

新增：

```text
docs/archive/
```

### 2.2 归档命名

旧版 `product-design.md` 归档为带版本和日期的文件，例如：

```text
docs/archive/product-design-v1.2-2026-03-23.md
```

### 2.3 主文档回链

新的 `docs/product-design.md` 需在文首给出：

- 当前文档定位
- 历史归档入口
- 当前主线和历史搁置范围

## 3. 当前主线文档结构

新的 `docs/product-design.md` 采用收敛结构：

1. 当前产品定位
2. 当前主线范围与非范围
3. 页面与入口结构
4. 名片分享与会员分层
5. AI 润色与后续衔接
6. 当前验收重点
7. 历史归档说明

不再把旧信用页面、旧入口和旧组件写成当前功能正文。

## 4. 事实对齐策略

### 4.1 以当前仓库为准

- 页面数量：以 `src/pages.json` 当前注册页面为准
- 组件数量：以 `src/components/Kp*.vue` 为准
- API / utils / types 数量：以当前目录文件数为准
- 主线状态：以 `05-05` Spec 与当前源码实现为准

### 4.2 历史信息保留方式

- `05-03` 信用积分方案只允许出现在历史说明或历史 Spec 引导中
- 若文档仍需提及旧信用方案，只写“已搁置，详见历史 Spec / 归档文档”

## 5. 验证方式

使用文本扫描确认非历史层文档中不再把以下内容写成当前主线：

- `我的信用分`
- `积分记录`
- `排行榜`
- `KpCreditBadge`
- `KpLevelTag`

允许命中位置：

- `docs/archive/*`
- `.sce/specs/05-03-*`
- `.sce/specs/05-01-*` 中的历史说明

## 6. 交付物

- 文档治理 Spec 三件套
- 新版 `docs/product-design.md`
- 归档版旧 `product-design` 文档
- 更新后的开发手册和 Spec 索引 / 映射
- 一份治理报告或记录
