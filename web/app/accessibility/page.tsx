import ProsePage from "../components/ProsePage";
import { pageMetadata } from "../../lib/site";
import { CONTACT_EMAIL, ISSUES_URL } from "../../lib/nav";

export const metadata = pageMetadata(
  "/accessibility",
  "Accessibility",
  "The accessibility standard ARI3LLA INDEX aims for, its known limitations, and how to report a barrier.",
);

export default function Accessibility() {
  return (
    <ProsePage
      title="Accessibility"
      updated="2026-11-24"
      sections={[
        { title: "Standard", body: [
          <>ARI3LLA INDEX aims to meet the <a href="https://www.w3.org/TR/WCAG22/" rel="noopener noreferrer">Web Content Accessibility Guidelines (WCAG) 2.2</a> at level AA.</>,
        ]},
        { title: "What is in place", body: [
          "Pages are set in near-black text on a paper-coloured background, in one serif for reading and one sans-serif for labels. Text contrast is at least 4.5:1. The photocopy texture is decorative and carries no content.",
          "Every page has a skip link to the main content and the same navigation, with the current page announced to screen readers. Keyboard focus is shown with a visible outline. Long source lists are folded into ordinary disclosure elements (HTML details), which open with a keyboard or a screen reader like any other control. Layouts reflow to a single column on small screens. Nothing autoplays or animates, and reports can be read and printed as plain text.",
          "Accessibility rules are checked automatically on every change to the site's code.",
        ]},
        { title: "Known limitations", body: [
          "Some small uppercase labels are harder to read than body text. Automated checks cannot catch every barrier, and the site has not yet been reviewed by an external auditor.",
        ]},
        { title: "Report a barrier", body: [
          <>If something on the site is hard or impossible to use, email <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> or open a <a href={ISSUES_URL} rel="noopener noreferrer">GitHub issue</a>, naming the page and what went wrong.</>,
        ]},
      ]}
    />
  );
}
