import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
   <div>
      <h1>Stock Sentiment Analyzer</h1>
      <p>Search for a stock to get started.</p>
    </div>
  );
        
}

export default App
