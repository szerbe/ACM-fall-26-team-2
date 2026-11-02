"""Download typed FiQA training rows using the Hugging Face Dataset Viewer API.

Example from another backend file:
    from stockdataapi import StockDataAPI

    api = StockDataAPI()
    first_page = api.fetch_rows(offset=0, length=100)
    training_rows = list(api.iter_rows())  # Fetch the entire train split.

Command line (run from the repository root):
    python Backend/stockdataapi.py --output Backend/data/fiqa_train.jsonl

Uses only Python's standard library. No download happens when importing it.
"""

import argparse
import json
import math
import os
import ssl
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class StockDataRow(TypedDict):
    """The seven dataset columns; float and int represent float64 and int64."""

    sentence: str
    snippets: str
    target: str
    sentiment_score: float
    aspects: str
    format: str
    label: int


class DatasetError(RuntimeError):
    """A download failed or the API returned unsuitable training data."""


STRING_FIELDS = ("sentence", "snippets", "target", "aspects", "format")


def _integer(name: str, value: int, minimum: int, maximum: int | None = None) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or (maximum is not None and value > maximum)
    ):
        bounds = f"{minimum}–{maximum}" if maximum is not None else f">= {minimum}"
        raise ValueError(f"{name} must be an integer {bounds}")


def _validate_row(row: object, index: int) -> StockDataRow:
    """Reject missing/null/mistyped fields instead of corrupting training data."""
    if not isinstance(row, dict):
        raise DatasetError(f"Row {index}: expected an object")
    for field in STRING_FIELDS:
        if not isinstance(row.get(field), str):
            raise DatasetError(f"Row {index}: {field} must be a string")

    score = row.get("sentiment_score")
    try:
        valid_score = (
            not isinstance(score, bool)
            and isinstance(score, (int, float))
            and math.isfinite(score)
        )
    except OverflowError:
        valid_score = False
    if not valid_score:
        raise DatasetError(f"Row {index}: sentiment_score must be a finite float64")

    label = row.get("label")
    if isinstance(label, bool) or not isinstance(label, int) or not -(2**63) <= label < 2**63:
        raise DatasetError(f"Row {index}: label must be an int64")

    # Select only the requested fields. Preserve snippets/aspects as raw strings.
    return StockDataRow(
        sentence=row["sentence"], snippets=row["snippets"], target=row["target"],
        sentiment_score=float(score), aspects=row["aspects"],
        format=row["format"], label=label,
    )


