import React from 'react';
import './App.css';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import ServerListing from './components/ServerListing';

function App() {
  return (
    <Router>
        <Switch>
          <Route path="/">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="col-span-3">
                <ServerListing />
              </div>
            </div>
          </Route>
        </Switch>
    </Router>
  );
}

export default App;
