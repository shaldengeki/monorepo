import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

import TransactionDisplay from './components/TransactionDisplay';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<div className="text-center">
              <TransactionDisplay />
            </div>}>
          </Route>
        </Routes>
    </Router>
  );
}

export default App;
