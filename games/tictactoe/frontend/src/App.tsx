import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import ExampleView from './views/ExampleView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/example" replace />} />
          <Route path="example" element={<ExampleView />} />
        </Routes>
    </Router>
  );
}

export default App;
