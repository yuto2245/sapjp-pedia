import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ArticleView from '@/views/ArticleView.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView,
    },
    {
        path: '/articles/:id',
        name: 'article',
        component: ArticleView,
    },
    {
        path: '/articles/:id/history',
        name: 'history',
        component: () => import('@/views/HistoryView.vue'),
    },
    {
        path: '/articles/:id/propose',
        name: 'propose',
        component: () => import('@/views/RevisionView.vue'),
    },
    {
        path: '/editor',
        name: 'editor',
        component: () => import('@/views/EditorView.vue'),
    },
    {
        path: '/admin',
        name: 'admin',
        component: () => import('@/views/AdminDashboardView.vue'),
    },
    {
        path: '/developer/api',
        name: 'developer-api',
        component: () => import('@/views/DeveloperApiView.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
