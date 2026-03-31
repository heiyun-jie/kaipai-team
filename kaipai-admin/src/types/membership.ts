import type { PageResult } from './common';

export interface MembershipProduct {
  productId: number;
  productCode: string;
  productName: string;
  membershipTier: number;
  durationDays: number;
  listPrice: string;
  salePrice: string;
  status: number;
  benefitConfigJson?: string;
  sortNo: number;
  createTime?: string;
  updateTime?: string;
}

export interface MembershipProductQuery {
  pageNo: number;
  pageSize: number;
  membershipTier?: number;
  status?: number;
}

export interface MembershipProductCreatePayload {
  productCode: string;
  productName: string;
  membershipTier: number;
  durationDays: number;
  listPrice: number;
  salePrice: number;
  benefitConfigJson?: string;
  sortNo: number;
}

export interface MembershipAccount {
  membershipId: number;
  userId: number;
  tier: number;
  status: number;
  effectiveTime: string;
  expireTime: string;
  sourceType: string;
  sourceRefId?: number;
}

export interface MembershipAccountQuery {
  pageNo: number;
  pageSize: number;
  userId?: number;
  tier?: number;
  status?: number;
}

export interface MembershipAccountOpenPayload {
  tier: number;
  effectiveTime: string;
  expireTime: string;
  sourceType: string;
  sourceRefId?: number;
  remark?: string;
}

export interface MembershipAccountExtendPayload {
  expireTime: string;
  remark?: string;
}

export interface MembershipAccountClosePayload {
  remark?: string;
}

export type MembershipProductPageResult = PageResult<MembershipProduct>;
export type MembershipAccountPageResult = PageResult<MembershipAccount>;

