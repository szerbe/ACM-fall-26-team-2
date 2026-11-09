import { Link } from "react-router";

type StockCardProps = {
  ticker: string;
  name?: string;
  onRemove?: () => void;
};

function Stockcard({ ticker, name, onRemove }: StockCardProps) {
  return (
    <li className="stock-row">
      <Link className="stock-link" to={`/stock/${encodeURIComponent(ticker)}`}>
        <span className="stock-identity">
          <strong>{ticker}</strong>
          {name && <span>{name}</span>}
        </span>
        <span className="stock-action">
          <span className="stock-action-label">View analysis</span>
          <span aria-hidden="true">→</span>
        </span>
      </Link>
      {onRemove && (
        <button className="button" onClick={onRemove} aria-label={`Remove ${ticker}`}>
          Remove
        </button>
      )}
    </li>
  );
}

export default Stockcard;
