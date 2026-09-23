// scripts/copy-reports.mjs
// Copies data/reports/*.json into web/public/data/reports/ so the static
// export (output: "export" in next.config.ts) serves each raw report at a
// stable, predictable URL: /data/reports/<date>.json
//
// IMPORTANT (run 46): this used to run only via the "prebuild" npm lifecycle
// script, which meant a bare `npx next build` (skipping npm's lifecycle
// hooks) silently produced a build missing the JSON files. As of run 46,
// `copyReports()` is also invoked directly at the top of `next.config.ts`,
// which Next.js evaluates every time it reads config -- i.e. on ANY build
// invocation (`next build`, `npm run build`, `npm ci && next build`, etc.),
// not just the npm-lifecycle path. The "prebuild" script in package.json is
// left in place as a harmless, redundant belt-and-suspenders copy (copying
// again is a no-op cost, not a correctness risk).
//
// This is the download route wired into the Dataset JSON-LD's
// distribution/contentUrl on app/reports/[date]/page.tsx (see
// docs/agent-logs/raw-json-download-route-run45.md).

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function copyReports() {
  const srcDir = path.join(__dirname, "..", "..", "data", "reports");
  const destDir = path.join(__dirname, "..", "public", "data", "reports");

  fs.mkdirSync(destDir, { recursive: true });

  // Clear old copies first, so a report removed from data/reports/ (e.g. the
  // simulated archive withdrawn on 2026-09-22) can't linger as a public download.
  for (const stale of fs.readdirSync(destDir).filter((f) => f.endsWith(".json"))) {
    fs.rmSync(path.join(destDir, stale));
  }

  const files = fs.existsSync(srcDir) ? fs.readdirSync(srcDir).filter((f) => f.endsWith(".json")) : [];

  for (const file of files) {
    fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
  }

  console.log(`copy-reports: copied ${files.length} report(s) into public/data/reports/`);
  return files.length;
}

// Only run automatically when executed directly as a script (e.g. via the
// "prebuild" npm lifecycle script), not when imported by next.config.ts.
const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url));
if (isMain) {
  copyReports();
}
