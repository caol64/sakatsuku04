import { defineConfig } from "vite";
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from "@sveltejs/kit/vite";

const host = "localhost";

// https://vitejs.dev/config/
export default defineConfig(async () => ({
    plugins: [tailwindcss(), sveltekit()],

    // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
    //
    // 1. prevent vite from obscuring rust errors
    clearScreen: false,
    // 2. tauri expects a fixed port, fail if that port is not available
    server: {
        port: 1420,
        strictPort: true,
        host: host || false,
        hmr: host
            ? {
                  protocol: "ws",
                  host,
                  port: 1421,
              }
            : undefined,
        watch: {
            // 3. tell vite to ignore watching
            // ignored: ["**/src/**"],
        },
    },
}));
