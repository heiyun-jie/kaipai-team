# 共享工具函数与 API 层 - 技术设计

## 1. 架构概览

本模块采用分层架构，自底向上依次为：

- **类型层 (types/)**: 定义所有数据实体接口和通用类型
- **工具层 (utils/)**: 提供请求封装、登录态管理、文件上传、格式化、校验等基础能力
- **状态层 (stores/)**: 基于 Pinia 管理全局用户状态
- **API 层 (api/)**: 封装所有后端接口调用，依赖请求封装和类型定义

依赖关系：`api/ → utils/request.ts → utils/auth.ts → types/`

## 2. 文件结构

```
src/
├── types/
│   ├── common.ts          # 通用类型（ApiResponse, PageParams, PageResult）
│   ├── user.ts            # 用户类型
│   ├── actor.ts           # 演员资料类型
│   ├── company.ts         # 剧组/公司类型
│   ├── project.ts         # 项目类型
│   ├── role.ts            # 角色类型
│   └── apply.ts           # 投递类型
├── utils/
│   ├── request.ts         # HTTP 请求封装
│   ├── auth.ts            # 登录态管理
│   ├── upload.ts          # 文件上传封装
│   ├── format.ts          # 格式化工具
│   └── validate.ts        # 表单校验规则
├── stores/
│   └── user.ts            # 用户状态 Store
└── api/
    ├── auth.ts            # 认证 API
    ├── actor.ts           # 演员 API
    ├── company.ts         # 剧组 API
    ├── project.ts         # 项目 API
    ├── role.ts            # 角色 API
    └── apply.ts           # 投递 API
```

## 3. TypeScript 类型定义

### types/common.ts

```typescript
/** 统一 API 响应结构 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/** 分页请求参数 */
export interface PageParams {
  page: number;
  size: number;
}

/** 分页响应结果 */
export interface PageResult<T> {
  total: number;
  list: T[];
  page: number;
  size: number;
}
```

### types/user.ts

```typescript
/** 用户信息 */
export interface UserInfo {
  id: number;
  phone: string;
  role: UserRole;
  status: number;
  token?: string;
}

/** 用户角色枚举 */
export enum UserRole {
  Actor = 1,
  Crew = 2,
}

/** 登录响应 */
export interface LoginResult {
  token: string;
  user: UserInfo;
}
```

### types/actor.ts

```typescript
import type { PageParams } from './common';

/** 演员资料 */
export interface ActorProfile {
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

/** 演员搜索参数 */
export interface ActorSearchParams extends PageParams {
  gender?: string;
  minAge?: number;
  maxAge?: number;
  city?: string;
  skillType?: string;
  keyword?: string;
}
```

### types/company.ts

```typescript
/** 剧组/公司信息 */
export interface Company {
  userId: number;
  companyName: string;
  contactName: string;
  contactPhone: string;
  remark: string;
}
```

### types/project.ts

```typescript
import type { PageParams } from './common';

/** 项目状态 */
export enum ProjectStatus {
  Active = 1,
  Ended = 2,
}

/** 项目信息 */
export interface Project {
  id: number;
  companyId: number;
  title: string;
  description: string;
  location: string;
  status: ProjectStatus;
}

/** 项目搜索参数 */
export interface ProjectSearchParams extends PageParams {
  status?: ProjectStatus;
  location?: string;
  keyword?: string;
}
```

### types/role.ts

```typescript
import type { PageParams } from './common';

/** 角色（招募需求） */
export interface Role {
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

/** 角色搜索参数 */
export interface RoleSearchParams extends PageParams {
  projectId?: number;
  gender?: string;
  minAge?: number;
  maxAge?: number;
}
```

### types/apply.ts

```typescript
import type { PageParams } from './common';

/** 投递状态 */
export enum ApplyStatus {
  Pending = 1,
  Approved = 2,
  Rejected = 3,
}

/** 投递记录 */
export interface Apply {
  id: number;
  roleId: number;
  actorId: number;
  status: ApplyStatus;
  remark: string;
}

/** 投递搜索参数 */
export interface ApplySearchParams extends PageParams {
  status?: ApplyStatus;
  roleId?: number;
}
```

## 4. 请求封装实现

### utils/request.ts

