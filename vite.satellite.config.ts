import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  // Select the standalone Google provider; build still uses production NODE_ENV.
  mode:'satellite',
  plugins:[react()], publicDir:false,
  build:{outDir:'dist-satellite',rollupOptions:{input:'satellite.html'}},
});
