import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

function App() {
  return (
    <Router>
        <Switch>
          <Route path="/">
            <div className="text-center">
            </div>
          </Route>
        </Switch>
    </Router>
  );
}

export default App;
