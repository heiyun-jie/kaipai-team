# AI 资料册视觉接缝与封面遮罩修复 Execution

## 2026-05-20 Baseline

已按用户要求在开始本 spec 前提交所有项目代码基线：

| 仓库 | 分支 | 提交 |
| --- | --- | --- |
| `D:\XM\kaipai-team` | `main` | `3302e42 chore: checkpoint spec and runbook baseline` |
| `D:\XM\kaipai-team\kaipai-frontend` | `codex/card-share-membership-refactor` | `f2308d4 fix: render generated backgrounds for all profile pages` |
| `D:\XM\kaipai-team\kaipaile-server` | `master` | `de39574 feat: add profile card continuity metadata flow` |

未提交并保持隔离的本地文件：

1. `SecretKey.csv`
2. `output/`
3. 临时日志和临时 HTML
4. 后端 `target/classes`
5. 前端临时 probe 脚本

## 2026-05-20 Spec Scope

本 spec 只处理：

1. 封面左上遮罩白块。
2. 封面右下白色遮挡。
3. `cover -> resume -> gallery` 的确定性顶部参考带接续。
4. 对应 prompt 强化、字段消费、截图验证。

不处理：

1. 厂商注册。
2. 后台配置页新增功能。
3. 任意页数长图。
4. OCR 主路径。
5. 历史任务批量迁移。

## Agent Execution Log

### 2026-05-20 Frontend Worker

Frontend agency worker 完成：

1. 移除封面 `cover-identity-shield` 与 `cover-watermark-shield` 的默认渲染和样式。
2. 非 cover 页新增 `continuityReferenceUrl` 顶部参考带渲染。
3. `continuityBandRatio` 默认 `0.15`，边界限制为 `0.08 ~ 0.22`。
4. 参考带底部使用主题底色轻量 fade，避免重新制造白块。
5. 前端 `npm run type-check` 通过。

主工作区集成后又将 fade 从黑色暗化调整为主题底色过渡，避免 15% 接缝处出现硬横线。

### 2026-05-20 Backend Worker

Backend agency worker 完成：

1. 强化 `cover` prompt：底部约 `15%` 必须是干净、低细节、无人物身体、无衣料主体、无文字、无 Logo、无二维码、无卡片和无 UI 的可延展背景过渡带。
2. 强化 `resume/gallery` prompt：顶部约 `15%` 必须接近上一页参考带的主要形状、色彩、光线、纹理和空间方向，像从上一页底部继续向下生成。
3. 同步更新 Tencent 混元压缩 prompt，避免真实 provider payload 丢失强化语义。
4. 确认 `AiProfileCardPageRespDTO` 已返回前端需要的 continuity 字段。
5. 补充服务层 DTO 返回测试和 prompt/provider 单测断言。

### 2026-05-20 Local Verification

本地验证命令：

```text
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check

cd D:\XM\kaipai-team\kaipaile-server
mvn -q -DskipTests compile
mvn -q "-Dtest=AiProfileCardPromptAgentTest,TencentHunyuanProfileImageProviderTest,AiProfileCardServiceImplTest" test
```

结果：

1. 前端 type-check 通过。
2. 后端 compile 通过。
3. 后端定向单测通过。
4. Maven 测试期间仅出现 `spring-jcl` / JVM CDS 非阻断 warning。

H5 mock 截图验证脚本：

```text
D:\XM\kaipai-team\output\diagnostics\run-ai-profile-card-visual-seam-repair-h5.js
```

运行结果文件：

```text
D:\XM\kaipai-team\output\diagnostics\run-ai-profile-card-visual-seam-repair-h5-result.json
```

关键检查值：

```json
{
  "pages": ["cover", "resume", "gallery"],
  "posterCount": 3,
  "posterBgCount": 3,
  "continuityBandCount": 2,
  "identityShieldCount": 0,
  "watermarkShieldCount": 0,
  "bandHeights": [
    "--ai-continuity-band-height: 15.00%;",
    "--ai-continuity-band-height: 15.00%;"
  ]
}
```

截图证据：

1. `D:\XM\kaipai-team\output\diagnostics\with-task-cover.png`
2. `D:\XM\kaipai-team\output\diagnostics\with-task-resume.png`
3. `D:\XM\kaipai-team\output\diagnostics\with-task-gallery.png`
4. `D:\XM\kaipai-team\output\diagnostics\with-task-full-page.png`

## Remaining Risk

1. H5 mock 已验证渲染契约；真实小程序仍需要基于新生成任务再截图，因为历史任务可能只有 `cover` 有 `generatedImageUrl`。
2. 前端确定性贴上了上一页底部参考带；参考带下方与当前页生成图是否完全自然，仍取决于新 prompt 下 provider 的实际生成质量。
3. 如果 provider 继续输出水印，本轮不再用前端白块遮挡，应回到 provider 配置、重新生成或服务端审核策略处理。
