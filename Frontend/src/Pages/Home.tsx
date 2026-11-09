import Searchbar from "../components/Searchbar";
import Stockcard from "../components/Stockcard";
import { FEATURED_STOCKS } from "../utils/Watchlist";

function Home() {
  return (
    <main className="page">
      <section className="hero">
        <h1>Stock Sentiment Analyzer</h1>
        <p>Look up stock prices, market sentiment, and AI projections.</p>
        <Searchbar />
      </section>

      <section className="stock-section" aria-labelledby="explore-stocks">
        <div className="section-heading">
          <h2 id="explore-stocks">Explore stocks</h2>
          <p>Start with a featured company.</p>
        </div>
        <ul className="stock-list">
          {FEATURED_STOCKS.map((stock) => <Stockcard key={stock.ticker} {...stock} />)}
        </ul>
      </section>
    </main>
  );
}

export default Home;