```typescript
import { getToken, removeToken } from './auth';
import type { ApiResponse } from '@/types/common';

/** 请求配置 */
interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: Record<string, any>;
  header?: Record<string, string>;
  /** 是否显示 loading，默认 true */
  showLoading?: boolean;
  /** loading 提示文字 */
  loadingText?: string;
  /** 是否显示错误提示，默认 true */
  showError?: boolean;
}

/** API Base URL，从环境变量读取 */
const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || '';

/** 当前正在进行的请求数（用于 loading 计数） */
let requestCount = 0;

function showLoadingIndicator(text: string): void {
  if (requestCount === 0) {
    uni.showLoading({ title: text, mask: true });
  }
  requestCount++;
}

function hideLoadingIndicator(): void {
  requestCount--;
  if (requestCount <= 0) {
    requestCount = 0;
    uni.hideLoading();
  }
}

function handleUnauthorized(): void {
  removeToken();
  uni.removeStorageSync('kp_user');
  uni.reLaunch({ url: '/pages/login/index' });
}

/**
 * 核心请求函数
 */
export function request<T = any>(options: RequestOptions): Promise<T> {
  const {
    url,
    method = 'GET',
    data,
    header = {},
    showLoading = true,
    loadingText = '加载中...',
    showError = true,
  } = options;

  const token = getToken();
  if (token) {
    header['Authorization'] = `Bearer ${token}`;
  }
  if (!header['Content-Type']) {
    header['Content-Type'] = 'application/json';
  }

  if (showLoading) {
    showLoadingIndicator(loadingText);
  }

  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success: (res) => {
        const response = res.data as ApiResponse<T>;
        if (response.code === 200) {
          resolve(response.data);
          return;
        }
        if (response.code === 401) {
          handleUnauthorized();
          reject(new Error('登录已过期，请重新登录'));
          return;
        }
        if (showError) {
          uni.showToast({ title: response.message || '请求失败', icon: 'none', duration: 2000 });
        }
        reject(new Error(response.message || '请求失败'));
      },
      fail: (err) => {
        if (showError) {
          uni.showToast({ title: '网络异常，请稍后重试', icon: 'none', duration: 2000 });
        }
        reject(new Error(err.errMsg || '网络异常，请稍后重试'));
      },
      complete: () => {
        if (showLoading) {
          hideLoadingIndicator();
        }
      },
    });
  });
}

/** GET 请求快捷方法 */
export function get<T = any>(
  url: string,
  data?: Record<string, any>,
  options?: Partial<RequestOptions>,
): Promise<T> {
  return request<T>({ url, method: 'GET', data, ...options });
}

/** POST 请求快捷方法 */
export function post<T = any>(
  url: string,
  data?: Record<string, any>,
  options?: Partial<RequestOptions>,
): Promise<T> {
  return request<T>({ url, method: 'POST', data, ...options });
}

/** PUT 请求快捷方法 */
export function put<T = any>(
  url: string,
  data?: Record<string, any>,
  options?: Partial<RequestOptions>,
): Promise<T> {
  return request<T>({ url, method: 'PUT', data, ...options });
}

/** DELETE 请求快捷方法 */
export function del<T = any>(
  url: string,
  data?: Record<string, any>,
  options?: Partial<RequestOptions>,
): Promise<T> {
  return request<T>({ url, method: 'DELETE', data, ...options });
}
```

**使用示例**:

```typescript
import { get, post } from '@/utils/request';
import type { UserInfo } from '@/types/user';
import type { PageResult } from '@/types/common';
import type { ActorProfile } from '@/types/actor';

// 获取用户信息
const user = await get<UserInfo>('/api/auth/user-info');

// 提交登录
await post('/api/auth/login', { phone: '13812345678', code: '1234' });

// 分页列表
const result = await get<PageResult<ActorProfile>>('/api/actor/search', { page: 1, size: 10 });

// 不显示 loading
await get<UserInfo>('/api/auth/user-info', undefined, { showLoading: false });
```

## 5. 登录态管理实现

### utils/auth.ts

