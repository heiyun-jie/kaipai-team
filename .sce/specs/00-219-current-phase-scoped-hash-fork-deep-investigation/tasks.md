# 00-219 深度调查 - 任务清单

---

## 调查结论（2026-08-14，已根治）

**最终根因（证据链）**：
1. `dist/build` 三件套恒一致；dev 分叉 = wxss/js 是「当前逻辑 + 旧 scopeId `961980b7`」（与 build 逻辑相同、仅 scopeId 不同）→ 非 npm 构建产物
2. 工具编译缓存 `WeappCache\WeappCompileCache`（User Data 深层目录）持有旧 scopeId 版本（实测缓存文件含 `__scopeId: data-v-961980b7`，修改时间 = sync 后 28 秒）——工具检测到 dist/dev 变化后用旧缓存写回 js/wxss
3. `cli cache --clean all` 清不到该深层目录（前 5 次「清缓存」未根治的原因）
4. scopeId 会随构建输入文件字节（换行符/BOM）漂移（f661c11f → 1e84df6f），但**只要 build 三件套一致 + 工具写回与 dev 一致，即无分叉、样式正常**

**根治（已固化 sync-mp-weixin.ps1）**：`Remove-WeappCache` —— 每次同步前清整个 `User Data\*\WeappCache`，工具下次打开基于当前产物重建缓存（新 scopeId），写回即新版本。

**验证（两轮）**：
- ① 改源码（注释）→ scopeId 变 0d4be9b7 → build→sync→open→工具重编译 → **dev 分叉 0、dev=build**（写回新版本）
- ② 还原源码后干净重建 → scopeId 1e84df6f → build→sync→open → **dev 分叉 0、dev=build**
- ③ 全树复扫 0；KpPageNav.vue 还原后工作区干净（仅 sync 脚本改动）

**教训**：①写文件禁止用会加 BOM 的 Set-Content（污染源码字节 → scopeId 漂移）；②工具写回来源是 WeappCache 深层缓存，常规清缓存命令清不到；③scopeId 数值会漂移，判断标准是「wxml/wxss/js 三件套一致」而非「固定哈希值」。
