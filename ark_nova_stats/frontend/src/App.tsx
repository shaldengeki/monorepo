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
import EmuCupView from './views/EmuCupView';
import PageContainer from './components/PageContainer';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<PageContainer><HomeView /></PageContainer>} />
          <Route path="user/:name" element={<PageContainer><UserView /></PageContainer>} />
          <Route path="cards" element={<PageContainer><CardsView /></PageContainer>} />
          <Route path="card/:id" element={<PageContainer><CardView /></PageContainer>} />
          <Route path="emu_cup" element={<PageContainer><EmuCupView /></PageContainer>} />
        </Routes>
    </Router>
  );
}

export default App;
