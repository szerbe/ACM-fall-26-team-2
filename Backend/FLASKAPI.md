# Stock API

A Flask API for the React frontend. All backend integration points live in
`flaskapi.py`: implement `get_stock_price`, `get_market_sentiment`, and
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
python flaskapi.py
```

The API runs at `http://127.0.0.1:5000`. For development with automatic reload:

```sh
python -m flask --app flaskapi run --debug
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

## Run the frontend

Leave Flask running. In a second terminal, open `Frontend` and run:

```sh
npm ci
npm run dev
```

Vite forwards `/api` requests to Flask on port 5000 during development and
preview. The stock analysis page reads all three fields, with separate messages
for missing data and provider errors. It displays prices in the quote currency
without a currency symbol because the API does not supply a currency code.

For deployment, use a WSGI server pointed at `flaskapi:app` or
`flaskapi:create_app()` and route `/api` to Flask on the frontend's origin. If
Flask uses a different origin or port, set `VITE_API_BASE_URL` to its origin
before starting or building the frontend and add the frontend's origin to the
comma-separated `ALLOWED_ORIGINS` on the Flask side. Set `PORT` to change
Flask's port. Export Flask variables in your shell before starting the server.

## Connect the neural network

The network on `will-branch-awesome` takes a financial sentence and returns a
numeric `predictedSentiment`. After bringing that code over, expose inference
with the trained model and its fitted vectorizer loaded once. The script
currently trains and runs a demo at import time, so keep that workflow behind a
main guard before importing model code from Flask.

In `get_market_sentiment(ticker)`, obtain financial text for the requested
ticker and run inference on it. Convert the resulting score or an aggregate of
scores to a display string such as `"Sentiment score +0.24"` and return it.
Return `None` if there is no relevant text. The analysis page displays the
string as soon as the provider returns it. Keep `get_ai_projection(ticker)`
for a separate forecasting provider that can supply a written projection.

## Check the API

From `Backend`, with the virtual environment active:

```sh
python -m unittest discover -s tests -v
```

Tests replace provider functions locally and do not require live data or keys.
