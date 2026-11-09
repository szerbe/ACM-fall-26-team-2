"""Check the API contract independently of future data providers."""

import unittest
from unittest.mock import patch

from flaskapi import create_app


class StockAPITests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_unconnected_providers_are_null(self):
        response = self.client.get("/api/stocks/aapl")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "ticker": "AAPL", "stock_price": None,
            "market_sentiment": None, "ai_projection": None, "errors": {},
        })

    def test_connected_providers_receive_normalized_ticker(self):
        with patch("flaskapi.get_stock_price", return_value=123.45) as price, \
             patch("flaskapi.get_market_sentiment", return_value="Bullish") as sentiment, \
             patch("flaskapi.get_ai_projection", return_value="Potential growth.") as projection:
            response = self.client.get("/api/stocks/%20brk.b%20")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "ticker": "BRK.B", "stock_price": 123.45,
            "market_sentiment": "Bullish", "ai_projection": "Potential growth.",
            "errors": {},
        })
        for provider in (price, sentiment, projection):
            provider.assert_called_once_with("BRK.B")

    def test_invalid_tickers_do_not_call_providers(self):
        with patch("flaskapi.get_stock_price") as price:
            for ticker in ("bad!", "-AAPL", "A" * 21, "%20"):
                with self.subTest(ticker=ticker):
                    response = self.client.get(f"/api/stocks/{ticker}")
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json["error"]["code"], "invalid_ticker")
        price.assert_not_called()

    def test_provider_failure_preserves_other_fields_and_hides_details(self):
        with patch("flaskapi.get_stock_price", side_effect=RuntimeError("secret-token")), \
             patch("flaskapi.get_market_sentiment", return_value="Neutral"), \
             self.assertLogs(self.app.logger, level="ERROR"):
            response = self.client.get("/api/stocks/AAPL")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json["stock_price"])
        self.assertEqual(response.json["market_sentiment"], "Neutral")
        self.assertIn("stock_price", response.json["errors"])
        self.assertNotIn("secret-token", response.get_data(as_text=True))

    def test_all_provider_failures_return_502(self):
        with patch("flaskapi.get_stock_price", side_effect=RuntimeError()), \
             patch("flaskapi.get_market_sentiment", side_effect=RuntimeError()), \
             patch("flaskapi.get_ai_projection", side_effect=RuntimeError()), \
             self.assertLogs(self.app.logger, level="ERROR"):
            response = self.client.get("/api/stocks/AAPL")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(len(response.json["errors"]), 3)

    def test_invalid_provider_values_become_errors(self):
        for value in (float("nan"), float("inf"), -1, True, "123.45"):
            with self.subTest(value=value), \
                 patch("flaskapi.get_stock_price", return_value=value), \
                 patch("flaskapi.get_market_sentiment", return_value={"label": "Bullish"}), \
                 patch("flaskapi.get_ai_projection", return_value=["Growth"]), \
                 self.assertLogs(self.app.logger, level="ERROR"):
                response = self.client.get("/api/stocks/AAPL")
                self.assertEqual(response.status_code, 502)
                self.assertIsNone(response.json["stock_price"])
                self.assertEqual(len(response.json["errors"]), 3)

    def test_http_errors_are_json(self):
        self.assertEqual(self.client.get("/missing").json["error"]["code"], "not_found")
        response = self.client.post("/api/stocks/AAPL")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json["error"]["code"], "method_not_allowed")

    def test_cors_allows_local_frontend_only(self):
        allowed = self.client.get("/api/stocks/AAPL", headers={"Origin": "http://localhost:5173"})
        self.assertEqual(allowed.headers["Access-Control-Allow-Origin"], "http://localhost:5173")
        denied = self.client.get("/api/stocks/AAPL", headers={"Origin": "https://example.com"})
        self.assertNotIn("Access-Control-Allow-Origin", denied.headers)


if __name__ == "__main__":
    unittest.main()
