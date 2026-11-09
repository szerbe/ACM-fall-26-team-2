import { NavLink } from "react-router";

function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <NavLink to="/" className="logo">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
            <path d="M3 17l6-6 4 4 7-8m-5 0h5v5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Stock Predictor
        </NavLink>
        <nav className="navigation" aria-label="Main navigation">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/watchlist">Saved stocks</NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;
