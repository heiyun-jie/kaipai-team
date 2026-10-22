# 素材库三列照片网格 - 技术设计

_Requirements: 3.1-3.3, 4, 5_

## 1. 路由与范围

| 路由 | 角色 | 变更 |
|------|------|------|
| `pages/assets/index` | Tab 根页素材管理 | 照片类型改为三列网格 |
| `pkg-profile/assets/index` | 资料/演员卡素材选择 | 照片类型改为三列网格并保留选择覆盖层 |

视频和 PDF 继续走当前 `.assets-page__row` 列表。脚本、API、store、后端和数据库不变。

## 2. 模板结构

两个页面均在 `.assets-page__list` 内按 `mediaType` 分支：

```text
assets-page__list
├── mediaType === photo -> assets-page__photo-grid
│   └── assets-page__photo-tile × N
│       ├── t-image 或单格占位
│       ├── 非 ready 状态条（按需）
│       └── 更多按钮或选择态圆标
├── mediaType !== photo -> assets-page__row × N
└── 共用 empty / loading / error / retry
```

普通素材库的照片格点击调用 `handleAsset(asset)`，右上角更多按钮使用 `.stop` 调用 `openActions(asset)`。资料素材页沿用同一 `handleAsset`；选择模式显示 `.assets-page__photo-check`，非选择模式显示更多按钮。

## 3. 尺寸与视觉合同

```scss
.assets-page__photo-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: $kp-spacing-gap;
  padding: $kp-spacing-gap $kp-spacing-xl;
}

.assets-page__photo-tile {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: $kp-radius-button;
}
```

按 `750rpx` 画布计算：`(750 - 40*2 - 16*2) / 3 = 212.67rpx`。`t-image` 填满格子并使用 `aspectFill`；占位、错误和处理态占据相同尺寸。覆盖按钮位于右上角，状态条位于底部，不参与网格布局计算。

## 4. 状态设计

- ready + 签名地址：显示图片。
- ready + 签名失败：显示当前媒体错误图标；其他格不受影响。
- processing / failed：显示等尺寸占位，并在底部展示当前状态。
- 资料选择模式 selected：蓝色描边和蓝底勾选圆标。
- 资料选择模式 disabled：降低图片透明度，但保持格子尺寸和点击门禁。

照片名称和分类不在网格正文中重复展示；管理动作仍可从每格更多菜单进入。视频/PDF列表继续显示完整名称、分类、状态和失败信息。

## 5. 验证设计

新增 `scripts/verify-00227-asset-photo-grid.mjs` 并接入 `package.json`，验证：

1. 两个源码页面均存在 `mediaType === 'photo'` 分支、`photo-grid` 和 `photo-tile`。
2. 两页均存在三列、`40rpx` 横向边距、`16rpx` gap 和 1:1 比例。
3. 视频/PDF分支仍包含 `.assets-page__row`、失败重试和更多菜单。
4. 资料素材页仍包含 selected、disabled 与选择圆标。
5. build/dev 两侧 WXML 存在照片网格节点，WXSS 存在三列、间距和比例规则。

实施后运行：

```text
npm run type-check
npm run verify:asset-photo-grid
npm run verify:tdesign-migration
uni build -p mp-weixin
powershell -File scripts/sync-mp-weixin.ps1
```

同步后检查 build/dev scope hash 一致，并使用微信开发者工具内部接口打开 `pages/assets/index` 截图和测量三列格子。资料选择页以可发现的真实入口或带参数路由核验选择覆盖层。

## 6. 发布兼容

本次只有 Vue 模板、SCSS、验证脚本和治理文档变化。请求与响应、素材记录、签名 URL、缓存键、上传参数和数据库均不变，因此后端无需同步发布，也不需要数据迁移。

## 7. 实施结果（2026-08-20）

- 两个页面的照片 Tab 已按三列 1:1 网格渲染，视频/PDF继续使用原信息列表。
- 普通素材页照片右上角更多菜单运行正常；资料选择页未选、选中和不可用覆盖层保持独立。
- `verify:asset-photo-grid` 共 48 项通过；`verify:tdesign-migration` 1327 项、`verify:v3-asset-wizard` 68 项继续全绿。
- build/dev 三件套完全一致：主素材页 scope hash 为 `data-v-abd3888b`，资料素材页为 `data-v-5cbe1f68`。
- 微信模拟器实测 `390px` 视口下网格左右内边距各 `20px`、列间距 `8px`、单格 `111.328125px × 111.328125px`，对应 `40rpx / 16rpx / 212.67rpx` 设计合同。
- 运行态证据：`.sce/evidence/wechat-devtools/00-227-assets-photo-grid-20260820.png`、`00-227-assets-photo-grid-actions-20260820.png`、`00-227-profile-assets-photo-grid-select-20260820.png`、`00-227-profile-assets-photo-grid-selected-20260820.png`。
