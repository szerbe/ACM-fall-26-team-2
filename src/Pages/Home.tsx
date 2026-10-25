import {useNavigate} from 'react-router';


const stocks = [
  { ticker: "AAPL", name: "Apple Inc." },
  { ticker: "MSFT", name: "Microsoft Corporation" },
  { ticker: "NVDA", name: "NVIDIA Corporation" },
  { ticker: "GOOGL", name: "Alphabet Inc." },
];

function Home() { 
    const navigate = useNavigate();
    
    return (
        <main className="home">
      <section className="hero">
        <h1>Stock Sentiment Analyzer</h1>
        <p>
          Explore stocks, analyze market sentiment, and view AI projections.
        </p>
      </section>

      <section className="stock-list">
        <h2>Explore Stocks</h2>

        <div className="stock-grid">
          {stocks.map((stock) => (
            <button
              className="stock-card"
              key={stock.ticker}
              onClick={() => navigate(`/stock/${stock.ticker}`)}
            >
              <h3>{stock.ticker}</h3>
              <p>{stock.name}</p>
              <span>View analysis →</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
export default Home;