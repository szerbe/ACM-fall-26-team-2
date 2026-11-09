import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { getWatchlist, saveWatchlist, STOCKS } from "../utils/Watchlist";
import { fetchStockAnalysis, isValidTicker, normalizeTicker } from "../utils/stockApi";
import type { StockAnalysisData } from "../utils/stockApi";

type AnalysisRequest =
  | { status: "loading" }
  | { status: "loaded"; data: StockAnalysisData }
  | { status: "failed"; message: string };

const priceFormat = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 6,
});

const metrics = [
  { field: "stock_price", label: "Stock price", empty: "Price unavailable." },
  { field: "market_sentiment", label: "Market sentiment", empty: "Sentiment unavailable." },
  { field: "ai_projection", label: "AI projection", empty: "No projection available yet." },
] as const;

function StockDetails({ ticker }: { ticker: string }) {
  const [pinned, setPinned] = useState(() => getWatchlist().includes(ticker));
  const [attempt, setAttempt] = useState(0);
  const [request, setRequest] = useState<AnalysisRequest>({ status: "loading" });
  const company = STOCKS.find((stock) => stock.ticker === ticker)?.name;

  useEffect(() => {
    const controller = new AbortController();
    fetchStockAnalysis(ticker, controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) setRequest({ status: "loaded", data });
      },
      (error: Error) => {
        if (!controller.signal.aborted) setRequest({ status: "failed", message: error.message });
      },
    );
    return () => controller.abort();
  }, [ticker, attempt]);

  function retry() {
    setRequest({ status: "loading" });
    setAttempt((previous) => previous + 1);
  }

  function togglePin() {
    const current = getWatchlist();
    const updated = current.includes(ticker)
      ? current.filter((item) => item !== ticker)
      : [...current, ticker];

    saveWatchlist(updated);
    setPinned(updated.includes(ticker));
  }

  return (
    <>
      <div className="detail-heading">
        <div className="page-heading">
          <h1>{ticker} analysis</h1>
          {company && <p>{company}</p>}
        </div>
        <button className="button pin-button" type="button" aria-pressed={pinned} onClick={togglePin}>
          <span aria-hidden="true">{pinned ? "★" : "☆"}</span>
          Pin stock
        </button>
      </div>

      {request.status === "failed" ? (
        <div className="empty-state">
          <p role="alert">{request.message}</p>
          <button className="button" onClick={retry}>Try again</button>
        </div>
      ) : (
        <>
          <dl className="metric-grid" aria-busy={request.status === "loading"}>
            {metrics.map(({ field, label, empty }) => {
              const data = request.status === "loaded" ? request.data : null;
              const value = data?.[field];
              const error = data?.errors[field];

              return (
                <div className="metric" key={field}>
                  <dt>{label}</dt>
                  <dd className={value == null ? "metric-placeholder" : `metric-value metric-${field}`}>
                    {typeof value === "number"
                      ? priceFormat.format(value)
                      : value ?? (data ? error ?? empty : "Loading…")}
                  </dd>
                </div>
              );
            })}
          </dl>
          {request.status === "loaded" && Object.keys(request.data.errors).length > 0 && (
            <button className="button retry-button" onClick={retry}>Retry stock data</button>
          )}
        </>
      )}
    </>
  );
}

function StockAnalysis() {
  const { ticker = "" } = useParams();
  const symbol = normalizeTicker(ticker);

  return (
    <main className="page">
      <Link className="back-link" to="/"><span aria-hidden="true">←</span> Home</Link>
      {isValidTicker(symbol) ? (
        <StockDetails key={symbol} ticker={symbol} />
      ) : (
        <div className="page-heading">
          <h1>Invalid stock ticker</h1>
          <p>Return home to look up a stock.</p>
        </div>
      )}
    </main>
  );
}

export default StockAnalysis;
