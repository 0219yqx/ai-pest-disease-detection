<template>
  <div class="app-shell">
    <div class="field" aria-hidden="true">
      <video
        v-show="playField"
        class="field-media"
        autoplay
        muted
        loop
        playsinline
        poster="/field/poster.jpg"
      >
        <source src="/field/wheat.webm" type="video/webm" />
        <source src="/field/wheat.mp4" type="video/mp4" />
      </video>
      <img v-show="!playField" class="field-media" src="/field/poster.jpg" alt="" />
      <div class="field-shade"></div>
    </div>

    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">田</span>
        <div>
          <div class="brand-name">田安智识</div>
          <div class="brand-sub">稼护慧眼</div>
        </div>
      </div>

      <p class="who">
        <strong>张工</strong>
        <span>河南省农技推广站</span>
      </p>

      <nav class="side-nav">
        <router-link v-for="item in nav" :key="item.path" :to="item.path" class="side-link" active-class="is-on">
          <span class="nav-icon" v-html="item.icon"></span>
          <span>{{ item.label }}</span>
          <span v-if="item.badge" class="side-num">{{ item.badge }}</span>
        </router-link>
      </nav>

      <div class="side-foot">
        <time>{{ clock }}</time>
        <span>{{ dateStr }}</span>
      </div>
    </aside>

    <div class="workspace">
      <header class="mobile-bar">
        <span class="brand-name">田安智识</span>
        <time>{{ clock }}</time>
      </header>
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <nav class="dock" aria-label="主导航">
      <router-link v-for="item in dock" :key="item.path" :to="item.path" class="dock-link" active-class="is-on">
        <span class="nav-icon" v-html="item.icon"></span>
        <span>{{ item.short }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const clock = ref('00:00:00')
const dateStr = ref('')
const playField = ref(false)
let timer = null

function tick() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  clock.value = `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
  const wk = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  dateStr.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${wk}`
}

const icon = {
  home: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 10.5 12 4l8 6.5V20H4z"/><path d="M9 20v-6h6v6"/></svg>',
  search: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="6"/><path d="m20 20-3.5-3.5"/></svg>',
  chat: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 6h14v9H8l-3 3z"/></svg>',
  map: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="m4 6 5-2 6 2 5-2v14l-5 2-6-2-5 2z"/><path d="M9 4v14M15 6v14"/></svg>',
  book: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 4h11v16H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M6 4v16"/></svg>',
}

const nav = [
  { path: '/', label: '工作台', icon: icon.home },
  { path: '/diagnose', label: '识别', badge: 'AI', icon: icon.search },
  { path: '/consult', label: '问诊', icon: icon.chat },
  { path: '/map', label: '病情地图', badge: '5', icon: icon.map },
  { path: '/knowledge', label: '知识', icon: icon.book },
]
const dock = [
  { path: '/', short: '工作台', icon: icon.home },
  { path: '/diagnose', short: '识别', icon: icon.search },
  { path: '/consult', short: '问诊', icon: icon.chat },
  { path: '/map', short: '地图', icon: icon.map },
  { path: '/knowledge', short: '知识', icon: icon.book },
]

onMounted(() => {
  tick()
  timer = setInterval(tick, 1000)
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const save = navigator.connection && navigator.connection.saveData
  playField.value = !reduce && !save
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.app-shell {
  position: relative;
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #1c140e;
  color: var(--ink);
}
.field {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.field-media {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 68%;
}
.field-shade {
  position: absolute;
  inset: 0;
  background: rgba(92, 64, 32, 0.18);
  pointer-events: none;
}

.sidebar {
  position: relative;
  z-index: 2;
  width: 212px;
  min-width: 212px;
  display: flex;
  flex-direction: column;
  background: rgba(36, 25, 16, 0.82);
  color: #F3EBDD;
  padding: 22px 16px 16px;
}
.brand { display: flex; gap: 10px; align-items: center; }
.brand-mark {
  width: 36px; height: 36px;
  display: grid; place-items: center;
  border: 1px solid rgba(243, 235, 221, 0.35);
  font-family: var(--serif);
  font-size: 18px;
}
.brand-name { font-family: var(--serif); font-size: 18px; letter-spacing: 0.04em; }
.brand-sub { font-size: 12px; color: #CDBFA8; margin-top: 2px; }
.who {
  margin: 22px 0 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(243, 235, 221, 0.16);
  display: flex; flex-direction: column; gap: 2px;
  font-size: 14px; color: #CDBFA8;
}
.who strong { color: #F3EBDD; font-weight: 500; }
.side-nav { display: flex; flex-direction: column; gap: 2px; }
.side-link {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 8px;
  color: #E7DCCB;
  text-decoration: none;
  font-size: 15px;
  border-left: 2px solid transparent;
}
.side-link:hover { color: #fff; }
.side-link.is-on {
  color: #F6E7C4;
  border-left-color: #C4A574;
  background: rgba(255, 255, 255, 0.04);
}
.nav-icon { width: 18px; height: 18px; display: flex; }
.nav-icon :deep(svg) { display: block; }
.side-num {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
  font-size: 12px;
  color: #C4A574;
}
.side-foot {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid rgba(243, 235, 221, 0.16);
  display: flex; flex-direction: column; gap: 2px;
  font-size: 12px; color: #CDBFA8;
}
.side-foot time { font-variant-numeric: tabular-nums; font-size: 16px; color: #F3EBDD; }

.workspace { position: relative; z-index: 1; flex: 1; min-width: 0; display: flex; flex-direction: column; }
.main-content { flex: 1; min-height: 0; overflow: auto; }
.mobile-bar, .dock { display: none; }

.page-enter-active { transition: opacity 180ms ease; }
.page-leave-active { transition: opacity 120ms ease; }
.page-enter-from, .page-leave-to { opacity: 0; }

@media (max-width: 767px) {
  .sidebar { display: none; }
  .mobile-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px 0;
    color: #F6F1E6;
  }
  .mobile-bar time { font-variant-numeric: tabular-nums; font-size: 14px; }
  .main-content { padding-bottom: 64px; }
  .dock {
    display: flex;
    position: fixed; z-index: 5;
    left: 0; right: 0; bottom: 0;
    height: 60px;
    background: rgba(36, 25, 16, 0.86);
    border-top: 1px solid rgba(243, 235, 221, 0.16);
  }
  .dock-link {
    flex: 1;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
    color: #CDBFA8; text-decoration: none; font-size: 12px;
  }
  .dock-link.is-on { color: #F6E7C4; }
}
</style>
