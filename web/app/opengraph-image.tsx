import { shareCard, OG_SIZE } from "../lib/og";

// Default share card for every page without its own. Built at export time.
export const dynamic = "force-static";
export const alt = "ARI3LLA INDEX: a weekly, source-linked record of style language";
export const size = OG_SIZE;
export const contentType = "image/png";

export default async function OpengraphImage() {
  return shareCard({
    kicker: "A weekly, source-linked record of style language",
    title: "What fashion coverage is naming each week, where, and from which kinds of outlets",
    foot: "EVERY CLAIM LINKED TO ITS SOURCE",
  });
}
