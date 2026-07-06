// scripts/copy-reports.mjs
// Copies data/reports/*.json into web/public/data/reports/ so the static
// export (output: "export" in next.config.ts) serves each raw report at a
// stable, predictable URL: /data/reports/<date>.json
//
// Runs automatically before `next build` via the "prebuild" npm lifecycle
// script (see package.json). This is the download route wired into the
// Dataset JSON-LD's distribution/contentUrl on app/reports/[date]/page.tsx
// (see docs/agent-logs/raw-json-download-route-run45.md).

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(__dirname, "..", "..", "data", "reports");
const destDir = path.join(__dirname, "..", "public", "data", "reports");

fs.mkdirSync(destDir, { recursive: true });

const files = fs.readdirSync(srcDir).filter((f) => f.endsWith(".json"));

for (const file of files) {
  fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
}

console.log(`copy-reports: copied ${files.length} report(s) into public/data/reports/`);
