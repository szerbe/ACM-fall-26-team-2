import { useState } from "react";
import { Link } from "react-router";
import Stockcard from "../components/Stockcard";
import { getWatchlist, saveWatchlist, STOCKS } from "../utils/Watchlist";

function Watchlist() {
  const [pinned, setPinned] = useState(() => getWatchlist());

  function removeStock(ticker: string) {
    const updated = pinned.filter((item) => item !== ticker);
    saveWatchlist(updated);
    setPinned(updated);
  }

  return (
    <main className="page">
      <div className="page-heading">
        <h1>Saved stocks</h1>
        <p>Revisit the stocks you’ve pinned.</p>
      </div>

      {pinned.length === 0 ? (
        <div className="empty-state">
          <p>You haven’t pinned any stocks yet.</p>
          <Link className="button button-primary" to="/">Explore stocks</Link>
        </div>
      ) : (
        <ul className="stock-list">
          {pinned.map((ticker) => (
            <Stockcard
              key={ticker}
              ticker={ticker}
              name={STOCKS.find((stock) => stock.ticker === ticker)?.name}
              onRemove={() => removeStock(ticker)}
            />
          ))}
        </ul>
      )}
    </main>
  );
}

export default Watchlist;
