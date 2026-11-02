# FiQA training data loader

`stockdataapi.py` downloads rows from `pauri32/fiqa-2018` using the
[Hugging Face Dataset Viewer API](https://huggingface.co/docs/dataset-viewer/rows).
It uses Python 3.10+ and the standard library, so no new packages are needed.
This retrieves labeled financial text for training; it does not train a model
or retrieve current stock prices.

## Import into your backend or training script

From another Python file inside `Backend`:

```python
from stockdataapi import StockDataAPI, save_jsonl

api = StockDataAPI()  # dataset=pauri32/fiqa-2018, config=default, split=train
first_page = api.fetch_rows(offset=0, length=100)
training_rows = list(api.iter_rows())  # Automatically fetch every page.

sentences = [row["sentence"] for row in training_rows]
classification_labels = [row["label"] for row in training_rows]
regression_scores = [row["sentiment_score"] for row in training_rows]

# Alternatively, stream records into a new training file:
save_jsonl(api.iter_rows(), "data/fiqa_train.jsonl")
```

Use `label` as the target for classification or `sentiment_score` as the target
for sentiment regression. Preserve the dataset's label IDs; the loader does not
guess their meaning or remap them. Do not include your chosen target or another
ground-truth sentiment annotation in model inputs, as that leaks the answers.

## Fields

| Field | Dataset type | Python type |
| --- | --- | --- |
| sentence | string | str |
| snippets | string | str |
| target | string | str |
| sentiment_score | float64 | float |
| aspects | string | str |
| format | string | str |
| label | int64 | int |

`snippets` and `aspects` remain strings even when their contents look like lists.
The client unwraps the API's `rows[].row` objects and returns exactly these seven
columns. It rejects missing/null fields, wrong types, non-finite scores, and labels
outside the signed 64-bit range. JSONL preserves numeric values but does not
store column dtype metadata; explicitly choose float64/int64 when constructing
arrays, dataframes, or tensors if those exact dtypes are required.

## Download from the command line

Run from the repository root:

```sh
# Download the entire train split:
Backend/venv/bin/python Backend/stockdataapi.py --output Backend/data/fiqa_train.jsonl

# Download at most 100 rows, matching the supplied curl request:
Backend/venv/bin/python Backend/stockdataapi.py --limit 100 --output Backend/data/fiqa_sample.jsonl
```

Options: `--dataset`, `--config`, `--split`, `--offset`, `--batch-size`, `--limit`,
and `--output`. The default output path is `data/fiqa_train.jsonl`, relative to
your current directory. `--limit` counts rows, not pages. The page size is 1–100.

Python supports the same controls:

```python
api = StockDataAPI(split="train", timeout=30)
subset = list(api.iter_rows(offset=100, batch_size=50, max_rows=200))
```

Only request split names that exist in the chosen dataset. No token is normally
needed for this public dataset. If needed, set `HF_TOKEN` in your environment or
pass `StockDataAPI(token=...)`; do not put credentials in source files.

Downloads have a per-request timeout and raise `DatasetError` for HTTP/network
errors or malformed/incomplete pages. There are no automatic retries. A failed
streaming export removes the unfinished output file. Existing files are never
overwritten. When consuming `iter_rows()` directly, earlier rows may have already
been yielded before a later request fails; callers should handle that failure.

HTTPS certificate verification stays enabled. If Python has no default CA file,
the client uses `/etc/ssl/cert.pem` when available. You can set `SSL_CERT_FILE` to
a trusted CA bundle for your environment; an explicit setting is respected.

## Verify

From `Backend`:

```sh
venv/bin/python -m unittest discover -s tests -p 'test_stockdataapi.py' -v
```

Tests exercise request construction, pagination, types, errors, and file exports
without contacting Hugging Face.
