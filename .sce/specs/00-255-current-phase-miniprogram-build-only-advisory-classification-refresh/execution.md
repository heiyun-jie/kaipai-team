# 小程序构建期依赖审计分类刷新 - 执行记录

## 2026-09-02

- `npm audit --omit=dev` 报告 `browserslist` high 和 `postcss-selector-parser` low；两者均为间接依赖。
- `npm ls --omit=dev --all` 确认前者来自 Babel/Autoprefixer，后者来自 UniApp/PostCSS modules 编译链。
- Candidate `20260902-113826-v3-draft` 冻结小程序产物扫描：两个包运行时命中均为 `0`，source map 为 `0`，Node 包清单和 `node_modules` 为 `0`。
- 已只向构建期复核集合增加两个精确包名，并扩充 controlled-build-toolchain 单测；未知 advisory 阻断逻辑保持不变。
- 定向脚本测试 `8/8`、发布脚本全量测试 `75/75` 通过。
- 新 Candidate `20260902-145540-v3-draft` 的依赖门禁为 `PASSED / CONTROLLED_BUILD_TOOLCHAIN_ONLY`，`unreviewedAdvisoryPackages=[]`，风险决定为 `RISK_ACCEPTED_WITH_EXPIRY`，到期时间保持 `2026-09-30T23:59:59+08:00`。
- 新 Candidate 不再包含 `DEPENDENCY_AUDIT_REVIEW_PENDING`；保留的 `REMOTE_HELPER_NOT_VERIFIED / CREDENTIAL_RISK_PENDING` 只约束正式发布，不阻断隔离测试验收。
- 事务证据见 `evidence/VERIFICATION.txt`；回滚只在 `ROLLBACK_TEST_FILE.py` 上验证，业务脚本和 `MODIFIED_FILE.py` 保持修改态。
- 正式发布继续 `NOT_AUTHORIZED`。