class StockDataAPI:
    """Reusable client for a dataset/config/split, defaulting to FiQA training.

    Set HF_TOKEN in the environment, or pass token, if authentication is needed.
    This public dataset normally works without a token. Calls have a timeout;
    network failures raise DatasetError rather than returning an empty dataset.
    """

    ENDPOINT = "https://datasets-server.huggingface.co/rows"

    def __init__(
        self,
        dataset: str = "pauri32/fiqa-2018",
        config: str = "default",
        split: str = "train",
        *,
        timeout: float = 30,
        token: str | None = None,
    ):
        for name, value in (("dataset", dataset), ("config", config), ("split", split)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a positive finite number")
        self.dataset = dataset
        self.config = config
        self.split = split
        self.timeout = timeout
        self._token = os.getenv("HF_TOKEN") if token is None else token
        self._ssl_context = ssl.create_default_context()
        # Some macOS Python installs lack a bundled CA file. Use the system's
        # trusted roots in that case, while retaining HTTPS/hostname checks.
        system_ca = Path("/etc/ssl/cert.pem")
        if (
            ssl.get_default_verify_paths().cafile is None
            and "SSL_CERT_FILE" not in os.environ
            and system_ca.is_file()
        ):
            self._ssl_context.load_verify_locations(cafile=str(system_ca))

    def _fetch_page(self, offset: int, length: int) -> tuple[list[StockDataRow], int]:
        _integer("offset", offset, 0)
        _integer("length", length, 1, 100)
        query = urlencode({
            "dataset": self.dataset, "config": self.config, "split": self.split,
            "offset": offset, "length": length,
        })
        headers = {"Accept": "application/json", "User-Agent": "StockDataAPI/1.0"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        request = Request(f"{self.ENDPOINT}?{query}", headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout, context=self._ssl_context) as response:
                payload = json.load(response)
        except HTTPError as error:
            raise DatasetError(
                f"Hugging Face returned HTTP {error.code} for {self.dataset}/{self.split} "
                f"at offset {offset}. Check dataset access, split, and rate limits."
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise DatasetError(f"Could not reach Hugging Face at offset {offset}; retry the download.") from error
        except (ValueError, UnicodeError) as error:
            raise DatasetError("Hugging Face returned invalid JSON") from error

        if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
            raise DatasetError("Hugging Face response is missing the rows array")
        if payload.get("partial"):
            raise DatasetError("Hugging Face returned a partial dataset; refusing an incomplete download")
        total = payload.get("num_rows_total")
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            raise DatasetError("Hugging Face response is missing a valid num_rows_total")
        entries = payload["rows"]
        if len(entries) > min(length, max(0, total - offset)):
            raise DatasetError("Hugging Face returned an inconsistent page size")
        if not entries and offset < total:
            raise DatasetError(f"Unexpected empty page at offset {offset}; dataset download is incomplete")

        rows = []
        for index, entry in enumerate(entries, start=offset):
            if not isinstance(entry, dict) or entry.get("row_idx") != index:
                raise DatasetError(f"Unexpected row index at offset {index}")
            if entry.get("truncated_cells"):
                raise DatasetError(f"Row {index} contains truncated training data")
            rows.append(_validate_row(entry.get("row"), index))
        return rows, total

    def fetch_rows(self, offset: int = 0, length: int = 100) -> list[StockDataRow]:
        """Fetch one page (1–100 rows), equivalent to the supplied curl request."""
        rows, _ = self._fetch_page(offset, length)
        return rows

    def iter_rows(
        self, *, offset: int = 0, batch_size: int = 100, max_rows: int | None = None,
    ) -> Iterator[StockDataRow]:
        """Yield validated records across pages; max_rows=None reads to the end.

        Materialize with list(api.iter_rows()) for a training library, or iterate
        directly to avoid keeping the entire dataset in memory.
        """
        _integer("offset", offset, 0)
        _integer("batch_size", batch_size, 1, 100)
        if max_rows is not None:
            _integer("max_rows", max_rows, 0)
        fetched = 0
        while max_rows is None or fetched < max_rows:
            length = batch_size if max_rows is None else min(batch_size, max_rows - fetched)
            rows, total = self._fetch_page(offset, length)
            yield from rows
            fetched += len(rows)
            offset += len(rows)
            if offset >= total:
                break


def save_jsonl(rows: Iterator[Mapping], output: str | Path) -> int:
    """Write one JSON record per line. Fail rather than overwrite an existing file.

    If streaming fails, remove the incomplete file so it cannot be mistaken for
    a complete training dataset. JSON preserves numeric values, but does not
    store a column dtype schema; use float64/int64 when creating training tensors.
    """
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("x", encoding="utf-8") as stream:
        try:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                count += 1
        except BaseException:
            path.unlink()
            raise
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Download FiQA rows for sentiment model training.")
    parser.add_argument("--dataset", default="pauri32/fiqa-2018")
    parser.add_argument("--config", default="default")
    parser.add_argument("--split", default="train")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--limit", type=int, help="Maximum rows to download; default: entire split")
    parser.add_argument("--output", type=Path, default=Path("data/fiqa_train.jsonl"))
    args = parser.parse_args()
    try:
        client = StockDataAPI(dataset=args.dataset, config=args.config, split=args.split)
        rows = client.iter_rows(offset=args.offset, batch_size=args.batch_size, max_rows=args.limit)
        count = save_jsonl(rows, args.output)
    except (DatasetError, ValueError, OSError) as error:
        parser.exit(1, f"Download failed: {error}\n")
    print(f"Saved {count} rows to {args.output}")


if __name__ == "__main__":
    main()
