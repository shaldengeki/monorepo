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
import NavBar, {NavBarElement} from '../../../react_library/NavBar';
import PageContainer from '../../../react_library/PageContainer';

function App() {
  const navbar = (
    <NavBar logo={logo192} title="Ark Nova Games Database">
      <NavBarElement link={'/emu_cup'} text={"Emu Cup"} />
      <NavBarElement link={'/cards'} text={"Cards"} />
    </NavBar>
  )

  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="home" element={<PageContainer navbar={navbar}><HomeView /></PageContainer>} />
          <Route path="user/:name" element={<PageContainer navbar={navbar}><UserView /></PageContainer>} />
          <Route path="cards" element={<PageContainer navbar={navbar}><CardsView /></PageContainer>} />
          <Route path="card/:id" element={<PageContainer navbar={navbar}><CardView /></PageContainer>} />
          <Route path="emu_cup" element={<PageContainer navbar={navbar}><EmuCupView /></PageContainer>} />
        </Routes>
    </Router>
  );
}

export default App;
