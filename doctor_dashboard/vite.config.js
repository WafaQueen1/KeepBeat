import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin.html'),
        ai_diagnostics: resolve(__dirname, 'ai-diagnostics.html'),
        correlations: resolve(__dirname, 'correlations.html'),
        login: resolve(__dirname, 'login.html'),
        patients: resolve(__dirname, 'patients.html'),
        register: resolve(__dirname, 'register.html'),
        settings: resolve(__dirname, 'settings.html'),
        stitch_signin: resolve(__dirname, 'stitch-signin.html'),
      },
    },
  },
});
