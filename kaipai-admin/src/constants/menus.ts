import type { AdminMenuItem } from '@/types/admin'

export const adminMenus: AdminMenuItem[] = [
  {
    key: 'dashboard',
    label: '工作台',
    icon: 'DataBoard',
    route: '/dashboard/index',
    menuPermission: 'menu.dashboard',
    pagePermission: 'page.dashboard.index',
  },
  {
    key: 'verify',
    label: '实名认证',
    icon: 'CircleCheck',
    menuPermission: 'menu.verify',
    children: [
      {
        key: 'verify-pending',
        label: '待审核',
        icon: 'CircleCheck',
        route: '/verify/pending',
        pagePermission: 'page.verify.pending',
      },
      {
        key: 'verify-history',
        label: '审核历史',
        icon: 'Document',
        route: '/verify/history',
        pagePermission: 'page.verify.history',
      },
    ],
  },
  {
    key: 'referral',
    label: '邀请裂变',
    icon: 'Connection',
    menuPermission: 'menu.referral',
    children: [
      {
        key: 'referral-risk',
        label: '异常邀请',
        icon: 'Warning',
        route: '/referral/risk',
        pagePermission: 'page.referral.risk',
      },
    ],
  },
  {
    key: 'membership',
    label: '会员中心',
    icon: 'Medal',
    menuPermission: 'menu.membership',
    children: [
      {
        key: 'membership-products',
        label: '会员产品',
        icon: 'Box',
        route: '/membership/products',
        pagePermission: 'page.membership.products',
      },
      {
        key: 'membership-accounts',
        label: '会员账户',
        icon: 'UserFilled',
        route: '/membership/accounts',
        pagePermission: 'page.membership.accounts',
      },
    ],
  },
  {
    key: 'refund',
    label: '退款中心',
    icon: 'Wallet',
    menuPermission: 'menu.refund',
    children: [
      {
        key: 'refund-orders',
        label: '退款单',
        icon: 'Tickets',
        route: '/refund/orders',
        pagePermission: 'page.refund.orders',
      },
    ],
  },
  {
    key: 'content',
    label: '页面配置',
    icon: 'MagicStick',
    menuPermission: 'menu.content',
    children: [
      {
        key: 'content-templates',
        label: '场景模板',
        icon: 'Files',
        route: '/content/templates',
        pagePermission: 'page.content.templates',
      },
    ],
  },
  {
    key: 'system',
    label: '系统管理',
    icon: 'Setting',
    menuPermission: 'menu.system',
    children: [
      {
        key: 'system-admin-users',
        label: '后台账号',
        icon: 'Avatar',
        route: '/system/admin-users',
        pagePermission: 'page.system.admin-users',
      },
    ],
  },
]
