import type { NextConfig } from "next";
import fs from "fs";
import path from "path";

// Copy data/reports/*.json into public/data/reports/ here (not just via the
// "prebuild" npm lifecycle script in package.json) because Next.js evaluates
// this config file on every build invocation, regardless of whether the
// build was launched via `npm run build` or a bare `next build` (run 46 —
// see docs/agent-logs/download-route-robustness-run46.md and
// scripts/copy-reports.mjs, which does the same copy for the npm lifecycle
// path; importing that ESM module directly here breaks Next's config
// bundling, so the logic is duplicated inline — keep both in sync).
(function copyReportsForConfig() {
  const srcDir = path.join(__dirname, "..", "data", "reports");
  const destDir = path.join(__dirname, "public", "data", "reports");
  fs.mkdirSync(destDir, { recursive: true });
  const files = fs.readdirSync(srcDir).filter((f) => f.endsWith(".json"));
  for (const file of files) {
    fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
  }
  console.log(`next.config.ts: copied ${files.length} report(s) into public/data/reports/`);
})();

const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
