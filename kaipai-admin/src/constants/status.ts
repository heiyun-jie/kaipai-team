export const verifyStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '未提交', tone: 'info' },
  1: { label: '待审核', tone: 'warning' },
  2: { label: '已通过', tone: 'success' },
  3: { label: '已拒绝', tone: 'danger' },
}

export const membershipStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '未开通', tone: 'info' },
  1: { label: '生效中', tone: 'success' },
  2: { label: '已过期', tone: 'warning' },
  3: { label: '已关闭', tone: 'danger' },
}

export const templateStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '草稿', tone: 'info' },
  1: { label: '已发布', tone: 'success' },
  2: { label: '已停用', tone: 'danger' },
}

export const referralStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '待生效', tone: 'info' },
  1: { label: '有效', tone: 'success' },
  2: { label: '已作废', tone: 'danger' },
  3: { label: '复核中', tone: 'warning' },
}

export const referralRiskFlagMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '无风险', tone: 'success' },
  1: { label: '命中风险', tone: 'warning' },
}

export const entitlementStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  1: { label: '生效中', tone: 'success' },
  2: { label: '已过期', tone: 'warning' },
  3: { label: '已撤销', tone: 'danger' },
}

export const dashboardBizLineMap: Record<string, string> = {
  verify: '实名认证',
  referral: '邀请裂变',
  refund: '退款',
  payment: '支付',
}

export const adminUserStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  1: { label: '启用中', tone: 'success' },
  2: { label: '已禁用', tone: 'danger' },
}

export const refundAuditStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '待审核', tone: 'warning' },
  1: { label: '已通过', tone: 'success' },
  2: { label: '已拒绝', tone: 'danger' },
}

export const refundStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '待处理', tone: 'info' },
  1: { label: '退款中', tone: 'warning' },
  2: { label: '退款成功', tone: 'success' },
  3: { label: '已关闭', tone: 'danger' },
}

export const adminRoleStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  1: { label: '启用中', tone: 'success' },
  2: { label: '已禁用', tone: 'danger' },
}

export const paymentOrderStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '待支付', tone: 'warning' },
  1: { label: '已支付', tone: 'success' },
  2: { label: '已关闭', tone: 'danger' },
}

export const paymentTransactionStatusMap: Record<number, { label: string; tone: 'info' | 'warning' | 'success' | 'danger' }> = {
  0: { label: '待回调', tone: 'warning' },
  1: { label: '成功', tone: 'success' },
  2: { label: '失败', tone: 'danger' },
}

export const membershipTierOptions = [
  { label: '基础会员', value: 1 },
  { label: '进阶会员', value: 2 },
  { label: '旗舰会员', value: 3 },
]