```typescript
import type { UserInfo } from '@/types/user';

const TOKEN_KEY = 'kp_token';
const USER_KEY = 'kp_user';

/** 获取 Token */
export function getToken(): string | null {
  return uni.getStorageSync(TOKEN_KEY) || null;
}

/** 设置 Token */
export function setToken(token: string): void {
  uni.setStorageSync(TOKEN_KEY, token);
}

/** 移除 Token */
export function removeToken(): void {
  uni.removeStorageSync(TOKEN_KEY);
}

/** 判断是否已登录 */
export function isLoggedIn(): boolean {
  return !!getToken();
}

/** 获取用户信息 */
export function getUserInfo(): UserInfo | null {
  const raw = uni.getStorageSync(USER_KEY);
  if (!raw) return null;
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    return null;
  }
}

/** 保存用户信息 */
export function setUserInfo(user: UserInfo): void {
  uni.setStorageSync(USER_KEY, JSON.stringify(user));
}

/** 移除用户信息 */
export function removeUserInfo(): void {
  uni.removeStorageSync(USER_KEY);
}

/** 判断当前用户是否为演员 */
export function isActor(): boolean {
  const user = getUserInfo();
  return user?.role === 1;
}

/** 判断当前用户是否为剧组 */
export function isCrew(): boolean {
  const user = getUserInfo();
  return user?.role === 2;
}
```

## 6. 文件上传封装实现

### utils/upload.ts

```typescript
import { getToken } from './auth';
import type { ApiResponse } from '@/types/common';

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || '';
const UPLOAD_URL = '/api/upload';
const MAX_IMAGE_SIZE = 10 * 1024 * 1024;  // 10MB
const MAX_VIDEO_SIZE = 100 * 1024 * 1024; // 100MB

interface UploadOptions {
  filePath: string;
  fileType: 'image' | 'video';
  onProgress?: (progress: number) => void;
}

interface UploadResult {
  url: string;
  key: string;
}

/**
 * 获取文件大小（字节）
 */
function getFileSize(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    uni.getFileInfo({
      filePath,
      success: (res) => resolve(res.size),
      fail: (err) => reject(new Error(err.errMsg || '获取文件信息失败')),
    });
  });
}

/**
 * 上传文件到 MinIO
 */
export function uploadFile(options: UploadOptions): Promise<UploadResult> {
  const { filePath, fileType, onProgress } = options;
  const maxSize = fileType === 'video' ? MAX_VIDEO_SIZE : MAX_IMAGE_SIZE;
  const sizeLabel = fileType === 'video' ? '100MB' : '10MB';

  return new Promise(async (resolve, reject) => {
    try {
      const size = await getFileSize(filePath);
      if (size > maxSize) {
        const msg = `${fileType === 'video' ? '视频' : '图片'}大小不能超过${sizeLabel}`;
        uni.showToast({ title: msg, icon: 'none' });
        reject(new Error(msg));
        return;
      }
    } catch {
      // 部分平台可能不支持 getFileInfo，继续上传
    }

    const token = getToken();
    const uploadTask = uni.uploadFile({
      url: `${BASE_URL}${UPLOAD_URL}`,
      filePath,
      name: 'file',
      formData: { fileType },
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        try {
          const data = JSON.parse(res.data) as ApiResponse<UploadResult>;
          if (data.code === 200) {
            resolve(data.data);
          } else {
            uni.showToast({ title: data.message || '上传失败', icon: 'none' });
            reject(new Error(data.message || '上传失败'));
          }
        } catch {
          reject(new Error('解析上传响应失败'));
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败，请重试', icon: 'none' });
        reject(new Error(err.errMsg || '上传失败'));
      },
    });

    if (onProgress && uploadTask) {
      uploadTask.onProgressUpdate((res) => {
        onProgress(res.progress);
      });
    }
  });
}

/** 上传图片 */
export function uploadImage(
  filePath: string,
  onProgress?: (progress: number) => void,
): Promise<UploadResult> {
  return uploadFile({ filePath, fileType: 'image', onProgress });
}

/** 上传视频 */
export function uploadVideo(
  filePath: string,
  onProgress?: (progress: number) => void,
): Promise<UploadResult> {
  return uploadFile({ filePath, fileType: 'video', onProgress });
}

/** 选择并上传图片 */
export function chooseAndUploadImage(count = 1): Promise<UploadResult[]> {
  return new Promise((resolve, reject) => {
    uni.chooseImage({
      count,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        try {
          const results = await Promise.all(
            res.tempFilePaths.map((path) => uploadImage(path)),
          );
          resolve(results);
        } catch (err) {
          reject(err);
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '选择图片失败')),
    });
  });
}

/** 选择并上传视频 */
export function chooseAndUploadVideo(): Promise<UploadResult> {
  return new Promise((resolve, reject) => {
    uni.chooseVideo({
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      compressed: true,
      success: async (res) => {
        try {
          const result = await uploadVideo(res.tempFilePath);
          resolve(result);
        } catch (err) {
          reject(err);
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '选择视频失败')),
    });
  });
}
```

