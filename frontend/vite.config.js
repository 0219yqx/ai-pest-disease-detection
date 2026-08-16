import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端服务地址：默认 8000（与 backend/config.py 的 PORT 保持一致），可用环境变量覆盖
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', port: 5173,
    // 允许引用仓库根目录 models/class_names.json（单一类别映射源）
    fs: { allow: ['..'] },
    proxy: { '/api': { target: proxyTarget, changeOrigin: true } },
  },
})
