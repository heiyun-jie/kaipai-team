# 小程序构建期依赖审计分类刷新 - 技术设计

## 1. 影响范围

- `.sce/runbooks/backend-admin-release/scripts/build-release-candidate-artifacts.py`
- `.sce/runbooks/backend-admin-release/scripts/tests/test_build_release_candidate_artifacts.py`
- Candidate `artifact-evidence.json / candidate-manifest.json`

不修改 `package.json`、lockfile、前端业务实现、后端实现或数据库迁移。

## 2. 依赖与产物证明

本地依赖树证明：

```text
UniApp compiler -> Babel/Autoprefixer -> browserslist
UniApp compiler/PostCSS modules -> postcss-selector-parser
```

冻结小程序证明必须同时满足：

```text
browserslist runtime matches = 0
postcss-selector-parser runtime matches = 0
source map count = 0
package manifest/node_modules count = 0
```

_Requirements: 3.1_

## 3. 分类逻辑

在既有构建期复核集合中增加两个精确包名。最终 `passed` 仍由以下条件共同决定：critical 为 0、未复核包为空、运行时 i18n 安全、无 source map、无包清单、无禁止工具链标记。

任何一个条件失败时仍返回 `REVIEW_REQUIRED / NOT_ACCEPTED`。

_Requirements: 3.2, 3.3_

## 4. 测试

- 扩充 controlled-build-toolchain 单测 fixture，包含两个新增包并断言 `unreviewedAdvisoryPackages=[]`。
- 保留未知 advisory、旧 i18n 和产物标记阻断测试。
- 执行发布脚本目录全量 `unittest discover`。

_Requirements: 4_

## 5. 回滚

回滚只移除两个精确包名及对应测试/Spec 登记。回滚后新 Candidate 会恢复 `DEPENDENCY_AUDIT_REVIEW_PENDING`，不会改变已经冻结的历史 Candidate。
