import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import TransactionDisplay from './components/TransactionDisplay';

function App() {
  return (
    <Router>
        <Switch>
          <Route path="/">
            <div className="text-center">
              <TransactionDisplay />
            </div>
          </Route>
        </Switch>
    </Router>
  );
}

export default App;
