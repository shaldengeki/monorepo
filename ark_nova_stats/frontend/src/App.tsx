import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import HomeView from './views/HomeView';
import UserView from './views/UserView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<HomeView />} />
          <Route path="user/:name" element={<UserView />} />
        </Routes>
    </Router>
  );
}

export default App;
