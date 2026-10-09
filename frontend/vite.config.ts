import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backendPort = process.env.BACKEND_PORT ?? "8000";

export default defineConfig({
  plugins: [react()],
  server: {
    // Same-origin WebSocket in development: the browser talks to Vite, Vite forwards to FastAPI.
    proxy: {
      "/ws": { target: `ws://localhost:${backendPort}`, ws: true },
    },
  },
});
