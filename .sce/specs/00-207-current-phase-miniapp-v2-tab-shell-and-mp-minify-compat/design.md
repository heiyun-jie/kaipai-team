# 00-207 技术设计 — v2 Tab 壳层胶囊对齐、个人页游客态与小程序压缩兼容

## 1. 改动范围

| 文件 | 改动性质 | 关联需求 |
|------|---------|---------|
| `kaipai-frontend/src/pages/home/index.vue` | 标题行胶囊对齐 + 风格卡宽高比 | 3.1, 3.4 |
| `kaipai-frontend/src/pages/card-list/index.vue` | 标题行胶囊对齐 | 3.1 |
| `kaipai-frontend/src/pages/mine/index.vue` | 标题行胶囊对齐 + 游客态收口 | 3.1, 3.2 |
| `kaipai-frontend/vite.config.ts` | 关闭 mp 产物压缩 | 3.3 |
| `kaipai-frontend/scripts/start-miniapp.py` | dev watch 去重 + 真实构建等待 | 3.5 |

本 Spec 不修改 API 层、Store、路由注册、`pages.json`、TabBar、后端接口、数据库或权限。

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

## 2. 标题行胶囊对齐

### 2.1 现状问题

三个 Tab 页原先都用静态 padding 排布标题行：

```scss
&__title-row { padding: 12rpx 32rpx 0; }      // home
&__title-row { padding: 16rpx 32rpx 8rpx; }   // card-list
&__header-row { padding: 12rpx 32rpx 20rpx; } // mine
```

`KpCapsuleSpacer` 只占位状态栏与导航高度，静态 padding 无法保证标题文字与右上角胶囊按钮垂直居中对齐，机型间偏移不可控。

### 2.2 方案

复用既有 `src/utils/floating-back-nav.ts`，它已经封装 `uni.getMenuButtonBoundingClientRect()` 并提供降级值：

```ts
backButtonStyle: {
  top: `${menuButtonTop}px`,      // menuButtonRect.top ?? statusBarHeight + 8
  height: `${menuButtonHeight}px`, // menuButtonRect.height ?? 32
}
```

三页统一改为：header 容器 `position: relative`，标题行 `position: absolute` 并由内联 style 接收 `top / height`，配合 `display: flex; align-items: center` 让文字在胶囊等高带内垂直居中。

```vue
<view class="home-v2__title-row" :style="{ top: backButtonStyle.top, height: backButtonStyle.height }">
```

```scss
&__header { position: relative; }
&__title-row {
  position: absolute;
  left: 32rpx;
  right: 200rpx;   // 让出右上角胶囊按钮区域
  display: flex;
  align-items: center;
}
```

`right: 200rpx` 是标题文本的安全右边界，保证长标题不与胶囊重叠。

### 2.3 absolute 造成的文档流补偿

标题行脱离文档流后，原先由它撑起的高度必须由 header 自身或后继元素补回，否则下方内容上移：

| 页面 | 补偿方式 |
|------|---------|
| `home` | `&__greeting { margin-top: 12rpx; }` |
| `card-list` | `&__tabs { margin-top: 16rpx; }` |
| `mine` | `&__header { padding-bottom: 20rpx; }` |

三页补偿方式不同，因为标题行下方的首个元素不同（问候语 / Tab 条 / 直接是内容区）。

_Requirements: 3.1_

## 3. 个人页游客态收口

### 3.1 判定口径改为 `hasStoredSession`

原先 `isLoggedIn` 直接取 `userStore.isLoggedIn`。改为以 `hasStoredSession` 为唯一游客判定源：

```ts
const isVisitor = computed(() => !userStore.hasStoredSession);
const isLoggedIn = computed(() => !isVisitor.value);
```

`hasStoredSession` 已由 `00-192` 建立为全局会话等价语义，本轮不新增会话判定逻辑，只让个人页对齐该口径，避免会话已存在但用户对象尚未 hydrate 时误判为游客。

### 3.2 统一账号能力门禁

新增两个本页函数，替换所有直接 `uni.navigateTo`：

```ts
function requireLoginForMineAction(): boolean {
  if (isVisitor.value) {
    uni.navigateTo({ url: '/pages/login/index' });
    return false;
  }
  return true;
}

function openAccountCapability(url: string): void {
  if (!requireLoginForMineAction()) return;
  uni.navigateTo({ url });
}
```

改为经由 `openAccountCapability` 的入口：个人资料、演艺经历、自我介绍、实名认证、`goEditProfile()`。

保持直接跳转不变的入口：帮助、关于（非账号能力），`goCardList()`（`switchTab` 到名片夹，游客可浏览）。

### 3.3 展示名回退链

