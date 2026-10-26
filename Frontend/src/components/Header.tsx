import { NavLink } from "react-router";



function Header() {
  return (
    <header className = "header">
      <NavLink to = "/" className = "logo">Stock Predictor</NavLink>

      <nav className = "navigation">
        <NavLink to = "/">Home</NavLink>
        <NavLink to = "/watchlist">Saved Stocks</NavLink>
        <NavLink to = "/stock">Stock Details</NavLink>
      </nav>
    </header>
  );
}


export default Header;