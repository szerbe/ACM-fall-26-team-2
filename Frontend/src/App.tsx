import { BrowserRouter as Router, Routes, Route } from 'react-router';
import Header from './components/Header';
import Home from './Pages/Home';
import Watchlist from './Pages/Watchlist';
import './App.css';
import StockAnalysis from './Pages/StockAnalysis';
function App() {
  return (
    <Router>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route 
          path="/stock/:ticker" element={<StockAnalysis />} />
        </Routes>
    </Router>
  );
}

export default App;

  
