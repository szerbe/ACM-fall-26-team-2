type StockField = "stock_price" | "market_sentiment" | "ai_projection";

export type StockAnalysisData = {
  ticker: string;
  stock_price: number | null;
  market_sentiment: string | null;
  ai_projection: string | null;
  errors: Partial<Record<StockField, string>>;
};

const apiBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");

export function normalizeTicker(ticker: string) {
  return ticker.trim().toUpperCase();
}

export function isValidTicker(ticker: string) {
  return /^[A-Z0-9][A-Z0-9.-]{0,19}$/.test(ticker);
}

export async function fetchStockAnalysis(
  ticker: string,
  signal: AbortSignal,
): Promise<StockAnalysisData> {
  const response = await fetch(`${apiBase}/api/stocks/${encodeURIComponent(ticker)}`, {
    headers: { Accept: "application/json" },
    signal,
  }).catch(() => null);
  const data = await response?.json().catch(() => null);

  // Flask returns the individual field errors even when all providers fail.
  if ((response?.ok || response?.status === 502) && data?.ticker === ticker && data.errors) {
    return data;
  }

  if (response?.status === 400 && typeof data?.error?.message === "string") {
    throw new Error(data.error.message);
  }

  throw new Error("Stock data is temporarily unavailable. Please try again.");
}
