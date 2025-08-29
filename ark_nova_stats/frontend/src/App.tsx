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
import logo192 from './logo192.png';
import PageContainer from '../../../react_library/PageContainer';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<PageContainer logo={logo192}><HomeView /></PageContainer>} />
          <Route path="user/:name" element={<PageContainer logo={logo192}><UserView /></PageContainer>} />
          <Route path="cards" element={<PageContainer logo={logo192}><CardsView /></PageContainer>} />
          <Route path="card/:id" element={<PageContainer logo={logo192}><CardView /></PageContainer>} />
          <Route path="emu_cup" element={<PageContainer logo={logo192}><EmuCupView /></PageContainer>} />
        </Routes>
    </Router>
  );
}

export default App;
