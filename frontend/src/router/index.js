import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
const routes = [
  { path: '/', name: 'Home', component: Home, meta: { title: '工作台' } },
  { path: '/diagnose', name: 'Diagnose', component: () => import('../views/Diagnose.vue'), meta: { title: 'AI识别' } },
  { path: '/consult', name: 'Consult', component: () => import('../views/Consult.vue'), meta: { title: '对话问诊' } },
  { path: '/map', name: 'MapView', component: () => import('../views/MapView.vue'), meta: { title: '病情地图' } },
  { path: '/knowledge', name: 'Knowledge', component: () => import('../views/Knowledge.vue'), meta: { title: '知识图谱' } },
]
export default createRouter({ history: createWebHistory(), routes })