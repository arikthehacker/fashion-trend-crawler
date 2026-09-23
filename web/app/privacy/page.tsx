import ProsePage from "../components/ProsePage";
import { pageMetadata } from "../../lib/site";
import { CONTACT_EMAIL, ISSUES_URL } from "../../lib/nav";

export const metadata = pageMetadata(
  "/privacy",
  "Privacy",
  "What ARI3LLA INDEX collects about visitors: aggregate, cookieless page analytics and nothing else.",
);

export default function Privacy() {
  return (
    <ProsePage
      title="Privacy"
      updated="2026-09-22"
      sections={[
        { title: "Summary", body: [
          "ARI3LLA INDEX has no accounts, no sign-up forms, no comments, no advertising and no tracking cookies. It collects aggregate page-view statistics and nothing else.",
        ]},
        { title: "Analytics", body: [
          <>The site uses <a href="https://vercel.com/docs/analytics/privacy-policy" rel="noopener noreferrer">Vercel Web Analytics</a> to count page views. It sets no cookies and does not identify individual visitors. It records the page, the referring site, and approximate country, browser, operating system and device type, in aggregate.</>,
          "This data is used only to understand which pages are read. It is not sold, shared for advertising, or combined with other data.",
        ]},
        { title: "Hosting logs", body: [
          <>The site is hosted by Vercel, which processes technical request data (such as IP addresses) to deliver and secure the site, as described in <a href="https://vercel.com/legal/privacy-policy" rel="noopener noreferrer">Vercel&apos;s privacy policy</a>. ARI3LLA INDEX does not access or keep those logs.</>,
        ]},
        { title: "Email and GitHub", body: [
          <>If you email <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>, your address and message are used only to reply. Reports filed as <a href={ISSUES_URL} rel="noopener noreferrer">GitHub issues</a> are public and governed by GitHub&apos;s terms.</>,
        ]},
        { title: "Your rights", body: [
          <>Because no personal profile is kept, there is usually nothing to access or delete. Questions or requests can be sent to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</>,
          "This page will be updated, with a new date, if any of the above changes.",
        ]},
      ]}
    />
  );
}
