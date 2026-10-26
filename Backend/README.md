# Stock API

A Flask API for the React frontend. All backend integration points live in
`app.py`: implement `get_stock_price`, `get_market_sentiment`, and
`get_ai_projection` as your data sources become available. Each receives an
uppercase ticker. The starter functions return `None`; no sample prices or AI
predictions are generated.

## Run locally

From the repository root (Python 3.10 or newer):

```sh
cd Backend
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The API runs at `http://127.0.0.1:5000`. For development with automatic reload:

```sh
python -m flask --app app run --debug
```

## Endpoints

- `GET /api/health` returns `{"status": "ok"}`. This checks the API process only.
- `GET /api/stocks/AAPL` returns the stock analysis below. Tickers are trimmed
  and uppercased; letters, numbers, dots, and hyphens are supported, up to 20
  characters, beginning with a letter or number (for example `BRK.B`).

Initial response, before connecting your backend functions:

```json
{
  "ticker": "AAPL",
  "stock_price": null,
  "market_sentiment": null,
  "ai_projection": null,
  "errors": {}
}
```

`stock_price` must be a finite, nonnegative Python number. Return prices in the
stock's quote currency. `market_sentiment` and `ai_projection` must be strings.
Use `None` for missing data. If you later need currency, timestamps, confidence,
or structured forecasts, add explicitly named response fields and keep these
existing fields consistent for frontend callers.

Provider exceptions and invalid return types leave that field `null` and add a
generic message under `errors[field_name]`; successful fields are preserved.
Provider failures are logged on the server. Responses use HTTP 200 for complete,
pending, and partially available results, 400 for invalid tickers, and 502 if all
three providers fail. Unknown routes and unsupported methods return JSON errors
with the appropriate HTTP status.

Keep future credentials in environment variables. Set timeouts on any outgoing
HTTP or AI requests inside your provider functions.

## Call from React

```ts
type StockAnalysis = {
  ticker: string;
  stock_price: number | null;
  market_sentiment: string | null;
  ai_projection: string | null;
  errors: Partial<Record<"stock_price" | "market_sentiment" | "ai_projection", string>>;
};

const response = await fetch(
  `http://127.0.0.1:5000/api/stocks/${encodeURIComponent(ticker)}`,
);
if (!response.ok) throw new Error(`Stock request failed (${response.status})`);
const analysis: StockAnalysis = await response.json();
// Use analysis.stock_price ?? "Not available yet" (and likewise for other fields).
```

Browser requests from `http://localhost:5173` and `http://127.0.0.1:5173` are
allowed by default. Set `ALLOWED_ORIGINS` to a comma-separated list to change
this. Set `PORT` to change the port used by `python app.py`. Export variables in
your shell before starting the server; `app.py` does not load `.env` files.

For deployment, use a WSGI server pointed at `app:app` or `app:create_app()`.

## Check the API

From `Backend`, with the virtual environment active:

```sh
python -m unittest discover -s tests -v
```

Tests replace provider functions locally and do not require live data or keys.
