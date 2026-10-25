export const STOCKS = [
  { ticker: "AAPL", name: "Apple Inc." },
  { ticker: "GOOGL", name: "Alphabet Inc." },  
  { ticker: "MSFT", name: "Microsoft Corporation" },
{ ticker: "AMZN", name: "Amazon.com, Inc." },]

const STORAGE_KEY = "watchlist";

export function getWatchlist(): string[] {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]") } catch { return []; }}

export function saveWatchlist(tickers: string[]){
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickers));
}