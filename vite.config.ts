import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
const researchOrigin=process.env.RESEARCH_API_ORIGIN || `http://127.0.0.1:${process.env.RESEARCH_PORT || '8091'}`;
const researchProxy={target:researchOrigin,changeOrigin:true};
const adminOrigin=process.env.ADMIN_API_ORIGIN || `http://127.0.0.1:${process.env.ADMIN_PORT || '4188'}`;
export default defineConfig({plugins:[react()],worker:{format:'es'},build:{chunkSizeWarningLimit:900},server:{port:4173,strictPort:true,proxy:{'/api/map-places':{target:process.env.MAP_API_ORIGIN||'https://satellite-app-production.up.railway.app',changeOrigin:true},'/api/reports':`http://127.0.0.1:${process.env.REPORT_PORT || '4187'}`,'/api/admin':adminOrigin,'/api/curation':adminOrigin,'/api/blog':adminOrigin,'/api/status':researchProxy,'/api/search':researchProxy,'/api/documents':researchProxy,'/api/chat':researchProxy}}});
