import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],build:{
  lib:{entry:'src/streamlit_entry.tsx',formats:['es'],fileName:()=>'factory_command.js'},
  cssCodeSplit:false,assetsInlineLimit:100000,
  rollupOptions:{output:{inlineDynamicImports:true}},
  outDir:'dist-component'
}});
