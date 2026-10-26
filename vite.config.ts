import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],worker:{format:'es'},build:{chunkSizeWarningLimit:900},server:{port:4173,strictPort:true,proxy:{'/api/reports':`http://127.0.0.1:${process.env.REPORT_PORT || '4187'}`}}});
