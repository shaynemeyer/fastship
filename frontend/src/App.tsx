import { useState } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState('Placed');

  return (
    <>
      <p>Shipment ID #132039232</p>
      <h2>Status: {status}</h2>

      <button
        onClick={() => {
          setStatus('In Transit');
        }}
      >
        Update Status
      </button>
    </>
  );
}

export default App;
