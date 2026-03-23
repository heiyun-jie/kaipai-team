# 共享工具函数与 API 层

## 1. 概述

本模块为"开拍了"(KaiPai)小程序提供统一的 TypeScript 类型定义、HTTP 请求封装、登录态管理、文件上传、格式化工具、表单校验、Pinia 状态管理以及所有后端 API 的调用封装。技术栈基于 uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + Pinia，后端为 Spring Boot 3.2.3 RESTful API（前缀 `/api`）。

## 2. 用户故事

- 作为前端开发者，我希望有统一的类型定义，以便在整个项目中保持类型安全。
- 作为前端开发者，我希望有封装好的请求工具，自动处理 Token 注入、错误提示和 Loading 状态，减少重复代码。
- 作为前端开发者，我希望有统一的登录态管理，方便在任意页面判断登录状态和用户角色。
- 作为前端开发者，我希望有文件上传封装，支持图片和视频上传到 MinIO，并自动校验文件大小。
- 作为前端开发者，我希望有格式化工具和表单校验规则，避免在各页面重复编写相同逻辑。
- 作为前端开发者，我希望所有 API 调用都有明确的入参和返回类型，便于 IDE 自动补全和编译期检查。

## 3. 功能需求

### 3.1 TypeScript 类型定义 (types/*.ts)

**描述**: 定义所有数据库实体对应的前端 TypeScript 接口，以及通用的 API 响应类型、分页类型等。

**函数签名**:

```typescript
// types/common.ts
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

interface PageParams {
  page: number;
  size: number;
}

interface PageResult<T> {
  total: number;
  list: T[];
  page: number;
  size: number;
}

// types/user.ts
interface UserInfo {
  id: number;
  phone: string;
  role: 1 | 2; // 1=演员 2=剧组
  status: number;
  token?: string;
}

// types/actor.ts
interface ActorProfile {
  userId: number;
  name: string;
  gender: string;
  age: number;
  height: number;
  city: string;
  avatar: string;
  intro: string;
  photos: string[];
  videoUrl: string;
  skillTypes: string[];
}

// types/company.ts
interface Company {
  userId: number;
  companyName: string;
  contactName: string;
  contactPhone: string;
  remark: string;
}

// types/project.ts
interface Project {
  id: number;
  companyId: number;
  title: string;
  description: string;
  location: string;
  status: 1 | 2; // 1=进行中 2=已结束
}

// types/role.ts
interface Role {
  id: number;
  projectId: number;
  roleName: string;
  gender: string;
  minAge: number;
  maxAge: number;
  requirement: string;
  fee: string;
  deadline: string;
}

// types/apply.ts
interface Apply {
  id: number;
  roleId: number;
  actorId: number;
  status: 1 | 2 | 3; // 1=待审核 2=通过 3=拒绝
  remark: string;
}
```

**验收标准**:
- WHEN 开发者导入类型定义 THEN 所有实体接口均可用且字段与数据库实体一一对应
- WHEN 使用 ApiResponse 泛型 THEN 能正确推断 data 字段的类型
- WHEN 使用 PageResult 泛型 THEN 能正确推断 list 元素的类型

### 3.2 请求封装 (utils/request.ts)

**描述**: 基于 `uni.request` 封装统一的 HTTP 请求工具，支持 Base URL 配置、Token 自动注入、统一错误处理（code !== 200）、Loading 状态管理、请求/响应类型泛型。

**函数签名**:

```typescript
interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: Record<string, any>;
  header?: Record<string, string>;
  showLoading?: boolean;
  loadingText?: string;
  showError?: boolean;
}

function request<T = any>(options: RequestOptions): Promise<T>;
function get<T = any>(url: string, data?: Record<string, any>, options?: Partial<RequestOptions>): Promise<T>;
function post<T = any>(url: string, data?: Record<string, any>, options?: Partial<RequestOptions>): Promise<T>;
function put<T = any>(url: string, data?: Record<string, any>, options?: Partial<RequestOptions>): Promise<T>;
function del<T = any>(url: string, data?: Record<string, any>, options?: Partial<RequestOptions>): Promise<T>;
```

