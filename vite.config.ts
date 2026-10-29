import {defineConfig, type ProxyOptions} from 'vite';
import react from '@vitejs/plugin-react';
const researchOrigin=process.env.RESEARCH_API_ORIGIN || `http://127.0.0.1:${process.env.RESEARCH_PORT || '8091'}`;
// The loopback dev server is an application proxy, like the deployed frontend.
// Only the explicitly configured hosted origin is forwarded; local API mode stays unchanged.
const researchProxy:ProxyOptions={target:researchOrigin,changeOrigin:true,configure(proxy){
  if(process.env.RESEARCH_BROWSER_ORIGIN)proxy.on('proxyReq',request=>request.setHeader('Origin',process.env.RESEARCH_BROWSER_ORIGIN!));
}};
const adminOrigin=process.env.ADMIN_API_ORIGIN || `http://127.0.0.1:${process.env.ADMIN_PORT || '4188'}`;
export default defineConfig({plugins:[react()],worker:{format:'es'},build:{chunkSizeWarningLimit:900},server:{port:4173,strictPort:true,proxy:{'/api/map-places':{target:process.env.MAP_API_ORIGIN||'https://satellite-app-production.up.railway.app',changeOrigin:true},'/api/reports':`http://127.0.0.1:${process.env.REPORT_PORT || '4187'}`,'/api/admin':adminOrigin,'/api/curation':adminOrigin,'/api/blog':adminOrigin,'/api/status':researchProxy,'/api/search':researchProxy,'/api/documents':researchProxy,'/api/chat':researchProxy}}});
