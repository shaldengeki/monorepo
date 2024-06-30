import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import ExampleView from './views/ExampleView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<ExampleView />} />
        </Routes>
    </Router>
  );
}

export default App;
