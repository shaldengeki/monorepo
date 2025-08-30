import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import logo192 from './logo192.png';
import GameView from './views/GameView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/example" replace />} />
          <Route path="example" element={<GameView logo={logo192} />} />
        </Routes>
    </Router>
  );
}

export default App;
