<template>
  <div class="app-layout">
    <aside class="sidebar">
      <!-- 顶部品牌 + 用户身份卡 -->
      <div class="sidebar-header">
        <div class="logo-area">
          <div class="logo-icon shine">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="13" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
              <path d="M14 5 C14 5, 8 10, 8 15 C8 18.5, 10.5 21, 14 21 C17.5 21, 20 18.5, 20 15 C20 10, 14 5, 14 5Z" fill="rgba(255,255,255,0.9)"/>
              <path d="M14 10 C14 10, 11 13, 11 15.5 C11 17.2, 12.3 18.5, 14 18.5 C15.7 18.5, 17 17.2, 17 15.5 C17 13, 14 10, 14 10Z" fill="#2e7d32"/>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-title">田安智识</span>
            <span class="logo-sub">稼护慧眼</span>
          </div>
        </div>
      </div>

      <!-- 用户身份卡（国赛级身份上下文） -->
      <div class="user-card">
        <div class="uc-avatar">植</div>
        <div class="uc-info">
          <div class="uc-name">植保员 · 张工</div>
          <div class="uc-role">
            <span class="uc-role-dot"></span>
            河南省农技推广站
          </div>
        </div>
      </div>

      <!-- 导航分组 1 -->
      <div class="nav-group-title">核心功能</div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItemsMain"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <!-- 导航分组 2 -->
      <div class="nav-group-title nav-group-title--2">数据决策</div>
      <nav class="sidebar-nav sidebar-nav--sub">
        <router-link
          v-for="item in navItemsData"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <!-- 底部：实时时钟 + 系统状态 -->
      <div class="sidebar-footer">
        <div class="sf-clock">
          <span class="sf-time">{{ clock }}</span>
          <span class="sf-date">{{ dateStr }}</span>
        </div>
        <div class="sf-row">
          <span class="sf-dot"></span>
          <span>系统运行中</span>
          <span class="sf-ver">v2.0 · 国赛版</span>
        </div>
      </div>
    </aside>
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const clock = ref('00:00:00')
const dateStr = ref('')
let timer = null

function tick() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  clock.value = `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
  const wk = ['周日','周一','周二','周三','周四','周五','周六'][d.getDay()]
  dateStr.value = `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${wk}`
}
onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onBeforeUnmount(() => { clearInterval(timer) })

const navItemsMain = [
  { path: '/',          label: '工作台',   icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>' },
  { path: '/diagnose',  label: 'AI识别',   badge: 'AI', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' },
  { path: '/consult',   label: '对话问诊', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' },
]
const navItemsData = [
  { path: '/map',       label: '病情地图', badge: '5', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>' },
  { path: '/knowledge', label: '知识图谱', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><line x1="9.5" y1="10" x2="6.5" y2="7.5"/><line x1="14.5" y1="10" x2="17.5" y2="7.5"/><line x1="9.5" y1="14" x2="6.5" y2="16.5"/><line x1="14.5" y1="14" x2="17.5" y2="16.5"/></svg>' },
]
</script>
<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* ---- 侧边栏 ---- */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: linear-gradient(180deg, #0c1a0c 0%, #132613 50%, #0f1f0f 100%);
  display: flex;
  flex-direction: column;
  color: #fff;
  user-select: none;
  position: relative;
  overflow: hidden;
}
.sidebar::before {
  content: '';
  position: absolute;
  top: -40%;
  left: -40%;
  width: 180%;
  height: 180%;
  background: radial-gradient(ellipse at 30% 20%, rgba(46,125,50,0.08) 0%, transparent 60%);
  pointer-events: none;
}

.sidebar-header {
  padding: 22px 18px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  position: relative;
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(46,125,50,0.2);
  border-radius: 10px;
  border: 1px solid rgba(76,175,80,0.15);
}
.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}
.logo-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 2px;
}
.logo-sub {
  font-size: 11px;
  opacity: 0.5;
  letter-spacing: 4px;
  margin-top: 1px;
}

/* ---- 用户身份卡 ---- */
.user-card {
  margin: 14px 12px 6px;
  padding: 11px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(46,125,50,0.18), rgba(46,125,50,0.06));
  border: 1px solid rgba(92,218,124,0.18);
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}
.user-card::before {
  content: ''; position: absolute; top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(92,218,124,0.12), transparent);
  animation: cardSheen 4s ease-in-out infinite;
}
@keyframes cardSheen {
  0%, 100% { left: -100%; }
  50%      { left: 150%; }
}
.uc-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, #5cda7c, #2e7d32);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 800; color: #fff;
  flex-shrink: 0; box-shadow: 0 2px 8px rgba(46,125,50,0.4);
}
.uc-info { flex: 1; min-width: 0; }
.uc-name {
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.92);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.uc-role {
  display: flex; align-items: center; gap: 4px;
  font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.uc-role-dot {
  width: 5px; height: 5px; border-radius: 50%; background: #5cda7c;
  flex-shrink: 0;
}

/* ---- 导航分组标题 ---- */
.nav-group-title {
  font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
  color: rgba(255,255,255,0.3);
  padding: 14px 22px 6px;
  text-transform: uppercase;
}
.nav-group-title--2 { padding-top: 8px; }

/* ---- 导航 ---- */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 0 10px;
  gap: 2px;
}
.sidebar-nav--sub { padding-top: 2px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  color: rgba(255,255,255,0.55);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  border-radius: 10px;
  transition: all 180ms ease;
  position: relative;
  overflow: hidden;
}
.nav-item::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(92,218,124,0.08), transparent);
  transform: translateX(-100%);
  transition: transform 500ms var(--ease-out);
}
.nav-item:hover::after { transform: translateX(100%); }
.nav-item:hover {
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.9);
  padding-left: 16px;
}
.nav-item--active {
  background: linear-gradient(135deg, rgba(46,125,50,0.2), rgba(46,125,50,0.1));
  color: #5cda7c;
  font-weight: 600;
  box-shadow: inset 0 0 0 1px rgba(76,175,80,0.12);
}
.nav-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  background: #5cda7c;
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 8px rgba(92,218,124,0.6);
  animation: navBarIn 320ms var(--ease-spring);
}
@keyframes navBarIn {
  from { height: 0; opacity: 0; }
  to   { height: 18px; opacity: 1; }
}
.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0.75;
}
.nav-item--active .nav-icon {
  opacity: 1;
}
.nav-label { font-size: 13px; }
.nav-badge {
  margin-left: auto;
  background: rgba(46,125,50,0.35);
  color: #5cda7c;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 999px;
}

/* ---- 底部 ---- */
.sidebar-footer {
  margin-top: auto;
  padding: 14px 18px;
  border-top: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sf-clock {
  display: flex; align-items: baseline; justify-content: space-between;
  padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.sf-time {
  font-size: 16px; font-weight: 700; color: rgba(255,255,255,0.92);
  font-variant-numeric: tabular-nums; letter-spacing: 1px;
}
.sf-date { font-size: 10px; color: rgba(255,255,255,0.4); }
.sf-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}
.sf-ver { margin-left: auto; font-size: 10px; opacity: 0.7; }
.sf-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #5cda7c;
  box-shadow: 0 0 6px rgba(92,218,124,0.7);
  animation: pulse-dot 2s infinite;
}

/* ---- 主内容 ---- */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-primary);
  width: 100%;
}

/* ---- 页面过渡 ---- */
.page-enter-active {
  animation: fadeIn 300ms var(--ease-out);
}
.page-leave-active {
  animation: fadeIn 200ms var(--ease-out) reverse;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
