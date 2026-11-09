export const FEATURED_STOCKS = [
  { ticker: "AAPL", name: "Apple Inc." },
  { ticker: "MSFT", name: "Microsoft Corporation" },
  { ticker: "NVDA", name: "NVIDIA Corporation" },
  { ticker: "GOOGL", name: "Alphabet Inc." },
];

export const STOCKS = [
  ...FEATURED_STOCKS,
  { ticker: "AMZN", name: "Amazon.com, Inc." },
];

const STORAGE_KEY = "watchlist";

export function getWatchlist(): string[] {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]") } catch { return []; }}

export function saveWatchlist(tickers: string[]){
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickers));
}
