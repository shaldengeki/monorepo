import React from 'react';
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
            <div className="text-center">
              <ServerListing />
            </div>
          </Route>
        </Switch>
    </Router>
  );
}

export default App;
