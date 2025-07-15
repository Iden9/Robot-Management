import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getDefaultHomePath, hasPathPermission } from '@/utils/menu'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      redirect: () => {
        return getDefaultHomePath()
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login/index.vue'),
      meta: {
        requiresAuth: false,
        title: '用户登录'
      }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register/index.vue'),
      meta: {
        requiresAuth: false,
        title: '用户注册'
      }
    },
    {
      path: '/dashboard',
      name: 'SystemDashboard',
      component: () => import('../views/SystemDashboard/index.vue'),
      meta: {
        requiresAuth: true,
        title: '系统仪表板',
        roles: ['admin', 'operator']
      }
    },
    {
      path: '/education',
      name: 'EducationTraining',
      component: () => import('../views/EducationTraining/index.vue'),
      meta: {
        requiresAuth: true,
        title: '教育培训',
        roles: ['admin', 'operator', 'viewer']
      }
    },
    {
      path: '/navigation',
      name: 'SelfGuidedNavigation',
      component: () => import('../views/SelfGuidedNavigation/index.vue'),
      meta: {
        requiresAuth: true,
        title: '自主导览',
        roles: ['admin', 'operator', 'viewer']
      }
    },
    {
      path: '/equipment',
      name: 'EquipmentManagement',
      component: () => import('../views/EquipmentManagement/index.vue'),
      meta: {
        requiresAuth: true,
        title: '设备管理',
        roles: ['admin', 'operator']
      }
    },
    {
      path: '/robot-control',
      name: 'RobotControl',
      component: () => import('../views/RobotControl/index.vue'),
      meta: {
        requiresAuth: true,
        title: '机器人控制',
        roles: ['admin', 'operator', 'viewer']
      }
    },
    {
      path: '/account',
      name: 'AccountManagement',
      component: () => import('../views/AccountManagement/index.vue'),
      meta: {
        requiresAuth: true,
        title: '账户管理',
        roles: ['admin']
      }
    },
    {
      path: '/system',
      name: 'SystemSettings',
      component: () => import('../views/SystemSettings/index.vue'),
      meta: {
        requiresAuth: true,
        title: '系统设置',
        roles: ['admin']
      }
    },
    {
      path: '/roles',
      name: 'RoleManagement',
      component: () => import('../views/RoleManagement/index.vue'),
      meta: {
        requiresAuth: true,
        title: '角色管理',
        roles: ['admin']
      }
    },
    {
      path: '/knowledge',
      name: 'KnowledgeManagement',
      component: () => import('../views/KnowledgeManagement/index.vue'),
      meta: {
        requiresAuth: true,
        title: '知识库管理',
        roles: ['admin', 'operator', 'viewer']
      }
    },
    {
      path: '/prompt',
      name: 'PromptManagement',
      component: () => import('../views/PromptManagement/index.vue'),
      meta: {
        requiresAuth: true,
        title: '提示词管理',
        roles: ['admin', 'operator', 'viewer']
      }
    },
    {
      path: '/403',
      name: 'Forbidden',
      component: () => import('../views/Error/403.vue'),
      meta: {
        requiresAuth: false,
        title: '权限不足'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      redirect: '/'
    }
  ],
})

// 全局前置守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 宇树G1 EDU`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 检查用户是否已登录
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页面
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 检查用户权限 - 优先使用基于权限的检查
    if (!hasPathPermission(to.path)) {
      // 没有权限，跳转到403页面
      next({ name: 'Forbidden' })
      return
    }
  } else {
    // 不需要认证的页面（如登录页、注册页）
    if (authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      // 已登录用户访问登录页或注册页，跳转到仪表板
      next({ name: 'SystemDashboard' })
      return
    }
  }
  
  next()
})

// 全局后置守卫
router.afterEach((to, from) => {
  // 这里可以添加一些后置处理，比如埋点统计
  console.log(`路由跳转: ${from.path} -> ${to.path}`)
})

export default router