**验收标准**:
- WHEN 发起请求且本地存在 Token THEN 请求头自动携带 `Authorization: Bearer <token>`
- WHEN 后端返回 code !== 200 THEN 自动弹出错误提示（uni.showToast）并 reject Promise
- WHEN 后端返回 code === 401 THEN 清除本地 Token 并跳转到登录页
- WHEN showLoading 为 true THEN 请求期间显示 uni.showLoading，请求结束后隐藏
- WHEN 网络异常 THEN 提示"网络异常，请稍后重试"
- WHEN 使用泛型调用 THEN 返回值类型正确推断为 T

### 3.3 登录态管理 (utils/auth.ts)

**描述**: 提供 Token 的存取与清除、登录状态判断、角色判断等工具函数，基于 uni.setStorageSync / uni.getStorageSync 实现持久化。

**函数签名**:

```typescript
const TOKEN_KEY = 'kp_token';
const USER_KEY = 'kp_user';

function getToken(): string | null;
function setToken(token: string): void;
function removeToken(): void;
function isLoggedIn(): boolean;
function getUserInfo(): UserInfo | null;
function setUserInfo(user: UserInfo): void;
function removeUserInfo(): void;
function isActor(): boolean;
function isCrew(): boolean;
```

**验收标准**:
- WHEN 调用 setToken THEN Token 持久化到 uni storage，后续 getToken 可获取
- WHEN 调用 removeToken THEN storage 中 Token 被清除，getToken 返回 null
- WHEN 用户未登录 THEN isLoggedIn 返回 false
- WHEN 用户角色为 1 THEN isActor 返回 true，isCrew 返回 false
- WHEN 用户角色为 2 THEN isCrew 返回 true，isActor 返回 false

### 3.4 文件上传封装 (utils/upload.ts)

**描述**: 封装 `uni.uploadFile`，支持图片和视频上传到 MinIO，自动携带 Token，校验文件大小（视频最大 100MB），支持上传进度回调。

**函数签名**:

```typescript
interface UploadOptions {
  filePath: string;
  fileType: 'image' | 'video';
  onProgress?: (progress: number) => void;
}

interface UploadResult {
  url: string;
  key: string;
}

function uploadFile(options: UploadOptions): Promise<UploadResult>;
function uploadImage(filePath: string, onProgress?: (progress: number) => void): Promise<UploadResult>;
function uploadVideo(filePath: string, onProgress?: (progress: number) => void): Promise<UploadResult>;
function chooseAndUploadImage(count?: number): Promise<UploadResult[]>;
function chooseAndUploadVideo(): Promise<UploadResult>;
```

**验收标准**:
- WHEN 上传视频且文件大小超过 100MB THEN 提示"视频大小不能超过100MB"并拒绝上传
- WHEN 上传文件 THEN 请求头自动携带 Authorization Token
- WHEN 上传过程中 THEN onProgress 回调被正确调用，参数为 0-100 的进度值
- WHEN 上传成功 THEN 返回包含 url 和 key 的 UploadResult
- WHEN 上传失败 THEN 提示错误信息并 reject Promise

### 3.5 格式化工具 (utils/format.ts)

**描述**: 提供常用的数据格式化函数，包括日期格式化、手机号脱敏、文件大小格式化、性别文本转换、状态文本转换等。

**函数签名**:

```typescript
function formatDate(date: string | number | Date, format?: string): string;
function formatPhone(phone: string): string;
function formatFileSize(bytes: number): string;
function formatGender(gender: string): string;
function formatProjectStatus(status: 1 | 2): string;
function formatApplyStatus(status: 1 | 2 | 3): string;
function formatAge(minAge: number, maxAge: number): string;
function formatFee(fee: string): string;
```