```ts
const displayName = computed(() => {
  if (isVisitor.value) return '未登录用户';
  return currentUser.value?.nickname || formatPhone(currentUser.value?.phone || '') || '演员用户';
});
```

已登录但无昵称时回退到 `formatPhone()` 脱敏手机号，再回退到 `演员用户`，不再出现「已登录却显示未登录用户」。`formatPhone` 复用既有 `src/utils/format.ts`，不新增脱敏实现。

### 3.4 请求边界

`onShow` 的完整度请求门禁由 `userStore.isLoggedIn` 改为 `isVisitor`，与页面展示口径同源：

```ts
onShow(async () => {
  if (isVisitor.value) return;
  // getProfileCompleteness()
});
```

同时移除未使用的 `onMounted` import。

_Requirements: 3.2_

## 4. 小程序产物压缩兼容

### 4.1 问题与决策

esbuild 压缩产物中出现小程序 JS 引擎无法解析的语法形态（改动注释记录为 `?.5:` 形态），导致页面 JS 解析失败，表现为 `navigateTo` timeout 与白屏。

```ts
build: {
  minify: false,
}
```

用户已明确要求保留该配置。这是一个**以包体换运行时可解析性**的取舍：压缩关闭后主包体积上升，因此包体审计结果必须作为该配置的持续门禁，一旦逼近单包 `2 MB` 约束需回到本 Spec 重新评估（候选方向：改用 `terser` 或按 target 降级，而非无条件关闭压缩）。

### 4.2 兼容边界

`minify: false` 作用于全部构建目标，不只 mp-weixin。本轮只验证 mp-weixin 链路；H5 与其它小程序平台不在本 Spec 验证范围。

_Requirements: 3.3_

## 5. 首页风格卡宽高比

```scss
&__style-img-wrap { width: 100%; aspect-ratio: 3/2; }  // 原 3/4
```

`3/4` 竖版让 2×2 风格网格首屏占高过大。改为 `3/2` 横版压缩网格总高。仅改容器宽高比，`&__style-img` 的 `width/height: 100%` 与 `--placeholder` 兜底不变。

_Requirements: 3.4_

## 6. 本地启动脚本

### 6.1 dev watch 去重

原脚本无条件启动 `dev:mp-weixin`，外部终端已有 watch 时会重复启动、争抢同一 `dist/dev` 输出目录。新增只读 `Win32_Process` 查询：

```python
def has_existing_dev_watch() -> bool:
    # 匹配 vite-plugin-uni + (-p|--platform) mp-weixin + 本项目路径
```

三个条件同时命中才算已有 watch，避免误杀其它项目的 uni 进程。查询失败、超时或无 PowerShell 时返回 `False`，退化为原有行为，不阻塞启动。

### 6.2 真实构建等待

原 `wait_for_dev_build()` 只判断 `app.json` 是否存在，上一轮遗留产物会让它立即返回 `True`，开发者工具随即加载旧产物。改为签名比对：

```python
def file_signature(path) -> tuple[int, int] | None:
    return stat.st_mtime_ns, stat.st_size
```

传入构建前签名，轮询直到签名**发生变化**才算本轮构建完成；轮询间隔从 `1s` 收到 `0.5s`。同时新增 `proc.poll()` 检查，watch 在首次构建完成前退出时直接 `raise SystemExit`，不再静默等到超时。

`open_devtools` 的形参类型标注由 `str` 修正为 `Path`，与实际传入值一致。

_Requirements: 3.5_

## 7. 验证设计

### 7.1 静态门禁

`scripts/verify-miniapp-v2-tab-shell-and-mp-minify.mjs` 按可理解的合同逐项断言，不做整文件快照：

- 三页各自的 `backButtonStyle` 内联绑定、`getFloatingBackNavStyles` import、header `position: relative`、标题行 `position: absolute`
- 三页各自的文档流补偿声明
- `mine` 的 `hasStoredSession` 判定、`openAccountCapability` 定义、四个账号入口均经由该函数、`goCardList` 保持 `switchTab`
- `vite.config.ts` 的 `minify: false`
- `home` 的 `aspect-ratio: 3/2`
- `00-201 / 00-205` 保护项：Hero 文案、`480rpx` 舞台、阴阳鱼位图、`goAiProfileCard` / `goCardList`、瀑布流入口

### 7.2 运行时与产物门禁

1. `npm run type-check`
2. `npm run build:mp-weixin`（postbuild 自动同步 `dist/build` → `dist/dev`）
3. `src / dist/build / dist/dev` 三层 grep 核对关键字已进入产物
4. `npm run audit:mp-package` — 记录 `minify: false` 下的真实包体
5. `npm run audit:steering`

_Requirements: 4, 5_
