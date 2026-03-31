import { adminMenus } from '@/constants/menus'

export type PermissionCategory = 'menu' | 'page' | 'action'
export type PermissionModuleKey =
  | 'dashboard'
  | 'verify'
  | 'referral'
  | 'membership'
  | 'payment'
  | 'refund'
  | 'content'
  | 'system'

export interface PermissionMeta {
  code: string
  label: string
  category: PermissionCategory
  moduleKey: PermissionModuleKey
}

export interface PermissionTreeNode {
  key: string
  label: string
  children?: PermissionTreeNode[]
  disabled?: boolean
  permissionCode?: string
}

const MODULE_LABELS: Record<PermissionModuleKey, string> = {
  dashboard: '工作台',
  verify: '实名认证',
  referral: '邀请裂变',
  membership: '会员中心',
  payment: '订单中心',
  refund: '退款中心',
  content: '页面配置',
  system: '系统管理',
}

const PAGE_LABELS: Record<string, string> = {
  'page.dashboard.index': '工作台概览',
  'page.verify.pending': '实名认证待审核',
  'page.verify.history': '实名认证历史',
  'page.verify.detail': '实名认证详情',
  'page.referral.risk': '异常邀请',
  'page.referral.eligibility': '邀请资格',
  'page.membership.products': '会员产品',
  'page.membership.accounts': '会员账户',
  'page.payment.orders': '支付订单',
  'page.payment.transactions': '支付流水',
  'page.refund.orders': '退款单',
  'page.refund.logs': '退款日志',
  'page.content.templates': '场景模板',
  'page.system.admin-users': '后台账号',
  'page.system.roles': '角色管理',
  'page.system.operation-logs': '操作日志',
}

const ACTION_META: PermissionMeta[] = [
  { code: 'action.verify.approve', label: '实名认证审核通过', category: 'action', moduleKey: 'verify' },
  { code: 'action.verify.reject', label: '实名认证审核拒绝', category: 'action', moduleKey: 'verify' },
  { code: 'action.referral.risk.approve', label: '异常邀请通过', category: 'action', moduleKey: 'referral' },
  { code: 'action.referral.risk.invalidate', label: '异常邀请作废', category: 'action', moduleKey: 'referral' },
  { code: 'action.referral.risk.resolve', label: '异常邀请复核完成', category: 'action', moduleKey: 'referral' },
  { code: 'action.referral.eligibility.grant', label: '邀请资格发放', category: 'action', moduleKey: 'referral' },
  { code: 'action.referral.eligibility.revoke', label: '邀请资格撤销', category: 'action', moduleKey: 'referral' },
  { code: 'action.referral.eligibility.extend', label: '邀请资格延长', category: 'action', moduleKey: 'referral' },
  { code: 'action.membership.product.create', label: '新建会员产品', category: 'action', moduleKey: 'membership' },
  { code: 'action.membership.account.open', label: '手工开通会员', category: 'action', moduleKey: 'membership' },
  { code: 'action.membership.account.extend', label: '手工延期会员', category: 'action', moduleKey: 'membership' },
  { code: 'action.membership.account.close', label: '关闭会员', category: 'action', moduleKey: 'membership' },
  { code: 'action.refund.approve', label: '退款审核通过', category: 'action', moduleKey: 'refund' },
  { code: 'action.refund.reject', label: '退款审核拒绝', category: 'action', moduleKey: 'refund' },
  { code: 'action.content.template.create', label: '新建场景模板', category: 'action', moduleKey: 'content' },
  { code: 'action.content.template.edit', label: '编辑场景模板', category: 'action', moduleKey: 'content' },
  { code: 'action.content.template.publish', label: '发布模板', category: 'action', moduleKey: 'content' },
  { code: 'action.content.template.rollback', label: '回滚模板', category: 'action', moduleKey: 'content' },
  { code: 'action.system.admin-user.create', label: '新建后台账号', category: 'action', moduleKey: 'system' },
  { code: 'action.system.admin-user.edit', label: '编辑后台账号', category: 'action', moduleKey: 'system' },
  { code: 'action.system.admin-user.enable', label: '启用后台账号', category: 'action', moduleKey: 'system' },
  { code: 'action.system.admin-user.disable', label: '禁用后台账号', category: 'action', moduleKey: 'system' },
  { code: 'action.system.admin-user.reset-password', label: '重置后台账号密码', category: 'action', moduleKey: 'system' },
  { code: 'action.system.admin-user.bind-roles', label: '后台账号绑定角色', category: 'action', moduleKey: 'system' },
  { code: 'action.system.role.create', label: '新建角色', category: 'action', moduleKey: 'system' },
  { code: 'action.system.role.edit', label: '编辑角色', category: 'action', moduleKey: 'system' },
  { code: 'action.system.role.enable', label: '启用角色', category: 'action', moduleKey: 'system' },
  { code: 'action.system.role.disable', label: '禁用角色', category: 'action', moduleKey: 'system' },
  { code: 'action.system.role.copy', label: '复制角色', category: 'action', moduleKey: 'system' },
]

