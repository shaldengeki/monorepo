import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import CardView from './views/CardView';
import CardsView from './views/CardsView';
import HomeView from './views/HomeView';
import UserView from './views/UserView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<HomeView />} />
          <Route path="user/:name" element={<UserView />} />
          <Route path="cards" element={<CardsView />} />
          <Route path="card/:id" element={<CardView />} />
        </Routes>
    </Router>
  );
}

export default App;