## 7. 格式化工具实现

### utils/format.ts

```typescript
/**
 * 日期格式化
 * @param date 日期字符串、时间戳或 Date 对象
 * @param format 格式模板，默认 'YYYY-MM-DD HH:mm'
 */
export function formatDate(
  date: string | number | Date,
  format = 'YYYY-MM-DD HH:mm',
): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';

  const pad = (n: number): string => String(n).padStart(2, '0');

  const map: Record<string, string> = {
    YYYY: String(d.getFullYear()),
    MM: pad(d.getMonth() + 1),
    DD: pad(d.getDate()),
    HH: pad(d.getHours()),
    mm: pad(d.getMinutes()),
    ss: pad(d.getSeconds()),
  };

  let result = format;
  for (const [key, value] of Object.entries(map)) {
    result = result.replace(key, value);
  }
  return result;
}

/** 手机号脱敏：138****5678 */
export function formatPhone(phone: string): string {
  if (!phone || phone.length !== 11) return phone || '';
  return `${phone.slice(0, 3)}****${phone.slice(7)}`;
}

/** 文件大小格式化 */
export function formatFileSize(bytes: number): string {
  if (bytes <= 0) return '0B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, index);
  const formatted = size % 1 === 0 ? String(size) : size.toFixed(2);
  return `${formatted}${units[index]}`;
}

/** 性别文本转换 */
export function formatGender(gender: string): string {
  const map: Record<string, string> = { male: '男', female: '女', unknown: '未知' };
  return map[gender] || gender;
}

/** 项目状态文本 */
export function formatProjectStatus(status: 1 | 2): string {
  const map: Record<number, string> = { 1: '进行中', 2: '已结束' };
  return map[status] || '未知';
}

/** 投递状态文本 */
export function formatApplyStatus(status: 1 | 2 | 3): string {
  const map: Record<number, string> = { 1: '待审核', 2: '已通过', 3: '已拒绝' };
  return map[status] || '未知';
}

/** 年龄范围格式化 */
export function formatAge(minAge: number, maxAge: number): string {
  if (minAge && maxAge) return `${minAge}-${maxAge}岁`;
  if (minAge) return `${minAge}岁以上`;
  if (maxAge) return `${maxAge}岁以下`;
  return '不限';
}

/** 费用格式化 */
export function formatFee(fee: string): string {
  if (!fee) return '面议';
  return `¥${fee}`;
}
```

## 8. 表单校验规则实现

### utils/validate.ts

```typescript
/** 校验规则接口（兼容 uview-plus） */
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

const PHONE_REG = /^1[3-9]\d{9}$/;

/** 校验手机号 */
export function isPhone(value: string): boolean {
  return PHONE_REG.test(value);
}

/** 校验年龄（1-120） */
export function isValidAge(age: number): boolean {
  return Number.isInteger(age) && age >= 1 && age <= 120;
}

/** 校验身高（50-250 cm） */
export function isValidHeight(height: number): boolean {
  return typeof height === 'number' && height >= 50 && height <= 250;
}

/** 手机号校验规则 */
export function phoneRule(required = true): ValidateRule[] {
  const rules: ValidateRule[] = [];
  if (required) {
    rules.push({ required: true, message: '请输入手机号', trigger: 'blur' });
  }
  rules.push({
    message: '请输入正确的手机号',
    trigger: 'blur',
    pattern: PHONE_REG,
  });
  return rules;
}

/** 姓名校验规则 */
export function nameRule(required = true): ValidateRule[] {
  const rules: ValidateRule[] = [];
  if (required) {
    rules.push({ required: true, message: '请输入姓名', trigger: 'blur' });
  }
  rules.push({ min: 2, max: 20, message: '姓名长度为2-20个字符', trigger: 'blur' });
  return rules;
}

/** 年龄校验规则 */
export function ageRule(required = true): ValidateRule[] {
  const rules: ValidateRule[] = [];
  if (required) {
    rules.push({ required: true, message: '请输入年龄', trigger: 'blur' });
  }
  rules.push({
    message: '年龄范围为1-120岁',
    trigger: 'blur',
    validator: (_rule: any, value: any) => isValidAge(Number(value)),
  });
  return rules;
}

/** 身高校验规则 */
export function heightRule(required = true): ValidateRule[] {
  const rules: ValidateRule[] = [];
  if (required) {
    rules.push({ required: true, message: '请输入身高', trigger: 'blur' });
  }
  rules.push({
    message: '身高范围为50-250cm',
    trigger: 'blur',
    validator: (_rule: any, value: any) => isValidHeight(Number(value)),
  });
  return rules;
}

/** 通用必填规则 */
export function requiredRule(message: string): ValidateRule[] {
  return [{ required: true, message, trigger: 'blur' }];
}

/** 视频链接校验规则 */
export function videoUrlRule(): ValidateRule[] {
  return [
    {
      message: '请输入有效的视频链接',
      trigger: 'blur',
      pattern: /^https?:\/\/.+/,
    },
  ];
}
```

