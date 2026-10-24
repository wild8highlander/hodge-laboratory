import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Relative base so the built bundle works from any subpath —
// including docs/theorems-vitrine/ on the existing GitHub Pages.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 4500,
    rollupOptions: {
      output: {
        manualChunks: {
          plotly: ['plotly.js-dist-min'],
          d3: ['d3'],
          katex: ['katex'],
          react: ['react', 'react-dom'],
        },
      },
    },
  },
});
