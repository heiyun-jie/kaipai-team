export interface AdminLoginPayload {
  account: string;
  password: string;
}

export interface AdminSessionInfo {
  adminUserId: number;
  account: string;
  userName: string;
  phone?: string;
  email?: string;
  roleCodes: string[];
  menuPermissions: string[];
  pagePermissions: string[];
  actionPermissions: string[];
}

export interface AdminLoginResult {
  accessToken: string;
  adminUserInfo: AdminSessionInfo;
}
