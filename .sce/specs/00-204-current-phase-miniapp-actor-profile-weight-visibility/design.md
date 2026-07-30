# 00-204 小程序个人档案体重常驻展示 - 技术设计

## 1. 边界判断

体重属于演员供给资料域。仓库已有唯一存储字段 `actor_profile.weight`、实体字段
`ActorProfile.weight`、请求字段 `ActorProfileCareerUpdateDTO.weight` 和响应字段
`ActorProfileRespDTO.weight`。本轮只调整可见入口并补合同门禁，不建立并行模型。

_Requirements: 3.1, 3.2, 3.3_

## 2. 前端设计

在 `kaipai-frontend/src/pages/actor-profile/edit.vue` 的
`profile-edit__measurements` 中加入第三个 `profile-edit__measurement`：

```vue
<label class="profile-edit__measurement">
  <text class="profile-edit__cell-label">体重</text>
  <view class="profile-edit__measurement-input">
    <input
      v-model.number="draft.career.weight"
      class="profile-edit__cell-input"
      type="number"
      placeholder="未填写"
    />
    <text class="profile-edit__unit">kg</text>
  </view>
</label>
```

现有测量项使用 `flex: 1`，相邻项使用同一条分隔线规则，因此无需新增或调整样式。
删除折叠职业资料中的原体重输入，避免同一字段出现两个编辑器；职业资料的其他节点保持
原样。

_Requirements: 3.1, 3.4_

## 3. 数据库设计

当前本地 `kaipai_dev` 与旧版 schema 测试夹具均已证明 `actor_profile.weight INT NULL` 存在，
因此不新增空操作迁移。只把 `actor_profile.weight` 加入本地后端启动前关键列检查，防止未来
缺列数据库在业务请求阶段才失败。

_Requirements: 3.2, 3.4_

## 4. 接口设计

继续使用既有合同：

```text
PUT /api/actor/profile/mine
request.career.weight: Integer | null, @Min(20), @Max(300)

GET /api/actor/profile/mine
PUT /api/actor/profile/mine
response.data.weight: Integer | null
```

通过 Controller 合同测试证明请求反序列化和响应序列化，通过 Service 测试证明值写入
`ActorProfile.weight`。不修改 Controller 路由，不新增 DTO，不更名字段。

_Requirements: 3.3, 3.4_

## 5. 验证设计

- 后端：schema gate 测试、Controller weight 合同测试、Service 持久化映射测试。
- 前端：`npm run type-check`、`npm run build:mp-weixin`，核对三层生成内容。
- 治理：`npm run audit:steering`、`npm run audit:mp-package`；已知非本轮失败需如实记录。

_Requirements: 3.1-3.4_
