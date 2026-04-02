import 'vue-router';

declare module 'vue-router' {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    pageCode?: string;
    pagePermission?: string;
    pagePermissionFallbacks?: string[];
    sectionKey?: string;
    sectionTitle?: string;
    sectionIcon?: string;
    sectionOrder?: number;
    itemTitle?: string;
    itemOrder?: number;
    hiddenInMenu?: boolean;
    placeholder?: boolean;
  }
}

export {};