## 9. 用户状态 Store 实现

### stores/user.ts

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { UserInfo } from '@/types/user';
import { UserRole } from '@/types/user';
import {
  getToken,
  setToken,
  removeToken,
  getUserInfo as getStoredUser,
  setUserInfo as storeUser,
  removeUserInfo,
} from '@/utils/auth';
import { loginByPhone as apiLogin } from '@/api/auth';

export const useUserStore = defineStore('user', () => {
  // --- State ---
  const userInfo = ref<UserInfo | null>(null);
  const token = ref<string | null>(null);

  // --- Getters ---
  const isLoggedIn = computed(() => !!token.value);
  const isActor = computed(() => userInfo.value?.role === UserRole.Actor);
  const isCrew = computed(() => userInfo.value?.role === UserRole.Crew);
  const userId = computed(() => userInfo.value?.id ?? null);

  // --- Actions ---

  /** 从 storage 恢复状态（App 启动时调用） */
  function initFromStorage(): void {
    token.value = getToken();
    userInfo.value = getStoredUser();
  }

  /** 设置用户数据并持久化 */
  function setUserData(user: UserInfo, newToken: string): void {
    userInfo.value = user;
    token.value = newToken;
    setToken(newToken);
    storeUser(user);
  }

  /** 手机号验证码登录 */
  async function login(phone: string, code: string): Promise<UserInfo> {
    const result = await apiLogin(phone, code);
    setUserData(result.user, result.token);
    return result.user;
  }

  /** 登出 */
  function logout(): void {
    userInfo.value = null;
    token.value = null;
    removeToken();
    removeUserInfo();
    uni.reLaunch({ url: '/pages/login/index' });
  }

  /** 更新部分用户信息 */
  function updateProfile(profile: Partial<UserInfo>): void {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...profile };
      storeUser(userInfo.value);
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    isActor,
    isCrew,
    userId,
    initFromStorage,
    setUserData,
    login,
    logout,
    updateProfile,
  };
});
```

**使用示例**:

```typescript
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// App.vue onLaunch 中恢复状态
userStore.initFromStorage();

// 登录
await userStore.login('13812345678', '1234');

// 判断角色
if (userStore.isActor) {
  // 演员逻辑
}

// 登出
userStore.logout();
```

## 10. API 模块实现

### api/auth.ts

```typescript
import { get, post, put } from '@/utils/request';
import type { UserInfo, LoginResult } from '@/types/user';

/** 发送短信验证码 */
export function sendSmsCode(phone: string): Promise<void> {
  return post('/api/auth/sms-code', { phone });
}

/** 手机号验证码登录 */
export function loginByPhone(phone: string, code: string): Promise<LoginResult> {
  return post<LoginResult>('/api/auth/login', { phone, code });
}

/** 微信登录 */
export function loginByWechat(code: string): Promise<LoginResult> {
  return post<LoginResult>('/api/auth/wechat-login', { code });
}

/** 获取当前用户信息 */
export function getUserInfo(): Promise<UserInfo> {
  return get<UserInfo>('/api/auth/user-info');
}

/** 更新用户角色 */
export function updateUserRole(role: 1 | 2): Promise<void> {
  return put('/api/auth/role', { role });
}
```

### api/actor.ts

```typescript
import { get, put } from '@/utils/request';
import type { PageResult } from '@/types/common';
import type { ActorProfile, ActorSearchParams } from '@/types/actor';

/** 获取演员资料 */
export function getActorProfile(userId: number): Promise<ActorProfile> {
  return get<ActorProfile>(`/api/actor/profile/${userId}`);
}

