import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // NOTE: "output: export" was tried alongside the Pagefind integration but broke
  // the build — sitemap.ts/robots.ts need explicit `dynamic = "force-static"` to be
  // export-compatible (see docs/agent-logs/pagefind-integration.md). Left as default
  // (server output) until that's fixed; Pagefind's postbuild step against `out/`
  // won't run correctly until static export is actually restored.
};

export default nextConfig;