**验收标准**:
- WHEN formatDate('2024-01-15T10:30:00') THEN 返回 "2024-01-15 10:30"（默认格式）
- WHEN formatPhone('13812345678') THEN 返回 "138****5678"
- WHEN formatFileSize(104857600) THEN 返回 "100MB"
- WHEN formatGender('male') THEN 返回 "男"
- WHEN formatProjectStatus(1) THEN 返回 "进行中"
- WHEN formatApplyStatus(2) THEN 返回 "已通过"
- WHEN formatAge(18, 25) THEN 返回 "18-25岁"
- WHEN formatFee('500') THEN 返回 "¥500"

### 3.6 表单校验规则 (utils/validate.ts)

**描述**: 提供常用的表单校验函数和 uview-plus 兼容的校验规则生成器，用于手机号、姓名、年龄、身高等字段的校验。

**函数签名**:

```typescript
interface ValidateRule {
  required?: boolean;
  message: string;
  trigger?: string;
  validator?: (rule: any, value: any) => boolean;
  pattern?: RegExp;
  min?: number;
  max?: number;
  type?: string;
}

function isPhone(value: string): boolean;
function isValidAge(age: number): boolean;
function isValidHeight(height: number): boolean;

function phoneRule(required?: boolean): ValidateRule[];
function nameRule(required?: boolean): ValidateRule[];
function ageRule(required?: boolean): ValidateRule[];
function heightRule(required?: boolean): ValidateRule[];
function requiredRule(message: string): ValidateRule[];
function videoUrlRule(): ValidateRule[];
```

**验收标准**:
- WHEN isPhone('13812345678') THEN 返回 true
- WHEN isPhone('1234567') THEN 返回 false
- WHEN isValidAge(25) THEN 返回 true
- WHEN isValidAge(-1) THEN 返回 false
- WHEN isValidAge(200) THEN 返回 false
- WHEN isValidHeight(175) THEN 返回 true
- WHEN isValidHeight(0) THEN 返回 false
- WHEN 使用 phoneRule() 校验空值 THEN 返回必填错误信息
- WHEN 使用 phoneRule() 校验非法手机号 THEN 返回格式错误信息

### 3.7 用户状态 Store (stores/user.ts)

**描述**: 基于 Pinia 的用户状态管理 Store，管理用户信息、Token、登录状态、角色判断，提供登录和登出 action。

**函数签名**:

```typescript
interface UserState {
  userInfo: UserInfo | null;
  token: string | null;
}

const useUserStore = defineStore('user', {
  state: (): UserState,
  getters: {
    isLoggedIn: (state) => boolean,
    isActor: (state) => boolean,
    isCrew: (state) => boolean,
    userId: (state) => number | null,
  },
  actions: {
    initFromStorage(): void,
    login(phone: string, code: string): Promise<UserInfo>,
    setUserData(user: UserInfo, token: string): void,
    logout(): void,
    updateProfile(profile: Partial<UserInfo>): void,
  },
});
```

**验收标准**:
- WHEN 调用 initFromStorage THEN 从 uni storage 恢复 token 和 userInfo
- WHEN 调用 login 成功 THEN userInfo 和 token 被设置，并持久化到 storage
- WHEN 调用 login 失败 THEN reject Promise 并保持原状态
- WHEN 调用 logout THEN 清除 userInfo、token 和 storage，跳转到登录页
- WHEN isLoggedIn THEN 当且仅当 token 不为空时返回 true
- WHEN isActor THEN 当且仅当 userInfo.role === 1 时返回 true
- WHEN isCrew THEN 当且仅当 userInfo.role === 2 时返回 true

### 3.8 API 模块 - 认证 (api/auth.ts)

**描述**: 封装认证相关的 API 调用，包括发送验证码、手机号登录、获取用户信息、微信登录等。

**函数签名**:

```typescript
function sendSmsCode(phone: string): Promise<void>;
function loginByPhone(phone: string, code: string): Promise<{ token: string; user: UserInfo }>;
function loginByWechat(code: string): Promise<{ token: string; user: UserInfo }>;
function getUserInfo(): Promise<UserInfo>;
function updateUserRole(role: 1 | 2): Promise<void>;
```

**验收标准**:
- WHEN 调用 sendSmsCode 传入合法手机号 THEN 发送 POST /api/auth/sms-code 请求
- WHEN 调用 loginByPhone THEN 发送 POST /api/auth/login 请求并返回 token 和用户信息
- WHEN 调用 loginByWechat THEN 发送 POST /api/auth/wechat-login 请求
- WHEN 调用 getUserInfo THEN 发送 GET /api/auth/user-info 请求并返回用户信息
- WHEN 调用 updateUserRole THEN 发送 PUT /api/auth/role 请求

### 3.9 API 模块 - 演员 (api/actor.ts)

**描述**: 封装演员资料相关的 API 调用，包括获取/更新演员资料、演员列表搜索等。

**函数签名**:

```typescript
interface ActorSearchParams extends PageParams {
  gender?: string;
  minAge?: number;
  maxAge?: number;
  city?: string;
  skillType?: string;
  keyword?: string;
}

function getActorProfile(userId: number): Promise<ActorProfile>;
function updateActorProfile(data: Partial<ActorProfile>): Promise<void>;
function searchActors(params: ActorSearchParams): Promise<PageResult<ActorProfile>>;
function getActorDetail(userId: number): Promise<ActorProfile>;
```

**验收标准**:
- WHEN 调用 getActorProfile THEN 发送 GET /api/actor/profile/{userId} 请求
- WHEN 调用 updateActorProfile THEN 发送 PUT /api/actor/profile 请求
- WHEN 调用 searchActors 带筛选条件 THEN 发送 GET /api/actor/search 请求并携带查询参数
- WHEN 调用 getActorDetail THEN 发送 GET /api/actor/{userId} 请求并返回完整演员资料

### 3.10 API 模块 - 剧组 (api/company.ts)

**描述**: 封装剧组/公司相关的 API 调用，包括获取/更新公司信息。

**函数签名**:

```typescript
function getCompanyInfo(userId: number): Promise<Company>;
function updateCompanyInfo(data: Partial<Company>): Promise<void>;
function getMyCompany(): Promise<Company>;
```

**验收标准**:
- WHEN 调用 getCompanyInfo THEN 发送 GET /api/company/{userId} 请求
- WHEN 调用 updateCompanyInfo THEN 发送 PUT /api/company 请求
- WHEN 调用 getMyCompany THEN 发送 GET /api/company/mine 请求并返回当前用户的公司信息

### 3.11 API 模块 - 项目 (api/project.ts)

**描述**: 封装项目相关的 API 调用，包括项目的增删改查和列表查询。

**函数签名**:

```typescript
interface ProjectSearchParams extends PageParams {
  status?: 1 | 2;
  location?: string;
  keyword?: string;
}

function createProject(data: Omit<Project, 'id'>): Promise<Project>;
function updateProject(id: number, data: Partial<Project>): Promise<void>;
function deleteProject(id: number): Promise<void>;
function getProject(id: number): Promise<Project>;
function getProjectList(params: ProjectSearchParams): Promise<PageResult<Project>>;
function getMyProjects(params: PageParams): Promise<PageResult<Project>>;
```

**验收标准**:
- WHEN 调用 createProject THEN 发送 POST /api/project 请求并返回创建的项目
- WHEN 调用 updateProject THEN 发送 PUT /api/project/{id} 请求
- WHEN 调用 deleteProject THEN 发送 DELETE /api/project/{id} 请求
- WHEN 调用 getProject THEN 发送 GET /api/project/{id} 请求
- WHEN 调用 getProjectList 带筛选条件 THEN 发送 GET /api/project/list 请求并携带查询参数
- WHEN 调用 getMyProjects THEN 发送 GET /api/project/mine 请求

