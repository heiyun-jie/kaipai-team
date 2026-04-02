export interface AdminSessionInfo {
  adminUserId: number
  account: string
  userName: string
  phone?: string
  email?: string
  roleCodes: string[]
  menuPermissions: string[]
  pagePermissions: string[]
  actionPermissions: string[]
}

export interface AdminLoginResponse {
  accessToken: string
  adminUserInfo: AdminSessionInfo
}

export interface AdminMenuItem {
  key: string
  label: string
  icon: string
  route?: string
  menuPermission?: string
  pagePermission?: string
  pagePermissionFallbacks?: string[]
  children?: AdminMenuItem[]
}
