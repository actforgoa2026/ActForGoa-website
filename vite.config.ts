import {defineConfig, type ProxyOptions} from 'vite';
import react from '@vitejs/plugin-react';
import {serveMapConfig} from './server/map-config';
const researchOrigin=process.env.RESEARCH_API_ORIGIN || `http://127.0.0.1:${process.env.RESEARCH_PORT || '8091'}`;
// The loopback dev server is an application proxy, like the deployed frontend.
// Only the explicitly configured hosted origin is forwarded; local API mode stays unchanged.
const researchProxy:ProxyOptions={target:researchOrigin,changeOrigin:true,configure(proxy){
  if(process.env.RESEARCH_BROWSER_ORIGIN)proxy.on('proxyReq',request=>request.setHeader('Origin',process.env.RESEARCH_BROWSER_ORIGIN!));
}};
const adminOrigin=process.env.VITE_LOCAL_AGENT==='1'?researchOrigin:process.env.ADMIN_API_ORIGIN || `http://127.0.0.1:${process.env.ADMIN_PORT || '4188'}`;
export default defineConfig({cacheDir:'.reports/vite-cache',plugins:[react(),{name:'public-google-map-config',configureServer(server){server.middlewares.use('/api/map-config',(req,res)=>serveMapConfig(req,res));}}],worker:{format:'es'},build:{chunkSizeWarningLimit:900},server:{port:4173,strictPort:true,proxy:{'/api/dev':researchProxy,'/api/map-places':{target:process.env.MAP_API_ORIGIN||'https://satellite-app-production.up.railway.app',changeOrigin:true},'/api/reports':`http://127.0.0.1:${process.env.REPORT_PORT || '4187'}`,'/api/satellite':process.env.SATELLITE_WEB_ORIGIN || adminOrigin,'/api/admin':adminOrigin,'/api/curation':adminOrigin,'/api/blog':adminOrigin,'/api/status':researchProxy,'/api/search':researchProxy,'/api/documents':researchProxy,'/api/chat':researchProxy}}});
