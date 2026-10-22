# scoped 哈希分叉深度调查 - 技术设计

_Requirements: ALL_

## 1. 证据链（已实测）

| # | 证据 | 指向 |
|---|------|------|
| E1 | `dist/build` 三件套恒一致（0 分叉） | 构建产物无问题 |
| E2 | dev 分叉文件 wxss/js 与 build **逻辑相同、字节长度相同**，唯一差异是 scopeId（dev=`961980b7`、build=`f661c11f`） | dev 文件 = 「当前逻辑 + 另一个 scopeId」 |
| E3 | 重构建后 build scopeId 稳定（同内容不变） | scopeId 是内容/字节函数 |
| E4 | dev 分叉文件时间戳 = sync 后 26 秒（12:01:30→12:01:56） | **工具在 sync 后立即写回** |
| E5 | `WeappCache\WeappCompileCache\95f4fc6f...\9636e7d3...`（13615B，修改 12:01:58）内容含 `__scopeId: data-v-961980b7` | **工具项目编译缓存持有旧 scopeId 版本** |
| E6 | `cli cache --clean all` 清不到 WeappCache 深层目录 | 前 5 次「清缓存」未根治的原因 |
| E7 | 源码被加 BOM/尾部空行后 scopeId 漂移（f661c11f→1e84df6f） | scopeId 随文件字节变化；BOM 污染制造伪漂移 |

## 2. 机制

微信开发者工具把 `dist/dev` 当作**它的编译输出目录**：
1. 打开项目时对 js/wxss 做增量编译，结果按内容缓存到 `WeappCache\WeappCompileCache`（User Data 深层目录）
2. 工具编译**优先命中缓存**；检测到 dist/dev 文件变化时触发重编译，但可能命中/混合旧缓存（旧 scopeId）
3. 工具的编译结果**写回 dist/dev**（wxml 不写回）→ wxml=新 scopeId、wxss/js=旧 scopeId → 分叉 → scoped 样式整套静默失效

## 3. 根治（已固化 `sync-mp-weixin.ps1`）

```
每次同步前：Remove-WeappCache（清 User Data\*\WeappCache 整个目录）
```

- 工具下次打开基于**当前产物**重建缓存（新 scopeId），写回即新版本 → 分叉机制上消除
- 保留：工具进程检测拦截（运行中拒绝构建）、三方哈希断言（wxml vs wxss vs js）、dev 编译设置（es6/postcss/minified=false）

## 4. 判断标准（重要）

- **scopeId 数值会漂移**（f661c11f / 0d4be9b7 / 1e84df6f 均正常）——判断依据是 **wxml/wxss/js 三件套一致**，而非固定哈希
- 源码文件禁用会加 BOM 的写入（`Set-Content` 默认 UTF8 无 BOM，但 `Set-Content -Encoding UTF8` 在 PS5 加 BOM；统一用 UTF8 无 BOM 或 git checkout 还原）

## 5. 复现与验证

- 验证流程：改源码 → quit 工具 → build（sync 自动清 WeappCache）→ open → 等编译 → 全树复扫分叉 0 且 dev=build
- 两轮验证通过：0d4be9b7 实验、1e84df6f 干净重建
