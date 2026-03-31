# 00-12 执行任务

## Workstream A — Spec 与权限矩阵建模

- [x] T1 新建 `00-12-admin-role-permission-tree` Spec 三件套
- [ ] T2 更新 Spec 索引，登记 `00-12 admin-role-permission-tree`
- [x] T3 建立后台角色权限 registry，明确模块、类别、标签与权限码映射

## Workstream B — 页面实现

- [x] T4 新增树形权限编辑组件，支持过滤、勾选统计和清空
- [x] T5 接入角色管理页，替换原三段权限码多选
- [x] T6 改善角色详情页权限展示，使其可读且可追溯

## Workstream C — 验证与回填

- [x] T7 运行 `npm run type-check`
- [x] T8 运行 `npm run build`
- [ ] T9 更新 Spec 验收状态与代码映射

## Notes

- `T2` 与 `T9` 依赖共享文档 `.sce/specs/README.md`、`.sce/specs/spec-code-mapping.md`；当前这两个文件已存在其他未提交改动，本轮先不整文件带入 commit，避免把无关变更一并提交。
