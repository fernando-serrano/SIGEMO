import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
    },
    {
      path: '/inicio',
      name: 'inicio',
      component: () => import('@/pages/DashboardPage.vue'),
    },
    {
      path: '/usuarios',
      name: 'usuarios',
      component: () => import('@/pages/UsersPage.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

export default router
