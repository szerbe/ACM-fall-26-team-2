
import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { getWatchlist, saveWatchlist } from "../utils/Watchlist";

function StockAnalysis() {
  const { ticker = "" } = useParams();
  const navigate = useNavigate();
  const [pinned, setPinned] = useState(() =>
    getWatchlist().includes(ticker.toUpperCase())
  );

  function togglePin() {
    const current = getWatchlist();
    const symbol = ticker.toUpperCase();

    const updated = current.includes(symbol)
      ? current.filter((item) => item !== symbol)
      : [...current, symbol];

    saveWatchlist(updated);
    setPinned(updated.includes(symbol));
  }

  return (
    <main className="home">
      <button onClick={() => navigate("/")}>← Back to Home</button>

      <h1>{ticker.toUpperCase()} Analysis</h1>
      <p>Stock price: Sample data</p>
      <p>Market sentiment: Not available yet</p>
      <p>AI projection: Coming soon</p>

      <button onClick={togglePin}>
        {pinned ? "★ Unpin Stock" : "☆ Pin Stock"}
      </button>
    </main>
  );
}

export default StockAnalysis;
