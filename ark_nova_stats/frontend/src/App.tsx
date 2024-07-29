import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import HomeView from './views/HomeView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<HomeView />} />
        </Routes>
    </Router>
  );
}

export default App;
