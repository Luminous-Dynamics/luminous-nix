import { defineConfig } from 'vite'
import { resolve } from 'path'
import react from '@vitejs/plugin-react'

// Custom plugin to handle /demo route
const demoRoutePlugin = () => {
  return {
    name: 'demo-route',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url === '/demo') {
          req.url = '/demo.html';
        }
        next();
      });
    }
  };
};

export default defineConfig({
  plugins: [react(), demoRoutePlugin()],
  // Base configuration for Tauri
  base: './',
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@nlp': resolve(__dirname, './implementations/web-based/js/nlp')
    }
  },

  // Server configuration for development
  server: {
    port: 5173,
    strictPort: false,
    open: false,
    watch: {
      ignored: ['**/src-tauri/**']
    }
  },

  // Build configuration
  build: {
    target: 'esnext',
    minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_DEBUG,
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        demo: resolve(__dirname, 'demo.html')
      }
    }
  },

  // Clear screen on dev start
  clearScreen: false,
  
  // Prevent Vite from obscuring Rust errors
  envPrefix: ['VITE_', 'TAURI_']
})