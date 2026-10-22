# 五张参考图的视觉标注

> 说明：以下值均为相对关系与归一化目标，不把不同尺寸的 PNG 原始像素直接写进业务样式。平台状态栏、微信胶囊和动态人像属于对齐参考或掩膜区。

## 全局模板

| 项目 | 图稿共性 | 实施规则 |
|---|---|---|
| 画布 | 大面积纯白，无深色 Hero、米色底或装饰性渐变球 | R01-R05 页面背景为 canvas |
| 主体留白 | 左右约 40rpx，正文与固定 CTA 同轴 | 不用 24rpx 默认值覆盖参考页 |
| 字体 | 黑色大标题、灰色说明、蓝色强调 | Display 48、H1 40、H2 32、Body 28、ListTitle 26、Caption 24、Micro 22 |
| 卡片 | 白底、轻细边框、16rpx 圆角，留白大于阴影 | 只有激活分段等局部状态可用很轻的阴影 |
| 品牌色 | `#2F6BFF` 视觉集中 | CTA、进度、链接、选中和认证；不将整页染蓝 |
| 底部 | 固定 CTA 或原生 TabBar，正文预留安全区 | 不与最后一项重叠 |

## R01 首页 / `pages/home/index`

| 锚点 | 图稿关系 | 样式模板 | 交互边界 |
|---|---|---|---|
| 顶部 | 品牌标题左对齐，问候语在下一层；胶囊不与正文抢位 | Tab 根页 `ReferenceNav` | 无返回按钮 |
| Hero | 40rpx 页面边距内的浅蓝大卡；左侧为星芒、40rpx 主标题、两行说明、蓝色 CTA；上下留白克制但不拥挤；右侧三层半透明演员卡插画占据 Hero 高度的大半 | `ReferenceCard` + 浅蓝局部背景，左右双栏 | 点击 CTA 进入真实创建流程 |
| 草稿 | 标题后是一张横向卡：方形封面、草稿状态、进度条、右侧“继续” | 媒体卡，封面 144rpx 级 | 真实草稿列表；无草稿时不伪造 |
| 模板 Tab | 经典/都市/古风/清新四等分文字，选中项为蓝色文字和下划线 | `ReferenceSegmentedTabs.home` | Tab 仍过滤真实背景库 |
| 模板网格 | 两列媒体卡，图片在上、风格名称在下 | `ReferenceMediaGrid` 两列变体 | 点击传真实 backgroundId |

## R02 创建 Hub / `pkg-actor-card/create/index`

| 锚点 | 图稿关系 | 样式模板 | 交互边界 |
|---|---|---|---|
| 顶部 | 返回箭头与胶囊同带；“AI 创建演员卡”按整屏居中 | `ReferenceNav.wizard` | KpPageNav 持有定位，调用方不拼胶囊 |
| 进度 | “创建进度 2/7”后接长进度轨；轨道与正文同轴 | `ReferenceProgress.hub` | `doneCount` 是服务端状态派生 |
| 引导 | H1“准备演员资料”+ 灰色说明，距进度区有完整区块间距 | `ReferenceSection` | 无独立重复导航标题 |
| 步骤卡 | 7 张等高白卡；浅蓝方形线稿图标、标题/说明、右侧状态与箭头 | `ReferenceCard.step`，最低 144rpx | 跳转、状态、失败重试和防重复点击保留 |
| CTA | 页面最下方全宽蓝色“继续下一项” | `ReferenceBottomCta` | 真实进入下一未完成步骤或生成页 |

## R03 参演作品 / `pkg-actor-card/step-works/index`

| 锚点 | 图稿关系 | 样式模板 | 交互边界 |
|---|---|---|---|
| 顶部/进度 | 居中标题、左侧返回、单独 `3/7` 与进度轨 | `ReferenceNav.wizard` + `ReferenceProgress.step` | 当前步固定为 3 |
| 说明区 | H1“选择参演作品”及一行辅助说明 | `ReferenceSection` | 标题与导航不是重复语句 |
| 分段 Tab | 浅灰外轨、白色激活段、蓝色激活文字 | `ReferenceSegmentedTabs.form` | 在经历选择和新增作品间切换 |
| 作品卡 | 首列蓝色圆勾/空圆，随后类别、标题/角色，右侧剧照计数和管理入口；剧照位于下一视觉行且与文本区对齐 | `ReferenceCard.work` + 横向媒体带 | 经历、新增、剧照选择/替换/删除/封面/排序与保存全部真实 |
| 追加/CTA | 细蓝边“添加其他作品”，其后显示已选数；底部蓝色“下一步” | `ReferenceBottomCta` | 不删除空态、失败和保存反馈 |

## R04 生活照片 / `pkg-actor-card/step-photos/index`

| 锚点 | 图稿关系 | 样式模板 | 交互边界 |
|---|---|---|---|
| 顶部/进度 | 居中标题、`4/7` 与同轴进度轨 | `ReferenceNav.wizard` + `ReferenceProgress.step` | 当前步固定为 4 |
| 上限提示 | 蓝色信息提示条位于说明区之后 | `ReferenceCard.notice` | 真实限制维持最多 12 张；图中 13 张是示例，不照搬为产品限制 |
| 上传入口 | 两张等宽、白底细边框的大按钮：素材库 / 手机上传 | `ReferenceCard.action` | 素材库 requestId 和手机上传均可达 |
| 计数/排序 | 左侧“已选择 N 张”，右侧蓝色“调整顺序” | `ReferenceSection.inlineAction` | 默认无每格上移/下移；进入排序模式后才显示 |
| 照片网格 | 三列方格、16rpx 间距；序号在左上、删除在右上；最后是虚线继续添加格 | `ReferenceMediaGrid.threeColumn` | 删除确认、封面第 1 张、保存回读不变 |
| CTA | 与网格同轴的蓝色“下一步” | `ReferenceBottomCta` | 上传/保存/跳转期间锁定 |

## R05 个人中心 / `pages/mine/index`

| 锚点 | 图稿关系 | 样式模板 | 交互边界 |
|---|---|---|---|
| 顶部 | “个人”左对齐，胶囊保持平台原位 | `ReferenceNav.tab` | Tab 根页无返回 |
| 档案卡 | 148rpx 级圆头像、姓名、普通“演员”文字、白底蓝边认证标签、右箭头；卡片外高约 192rpx，卡内左上留白薄于普通卡片 | `ReferenceCard.profile` | 点击进入真实资料页 |
| 完整度 | 标题与大百分比同行；蓝色进度轨和“继续完善”同行；百分比为 H1 层级，卡片约 160rpx | `ReferenceCard.completeness` | 完整度 API、失败重试与资料页跳转保留 |
| 统计卡 | 三列等宽、居中数字和标签，以细竖线分隔；数字使用 H1，不用 Display，卡片约 128rpx | `ReferenceCard.stats` | 演员卡/素材跳真实 Tab；浏览只读 |
| 分组列表 | “演员资料”“账户与服务”标题后是细边框分组；线性图标、主副文案、右箭头；资料双行 row 约 112rpx，主文案 26rpx、副文案 22rpx；服务单行 row 约 76rpx，主文案 24rpx；图标为 2rpx 轻线稿，服务行图标与文字轴线比资料双行更紧 | `ReferenceCard.listGroup` | 实名认证、帮助与反馈、设置均可达真实页面；退出登录收在设置页 |
| TabBar | 四个线性图标和文字；个人项蓝色 | `ReferenceTabBar` | 原生 TabBar 语义不变 |