/** 更新演员资料 */
export function updateActorProfile(data: Partial<ActorProfile>): Promise<void> {
  return put('/api/actor/profile', data);
}

/** 搜索演员列表 */
export function searchActors(params: ActorSearchParams): Promise<PageResult<ActorProfile>> {
  return get<PageResult<ActorProfile>>('/api/actor/search', params as Record<string, any>);
}

/** 获取演员详情 */
export function getActorDetail(userId: number): Promise<ActorProfile> {
  return get<ActorProfile>(`/api/actor/${userId}`);
}
```

### api/company.ts

```typescript
import { get, put } from '@/utils/request';
import type { Company } from '@/types/company';

/** 获取公司信息 */
export function getCompanyInfo(userId: number): Promise<Company> {
  return get<Company>(`/api/company/${userId}`);
}

/** 更新公司信息 */
export function updateCompanyInfo(data: Partial<Company>): Promise<void> {
  return put('/api/company', data);
}

/** 获取当前用户的公司信息 */
export function getMyCompany(): Promise<Company> {
  return get<Company>('/api/company/mine');
}
```

### api/project.ts

```typescript
import { get, post, put, del } from '@/utils/request';
import type { PageParams, PageResult } from '@/types/common';
import type { Project, ProjectSearchParams } from '@/types/project';

/** 创建项目 */
export function createProject(data: Omit<Project, 'id'>): Promise<Project> {
  return post<Project>('/api/project', data as Record<string, any>);
}

/** 更新项目 */
export function updateProject(id: number, data: Partial<Project>): Promise<void> {
  return put(`/api/project/${id}`, data as Record<string, any>);
}

/** 删除项目 */
export function deleteProject(id: number): Promise<void> {
  return del(`/api/project/${id}`);
}

/** 获取项目详情 */
export function getProject(id: number): Promise<Project> {
  return get<Project>(`/api/project/${id}`);
}

/** 搜索项目列表 */
export function getProjectList(params: ProjectSearchParams): Promise<PageResult<Project>> {
  return get<PageResult<Project>>('/api/project/list', params as Record<string, any>);
}

/** 获取我的项目列表 */
export function getMyProjects(params: PageParams): Promise<PageResult<Project>> {
  return get<PageResult<Project>>('/api/project/mine', params as Record<string, any>);
}
```

### api/role.ts

```typescript
import { get, post, put, del } from '@/utils/request';
import type { PageParams, PageResult } from '@/types/common';
import type { Role, RoleSearchParams } from '@/types/role';

/** 创建角色 */
export function createRole(data: Omit<Role, 'id'>): Promise<Role> {
  return post<Role>('/api/role', data as Record<string, any>);
}

/** 更新角色 */
export function updateRole(id: number, data: Partial<Role>): Promise<void> {
  return put(`/api/role/${id}`, data as Record<string, any>);
}

/** 删除角色 */
export function deleteRole(id: number): Promise<void> {
  return del(`/api/role/${id}`);
}

/** 获取角色详情 */
export function getRole(id: number): Promise<Role> {
  return get<Role>(`/api/role/${id}`);
}

/** 获取项目下的角色列表 */
export function getRolesByProject(
  projectId: number,
  params?: PageParams,
): Promise<PageResult<Role>> {
  return get<PageResult<Role>>(
    `/api/role/project/${projectId}`,
    params as Record<string, any>,
  );
}

/** 搜索角色列表 */
export function searchRoles(params: RoleSearchParams): Promise<PageResult<Role>> {
  return get<PageResult<Role>>('/api/role/search', params as Record<string, any>);
}
```

### api/apply.ts

```typescript
import { get, post, put, del } from '@/utils/request';
import type { PageResult } from '@/types/common';
import type { Apply, ApplySearchParams } from '@/types/apply';

/** 提交投递 */
export function submitApply(roleId: number, remark?: string): Promise<Apply> {
  return post<Apply>('/api/apply', { roleId, remark });
}

/** 取消投递 */
export function cancelApply(applyId: number): Promise<void> {
  return del(`/api/apply/${applyId}`);
}

/** 获取我的投递列表 */
export function getMyApplies(params: ApplySearchParams): Promise<PageResult<Apply>> {
  return get<PageResult<Apply>>('/api/apply/mine', params as Record<string, any>);
}