const CATEGORY_LABELS: Record<PermissionCategory, string> = {
  menu: '菜单权限',
  page: '页面权限',
  action: '操作权限',
}

const moduleOrder = adminMenus.map((item) => item.key as PermissionModuleKey)

const menuRegistry: PermissionMeta[] = adminMenus
  .filter((item) => item.menuPermission)
  .map((item) => ({
    code: item.menuPermission as string,
    label: `${item.label}菜单`,
    category: 'menu' as const,
    moduleKey: item.key as PermissionModuleKey,
  }))

const pageRegistryFromMenus: PermissionMeta[] = adminMenus.flatMap((item) => {
  const moduleKey = item.key as PermissionModuleKey
  const directPages = item.pagePermission
    ? [
        {
          code: item.pagePermission,
          label: PAGE_LABELS[item.pagePermission] || item.label,
          category: 'page' as const,
          moduleKey,
        },
      ]
    : []
  const childPages = (item.children || [])
    .filter((child) => child.pagePermission)
    .map((child) => ({
      code: child.pagePermission as string,
      label: PAGE_LABELS[child.pagePermission as string] || child.label,
      category: 'page' as const,
      moduleKey,
    }))

  return [...directPages, ...childPages]
})

const extraPageRegistry: PermissionMeta[] = Object.entries(PAGE_LABELS)
  .filter(([code]) => !pageRegistryFromMenus.some((item) => item.code === code))
  .map(([code, label]) => ({
    code,
    label,
    category: 'page' as const,
    moduleKey: inferModuleKey(code, 'page'),
  }))

export const permissionRegistry: PermissionMeta[] = [...menuRegistry, ...pageRegistryFromMenus, ...extraPageRegistry, ...ACTION_META]

export const permissionMetaMap = Object.fromEntries(permissionRegistry.map((item) => [item.code, item])) as Record<string, PermissionMeta>

export const permissionTreeData: PermissionTreeNode[] = moduleOrder.map((moduleKey) => {
  const moduleItems = permissionRegistry.filter((item) => item.moduleKey === moduleKey)
  const children = (['menu', 'page', 'action'] as PermissionCategory[])
    .map((category) => {
      const categoryItems = moduleItems.filter((item) => item.category === category)
      if (!categoryItems.length) {
        return null
      }

      return {
        key: `group:${moduleKey}:${category}`,
        label: CATEGORY_LABELS[category],
        children: categoryItems.map((item) => ({
          key: item.code,
          label: item.label,
          permissionCode: item.code,
        })),
      } satisfies PermissionTreeNode
    })
    .filter(Boolean) as PermissionTreeNode[]

  return {
    key: `module:${moduleKey}`,
    label: MODULE_LABELS[moduleKey],
    children,
  }
})

export function mergePermissionCodes(selection: {
  menuPermissions?: string[]
  pagePermissions?: string[]
  actionPermissions?: string[]
}) {
  return [...(selection.menuPermissions || []), ...(selection.pagePermissions || []), ...(selection.actionPermissions || [])]
}

export function splitPermissionCodes(codes: string[]) {
  const uniqueCodes = Array.from(new Set(codes))
  return {
    menuPermissions: uniqueCodes.filter((code) => code.startsWith('menu.')),
    pagePermissions: uniqueCodes.filter((code) => code.startsWith('page.')),
    actionPermissions: uniqueCodes.filter((code) => code.startsWith('action.')),
  }
}

export function getPermissionLabel(code: string) {
  return permissionMetaMap[code]?.label || `未登记权限 ${code}`
}

export function getPermissionDisplayText(code: string) {
  return `${getPermissionLabel(code)} · ${code}`
}

export function getUnknownPermissionCodes(codes: string[]) {
  return Array.from(new Set(codes.filter((code) => !permissionMetaMap[code])))
}

function inferModuleKey(code: string, category: PermissionCategory): PermissionModuleKey {
  const segments = code.split('.')
  const moduleToken = segments[1]

  if (moduleToken && moduleToken in MODULE_LABELS) {
    return moduleToken as PermissionModuleKey
  }

  if (category === 'action' && segments[2] && segments[2] in MODULE_LABELS) {
    return segments[2] as PermissionModuleKey
  }

  return 'system'
}
