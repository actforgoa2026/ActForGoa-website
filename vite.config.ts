import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
const researchOrigin=process.env.RESEARCH_API_ORIGIN || `http://127.0.0.1:${process.env.RESEARCH_PORT || '8091'}`;
const researchProxy={target:researchOrigin,changeOrigin:true};
const adminOrigin=process.env.VITE_LOCAL_AGENT==='1'?researchOrigin:process.env.ADMIN_API_ORIGIN || `http://127.0.0.1:${process.env.ADMIN_PORT || '4188'}`;
const reportOrigin=process.env.VITE_LOCAL_AGENT==='1'?researchOrigin:`http://127.0.0.1:${process.env.REPORT_PORT || '4187'}`;
export default defineConfig({cacheDir:'.reports/vite-cache',plugins:[react()],worker:{format:'es'},build:{chunkSizeWarningLimit:900},server:{hmr:process.env.DEV_RELAY_MODE==='1'?false:undefined,port:4173,strictPort:true,proxy:{'/api/dev':researchProxy,'/api/reports':reportOrigin,'/api/admin':adminOrigin,'/api/curation':adminOrigin,'/api/blog':adminOrigin,'/api/status':researchProxy,'/api/search':researchProxy,'/api/documents':researchProxy,'/api/chat':researchProxy}}});
