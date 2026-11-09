import { useState } from "react";
import type { SubmitEvent } from "react";
import { useNavigate } from "react-router";
import { isValidTicker, normalizeTicker } from "../utils/stockApi";

function Searchbar() {
  const navigate = useNavigate();
  const [ticker, setTicker] = useState("");
  const [invalid, setInvalid] = useState(false);

  function handleSearch(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const symbol = normalizeTicker(ticker);

    if (!isValidTicker(symbol)) {
      setInvalid(true);
      return;
    }

    navigate(`/stock/${encodeURIComponent(symbol)}`);
  }

  return (
    <form className="ticker-search" onSubmit={handleSearch}>
      <label htmlFor="ticker-search">Stock ticker</label>
      <div className="search-controls">
        <input
          id="ticker-search"
          placeholder="e.g. AAPL"
          value={ticker}
          autoCapitalize="characters"
          autoComplete="off"
          spellCheck={false}
          aria-invalid={invalid}
          aria-describedby={invalid ? "ticker-error" : undefined}
          onChange={(event) => {
            setTicker(event.target.value);
            setInvalid(false);
          }}
        />
        <button className="button button-primary" type="submit">Search</button>
      </div>
      {invalid && (
        <p className="form-error" id="ticker-error" role="alert">
          Enter a ticker up to 20 characters, starting with a letter or number.
          Only letters, numbers, dots, and hyphens are allowed.
        </p>
      )}
    </form>
  );
}

export default Searchbar;
