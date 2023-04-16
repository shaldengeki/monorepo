import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

import MainView from './views/MainView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<MainView />} />
        </Routes>
    </Router>
  );
}

export default App;
