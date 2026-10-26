
import { useNavigate } from "react-router";
import { getWatchlist, saveWatchlist, STOCKS } from "../utils/Watchlist";
import { useState } from "react";

function Watchlist() {
  const navigate = useNavigate();
  const [pinned, setPinned] = useState(() => getWatchlist());

  function removeStock(ticker: string) {
    const updated = pinned.filter((item) => item !== ticker);
    saveWatchlist(updated);
    setPinned(updated);
  }

  const savedStocks = pinned.map((ticker) => ({
    ticker,
    name: STOCKS.find((stock) => stock.ticker === ticker)?.name ?? ticker,
  }));

  return (
    <main className="home">
      <h1>Pinned Stocks</h1>

      {savedStocks.length === 0 ? (
        <p>You haven't pinned any stocks yet.</p>
      ) : (
        <div className="stock-grid">
          {savedStocks.map((stock) => (
            <div className="stock-card" key={stock.ticker}>
              <h3>{stock.ticker}</h3>
              <p>{stock.name}</p>

              <button onClick={() => navigate(`/stock/${stock.ticker}`)}>
                View Analysis
              </button>

              <button onClick={() => removeStock(stock.ticker)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default Watchlist;