/** 获取角色下的投递列表（剧组端） */
export function getAppliesByRole(
  roleId: number,
  params: ApplySearchParams,
): Promise<PageResult<Apply>> {
  return get<PageResult<Apply>>(
    `/api/apply/role/${roleId}`,
    params as Record<string, any>,
  );
}

/** 通过投递 */
export function approveApply(applyId: number): Promise<void> {
  return put(`/api/apply/${applyId}/approve`);
}

/** 拒绝投递 */
export function rejectApply(applyId: number, remark?: string): Promise<void> {
  return put(`/api/apply/${applyId}/reject`, { remark });
}

/** 获取投递详情 */
export function getApplyDetail(applyId: number): Promise<Apply> {
  return get<Apply>(`/api/apply/${applyId}`);
}
```

## 11. 测试策略

### 单元测试

使用 Vitest 对纯函数进行单元测试，覆盖以下模块：

- **utils/format.ts**: 测试所有格式化函数的输入输出，包括边界值和异常输入
- **utils/validate.ts**: 测试所有校验函数和规则生成器，覆盖合法值、非法值、边界值
- **utils/auth.ts**: Mock `uni.getStorageSync` / `uni.setStorageSync`，测试 Token 和用户信息的存取

```typescript
// 示例：utils/format.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate, formatPhone, formatFileSize, formatGender, formatProjectStatus, formatApplyStatus, formatAge, formatFee } from '@/utils/format';

describe('formatDate', () => {
  it('should format ISO date string', () => {
    expect(formatDate('2024-01-15T10:30:00')).toBe('2024-01-15 10:30');
  });
  it('should return empty string for invalid date', () => {
    expect(formatDate('invalid')).toBe('');
  });
});

describe('formatPhone', () => {
  it('should mask middle digits', () => {
    expect(formatPhone('13812345678')).toBe('138****5678');
  });
});

describe('formatFileSize', () => {
  it('should format 100MB', () => {
    expect(formatFileSize(104857600)).toBe('100MB');
  });
});

describe('formatGender', () => {
  it('should return 男 for male', () => {
    expect(formatGender('male')).toBe('男');
  });
});

describe('formatProjectStatus', () => {
  it('should return 进行中 for status 1', () => {
    expect(formatProjectStatus(1)).toBe('进行中');
  });
});

describe('formatApplyStatus', () => {
  it('should return 已通过 for status 2', () => {
    expect(formatApplyStatus(2)).toBe('已通过');
  });
});

describe('formatAge', () => {
  it('should format age range', () => {
    expect(formatAge(18, 25)).toBe('18-25岁');
  });
});

describe('formatFee', () => {
  it('should format fee with ¥ prefix', () => {
    expect(formatFee('500')).toBe('¥500');
  });
  it('should return 面议 for empty fee', () => {
    expect(formatFee('')).toBe('面议');
  });
});
```

### API 模块测试

Mock `utils/request.ts` 的 `get` / `post` / `put` / `del` 方法，验证各 API 函数调用了正确的 URL、HTTP 方法和参数。

```typescript
// 示例：api/auth.test.ts
import { describe, it, expect, vi } from 'vitest';
import { sendSmsCode, loginByPhone } from '@/api/auth';
import * as request from '@/utils/request';

vi.mock('@/utils/request');

describe('sendSmsCode', () => {
  it('should call POST /api/auth/sms-code', async () => {
    const postSpy = vi.spyOn(request, 'post').mockResolvedValue(undefined);
    await sendSmsCode('13812345678');
    expect(postSpy).toHaveBeenCalledWith('/api/auth/sms-code', { phone: '13812345678' });
  });
});

describe('loginByPhone', () => {
  it('should call POST /api/auth/login and return result', async () => {
    const mockResult = { token: 'abc', user: { id: 1, phone: '13812345678', role: 1, status: 1 } };
    vi.spyOn(request, 'post').mockResolvedValue(mockResult);
    const result = await loginByPhone('13812345678', '1234');
    expect(result).toEqual(mockResult);
  });
});
```

### Store 测试

使用 `@pinia/testing` 的 `createTestingPinia` 测试 Store 的 state、getters 和 actions。

### 集成测试要点

- 请求拦截器正确注入 Token
- 401 响应触发登出和页面跳转
- 文件上传大小校验拦截超限文件
- Loading 计数器在并发请求时正确管理显示/隐藏
