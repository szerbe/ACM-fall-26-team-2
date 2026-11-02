"""Offline checks for the dataset loader's data and pagination contracts."""

import io
import json
import ssl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse

from stockdataapi import DatasetError, StockDataAPI, save_jsonl


def record(index=0):
    return {
        "sentence": f"Example {index}", "snippets": "['Example']", "target": "TEST",
        "sentiment_score": -0.543, "aspects": "['Stock/Price Action']",
        "format": "post", "label": 2,
    }


def page(offset=0, length=2, total=2):
    return {
        "rows": [{"row_idx": i, "row": record(i), "truncated_cells": []}
                 for i in range(offset, min(offset + length, total))],
        "num_rows_total": total, "partial": False,
    }


def response(payload):
    return io.BytesIO(json.dumps(payload).encode())


class StockDataAPITests(unittest.TestCase):
    def test_fetch_request_and_field_types(self):
        with patch("stockdataapi.urlopen", return_value=response(page())) as get:
            rows = StockDataAPI(token="test-token").fetch_rows(length=2)
        request = get.call_args.args[0]
        self.assertEqual(parse_qs(urlparse(request.full_url).query), {
            "dataset": ["pauri32/fiqa-2018"], "config": ["default"],
            "split": ["train"], "offset": ["0"], "length": ["2"],
        })
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(get.call_args.kwargs["timeout"], 30)
        context = get.call_args.kwargs["context"]
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        self.assertEqual(rows[0], record())
        self.assertIsInstance(rows[0]["sentiment_score"], float)
        self.assertIsInstance(rows[0]["label"], int)
        self.assertIsInstance(rows[0]["snippets"], str)
        self.assertIsInstance(rows[0]["aspects"], str)

    def test_pagination_limit_and_offset(self):
        def fake_get(request, **kwargs):
            query = parse_qs(urlparse(request.full_url).query)
            return response(page(int(query["offset"][0]), int(query["length"][0]), total=961))

        with patch("stockdataapi.urlopen", side_effect=fake_get) as get:
            rows = list(StockDataAPI().iter_rows(offset=10, batch_size=100, max_rows=205))
        self.assertEqual(len(rows), 205)
        self.assertEqual(rows[0]["sentence"], "Example 10")
        self.assertEqual(rows[-1]["sentence"], "Example 214")
        queries = [parse_qs(urlparse(call.args[0].full_url).query) for call in get.call_args_list]
        self.assertEqual([q["offset"] for q in queries], [["10"], ["110"], ["210"]])
        self.assertEqual([q["length"] for q in queries], [["100"], ["100"], ["5"]])

    def test_full_download_stops_at_total(self):
        with patch("stockdataapi.urlopen", side_effect=[response(page(0, 2, 3)), response(page(2, 2, 3))]) as get:
            rows = list(StockDataAPI().iter_rows(batch_size=2))
        self.assertEqual(len(rows), 3)
        self.assertEqual(get.call_count, 2)

    def test_no_network_for_zero_limit(self):
        with patch("stockdataapi.urlopen") as get:
            self.assertEqual(list(StockDataAPI().iter_rows(max_rows=0)), [])
        get.assert_not_called()

    def test_invalid_parameters(self):
        with patch("stockdataapi.urlopen") as get:
            for kwargs in ({"offset": -1}, {"length": 101}, {"length": 0}, {"offset": True}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    StockDataAPI().fetch_rows(**kwargs)
            for kwargs in ({"batch_size": 101}, {"max_rows": -1}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    list(StockDataAPI().iter_rows(**kwargs))
        get.assert_not_called()

    def test_invalid_training_fields(self):
        for field, bad_value in (
            ("sentence", None), ("snippets", []), ("target", 1), ("aspects", {}),
            ("format", None), ("sentiment_score", "0.5"), ("sentiment_score", float("nan")),
            ("sentiment_score", True), ("label", 2.5), ("label", True), ("label", 2**63),
        ):
            payload = page()
            payload["rows"][0]["row"][field] = bad_value
            with self.subTest(field=field, value=bad_value), \
                 patch("stockdataapi.urlopen", return_value=response(payload)), \
                 self.assertRaisesRegex(DatasetError, field):
                StockDataAPI().fetch_rows()

    def test_incomplete_or_malformed_pages_are_rejected(self):
        bad_pages = [{}, {"rows": [], "num_rows_total": 2}, {**page(), "partial": True}]
        truncated = page()
        truncated["rows"][0]["truncated_cells"] = ["sentence"]
        wrong_index = page()
        wrong_index["rows"][0]["row_idx"] = 10
        for payload in [*bad_pages, truncated, wrong_index]:
            with self.subTest(payload=payload), \
                 patch("stockdataapi.urlopen", return_value=response(payload)), \
                 self.assertRaises(DatasetError):
                StockDataAPI().fetch_rows()

    def test_request_failures_are_actionable(self):
        for error in (
            URLError("network unavailable"), TimeoutError(),
            HTTPError("https://example.com", 429, "Too Many Requests", {}, None),
        ):
            with self.subTest(error=error), patch("stockdataapi.urlopen", side_effect=error), \
                 self.assertRaises(DatasetError):
                StockDataAPI().fetch_rows()
        with patch("stockdataapi.urlopen", return_value=io.BytesIO(b"not JSON")), \
             self.assertRaisesRegex(DatasetError, "invalid JSON"):
            StockDataAPI().fetch_rows()

    def test_export_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "training.jsonl"
            self.assertEqual(save_jsonl(iter([record()]), output), 1)
            self.assertEqual(json.loads(output.read_text()), record())
            with self.assertRaises(FileExistsError):
                save_jsonl(iter([]), output)
            self.assertEqual(json.loads(output.read_text()), record())

    def test_failed_stream_removes_incomplete_export(self):
        def broken_rows():
            yield record()
            raise DatasetError("Second page failed")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "training.jsonl"
            with self.assertRaises(DatasetError):
                save_jsonl(broken_rows(), output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
