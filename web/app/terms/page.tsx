import ProsePage from "../components/ProsePage";
import { pageMetadata } from "../../lib/site";
import { CONTACT_EMAIL, ISSUES_URL } from "../../lib/nav";

export const metadata = pageMetadata(
  "/terms",
  "Terms of Use",
  "Terms for using ARI3LLA INDEX: content licensing, linked sources, no warranty, and corrections.",
);

export default function Terms() {
  return (
    <ProsePage
      title="Terms of Use"
      updated="2026-09-22"
      sections={[
        { title: "What this site is", body: [
          "ARI3LLA INDEX is an independent, non-commercial research archive of style language. It is provided for information and historical reference. Nothing on it is fashion, purchasing, investment or business advice.",
        ]},
        { title: "Licensing", body: [
          <>The index&apos;s own material (its classifications, report text and structured data) is licensed under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener noreferrer">Creative Commons Attribution 4.0</a>. It may be reused with credit to &ldquo;ARI3LLA INDEX&rdquo; and a link to the page used.</>,
          "Articles, images and other material that reports link to belong to their publishers and are not covered by that license. The index links to sources; it does not republish them.",
          "The site's source code is published in its public repository under that repository's terms.",
        ]},
        { title: "Accuracy and corrections", body: [
          <>Reports state their confidence and cite a dated source for each claim, but may still contain errors. Published reports are corrected with a dated note rather than silently edited. Suspected errors can be reported by email to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> or as a <a href={ISSUES_URL} rel="noopener noreferrer">GitHub issue</a>.</>,
        ]},
        { title: "External links", body: [
          "Linked sites are outside the index's control. A link is a citation, not an endorsement.",
        ]},
        { title: "No warranty", body: [
          "The site is provided as is, without warranties of any kind. To the extent the law allows, ARI3LLA INDEX is not liable for any loss arising from use of the site or reliance on its content.",
        ]},
        { title: "Changes", body: [
          "These terms may be updated; the date above shows the latest version.",
        ]},
      ]}
    />
  );
}
