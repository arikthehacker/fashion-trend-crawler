import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { TIMELINE } from "../../../lib/ari3_cards";
import { Stamp } from "../../components/Chrome";
import { Ari3Page, day } from "../ui";

export const metadata = pageMetadata(
  "/ari3/timeline",
  "ARI3 research timeline",
  "How ARI3 developed, from the first crawl to pre-registered experiments. Dates are real. Planned steps carry no date."
);

export default function Timeline() {
  return (
    <Ari3Page label="Timeline" current="/ari3/timeline">
      <ol className="chron">
        {TIMELINE.map((x, i) => (
          <li key={i}>
            <span className="d">{x.planned ? <Stamp>Planned</Stamp> : day(x.date)}</span>
            <div>
              <b>{x.href ? <Link href={x.href}>{x.title}</Link> : x.title}</b>
              <p>{x.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </Ari3Page>
  );
}
