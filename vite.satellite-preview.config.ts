import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// Isolated static preview: no main-site routing, API rewrites or public archives.
export default defineConfig({
  plugins:[react()], publicDir:false,
  build:{outDir:'.reports/satellite-preview-dist',emptyOutDir:true,
    rollupOptions:{input:'satellite-preview.html'}},
  server:{host:'127.0.0.1',port:4186,strictPort:true},
});