### 3.12 API 模块 - 角色 (api/role.ts)

**描述**: 封装角色（招募需求）相关的 API 调用，包括角色的增删改查。

**函数签名**:

```typescript
interface RoleSearchParams extends PageParams {
  projectId?: number;
  gender?: string;
  minAge?: number;
  maxAge?: number;
}

function createRole(data: Omit<Role, 'id'>): Promise<Role>;
function updateRole(id: number, data: Partial<Role>): Promise<void>;
function deleteRole(id: number): Promise<void>;
function getRole(id: number): Promise<Role>;
function getRolesByProject(projectId: number, params?: PageParams): Promise<PageResult<Role>>;
function searchRoles(params: RoleSearchParams): Promise<PageResult<Role>>;
```

**验收标准**:
- WHEN 调用 createRole THEN 发送 POST /api/role 请求并返回创建的角色
- WHEN 调用 updateRole THEN 发送 PUT /api/role/{id} 请求
- WHEN 调用 deleteRole THEN 发送 DELETE /api/role/{id} 请求
- WHEN 调用 getRole THEN 发送 GET /api/role/{id} 请求
- WHEN 调用 getRolesByProject THEN 发送 GET /api/role/project/{projectId} 请求
- WHEN 调用 searchRoles 带筛选条件 THEN 发送 GET /api/role/search 请求并携带查询参数

### 3.13 API 模块 - 投递 (api/apply.ts)

**描述**: 封装投递（报名）相关的 API 调用，包括投递申请、审核、查询等。

**函数签名**:

```typescript
interface ApplySearchParams extends PageParams {
  status?: 1 | 2 | 3;
  roleId?: number;
}

function submitApply(roleId: number, remark?: string): Promise<Apply>;
function cancelApply(applyId: number): Promise<void>;
function getMyApplies(params: ApplySearchParams): Promise<PageResult<Apply>>;
function getAppliesByRole(roleId: number, params: ApplySearchParams): Promise<PageResult<Apply>>;
function approveApply(applyId: number): Promise<void>;
function rejectApply(applyId: number, remark?: string): Promise<void>;
function getApplyDetail(applyId: number): Promise<Apply>;
```

**验收标准**:
- WHEN 调用 submitApply THEN 发送 POST /api/apply 请求并返回投递记录
- WHEN 调用 cancelApply THEN 发送 DELETE /api/apply/{applyId} 请求
- WHEN 调用 getMyApplies THEN 发送 GET /api/apply/mine 请求
- WHEN 调用 getAppliesByRole THEN 发送 GET /api/apply/role/{roleId} 请求
- WHEN 调用 approveApply THEN 发送 PUT /api/apply/{applyId}/approve 请求
- WHEN 调用 rejectApply THEN 发送 PUT /api/apply/{applyId}/reject 请求
- WHEN 调用 getApplyDetail THEN 发送 GET /api/apply/{applyId} 请求

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **类型安全**: 所有函数必须有完整 TypeScript 类型标注，禁止 `any`（ApiResponse 泛型默认值除外）
- **错误处理**: 所有 API 调用统一错误处理，网络异常和业务异常分别处理
- **性能**: 请求封装直接基于 uni.request，不引入额外依赖；文件上传支持进度回调
- **可维护性**: 工具函数必须为纯函数（auth 相关除外），便于单元测试

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 后端 API 前缀 `/api`，Base URL 通过 `VITE_API_BASE_URL` 配置
- Token 存储 key `kp_token`，用户信息存储 key `kp_user`
- 文件上传接口 POST `/api/upload`，返回 `{ url, key }`
- 视频最大 100MB，图片最大 10MB
- API 响应格式 `{ code: 200, message: "success", data: {} }`
- Pinia Store 命名遵循 `use{Name}Store`
- 校验规则兼容 uview-plus 表单校验机制
