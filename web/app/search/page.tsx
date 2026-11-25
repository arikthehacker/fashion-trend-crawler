// Search: every signal and every headline behind it.

import SearchClient from "./SearchClient";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/search", "Search", "Search every signal in the ARI3LLA INDEX and every dated headline behind it, by word, outlet or signal name.");

export default function Search() {
  return (
    <main id="main-content">
      <Folio h1 left="Search" right="Signals and every headline behind them" />
      <SearchClient />
    </main>
  );
}
