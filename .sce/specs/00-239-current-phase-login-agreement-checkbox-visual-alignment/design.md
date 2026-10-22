# 登录页协议勾选框视觉对齐 - 技术设计

_Requirements: 2.1-2.3, 3_

## 1. 根因

`t-checkbox` 自身已经在 shadow/component 内部渲染 `.t-checkbox__icon-circle`。页面又对自定义组件宿主 `.login-page__checkbox` 设置 `width`、`height`、`border-radius` 和 `border`，所以宿主圆框与内部圆环同时可见；两个盒子的尺寸与中心参考线不同，最终呈现偏心双圆。移除宿主圆框后，未选中态恢复为单圆，但默认选中态依赖已为包体治理移除的 TDesign 图标字体，运行时只生成空的 `t-icon-check-circle-filled`，无法显示勾选标记。

## 2. 实现

保持 `t-checkbox`，不回退原生 `checkbox`：

- 组件显式使用 `:icon="agreementCheckboxIcons"`、`borderless`、`:block="false"`。
- 图标数组按 TDesign 约定提供 `[checked, unchecked]`，分别使用随包生成的官方 `check-circle-filled-brand.svg` 与 `circle-agreement.svg`，不依赖图标字体或远程资源。
- 通过 `custom-style` 在组件真实根节点设置 `--td-checkbox-icon-size: 32rpx`、图标行高和透明背景。
- 页面宿主只保留 `flex: 0 0 auto` 与垂直对齐，不再绘制任何圆、背景或伪图标。
- 协议行 `gap` 归零，由 TDesign `.t-checkbox__icon--left` 的内部间距作为唯一图标/文案间距。

## 3. 验证

新增 `scripts/verify-00239-login-agreement-checkbox.mjs`，检查：

1. Spec 三件套和索引存在。
2. 登录页仍使用 TDesign checkbox，且显式设置本地 SVG 图标数组、borderless/32rpx CSS 变量。
3. 页面宿主不再包含 width/height/border/border-radius 或 checked 伪状态。
4. 事件仍绑定 `handleAgreementChange`，协议链接事件仍独立。
5. build/dev 产物包含相同 SVG 路径、CSS 变量和宿主规则，scope hash 一致。
6. dev 产物只包含 test API。

## 4. 兼容边界

本轮不修改 `agreed` 状态来源、登录按钮 disabled/open-type、协议弹窗或测试环境后端。修复后重新冻结小程序测试产物，`00-236` 继续保持等待人工验收，不能自动进入生产。
