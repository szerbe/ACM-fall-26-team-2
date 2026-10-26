"""Stock API. Replace the three provider functions with your backend logic."""

import math
import os
import re

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException


def get_stock_price(ticker: str) -> float | None:
    """Return the latest price, or None when unavailable.

    Add your database or market-data call here. Convert provider-specific values
    (for example Decimal) to a Python float before returning them.
    """
    return None


def get_market_sentiment(ticker: str) -> str | None:
    """Return a sentiment string such as 'Bullish', or None when unavailable."""
    return None


def get_ai_projection(ticker: str) -> str | None:
    """Return your AI projection text, or None when unavailable."""
    return None


def create_app() -> Flask:
    """Create an application for local development, tests, or a WSGI server."""
    app = Flask(__name__)
    origins = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )
    CORS(
        app,
        resources={r"/api/*": {
            "origins": [origin.strip() for origin in origins.split(",") if origin.strip()],
            "methods": ["GET", "OPTIONS"],
        }},
    )

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/stocks/<ticker>")
    def stock_analysis(ticker: str):
        symbol = ticker.strip().upper()
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,19}", symbol):
            return jsonify(error={
                "code": "invalid_ticker",
                "message": "Use 1–20 letters, numbers, dots, or hyphens; start with a letter or number.",
            }), 400

        result = {"ticker": symbol, "errors": {}}
        providers = {
            "stock_price": get_stock_price,
            "market_sentiment": get_market_sentiment,
            "ai_projection": get_ai_projection,
        }
        for field, provider in providers.items():
            result[field] = None
            try:
                value = provider(symbol)
                if value is not None:
                    if field == "stock_price":
                        if (
                            isinstance(value, bool)
                            or not isinstance(value, (int, float))
                            or not math.isfinite(value)
                            or value < 0
                        ):
                            raise ValueError("Price must be a finite, nonnegative number")
                    elif not isinstance(value, str):
                        raise ValueError(f"{field} must be a string")
                result[field] = value
            except Exception:
                # Keep successful fields available; never expose provider secrets.
                app.logger.exception("Could not fetch %s for %s", field, symbol)
                result["errors"][field] = "Data is temporarily unavailable."

        # A null value without an error means the provider has no data yet.
        # If every provider fails, signal an upstream failure to API clients.
        status = 502 if len(result["errors"]) == len(providers) else 200
        return jsonify(result), status

    @app.errorhandler(HTTPException)
    def http_error(error: HTTPException):
        return jsonify(error={
            "code": error.name.lower().replace(" ", "_"),
            "message": error.description,
        }), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error: Exception):
        app.logger.exception("Unhandled API error")
        return jsonify(error={
            "code": "internal_error",
            "message": "An unexpected error occurred.",
        }), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")))
