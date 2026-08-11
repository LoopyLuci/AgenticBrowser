import { defineConfig } from "vite";
import { copyFileSync, cpSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

export default defineConfig({
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        sidepanel: join(__dirname, "src/entrypoints/sidepanel/index.tsx"),
        content: join(__dirname, "src/background/content.ts"),
        background: join(__dirname, "src/background/index.ts"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "[name].js",
        assetFileNames: "[name].[ext]",
      },
    },
  },
  plugins: [
    {
      name: "copy-assets",
      closeBundle() {
        const src = join(__dirname, "public");
        const dest = join(__dirname, "dist");
        if (!existsSync(dest)) mkdirSync(dest, { recursive: true });
        cpSync(src, dest, { recursive: true });
        ["manifest.json"].forEach((name) => {
          const s = join(__dirname, "public", name);
          const d = join(dest, name);
          if (existsSync(s)) copyFileSync(s, d);
        });
      },
    },
  ],
});
