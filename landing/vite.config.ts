import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({root:import.meta.dirname,base:'/landing/',plugins:[react()],build:{outDir:'../dist/landing',emptyOutDir:true,chunkSizeWarningLimit:650}});
