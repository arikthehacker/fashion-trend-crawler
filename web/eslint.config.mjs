import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // eslint-config-next already registers eslint-plugin-jsx-a11y and enables
  // a small subset of its rules (alt-text, aria-*). Add more of the plugin's
  // recommended rules on top — including its only heading-related rule.
  // Note: no jsx-a11y rule can detect a styled <p> masquerading visually as
  // a heading — see docs/agent-logs/heading-lint-automation.md for why, and
  // what to do about it instead.
  {
    rules: {
      // Only checks that <hN> elements aren't empty — does not (cannot)
      // check that non-<hN> elements aren't styled to look like headings.
      "jsx-a11y/heading-has-content": "error",
      "jsx-a11y/anchor-has-content": "error",
      "jsx-a11y/anchor-is-valid": "warn",
      "jsx-a11y/img-redundant-alt": "warn",
      "jsx-a11y/no-redundant-roles": "warn",
      "jsx-a11y/label-has-associated-control": "warn",
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
