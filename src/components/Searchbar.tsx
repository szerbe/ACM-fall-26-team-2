import { useState } from "react";


function Searchbar() { 
    const [ticker, setTicker] = useState("");

    function handleSearch() {
        // Implement search functionality here
        console.log(`Searching for stock: ${ticker}`);
    }
    return( 
        <div>   
            <input 
                placeholder = "Search for a stock..." 
                value = {ticker}
                onChange = {(event) => setTicker(event.target.value)}
            />
            <button onClick={handleSearch}> Search </button>
        </div>
    );
}

export default Searchbar;

