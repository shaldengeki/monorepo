import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

import MainView from './views/MainView';
import ChallengeView from './views/ChallengeView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<MainView />} />
          <Route path="challenges/:challengeId" element={<ChallengeView />} />
        </Routes>
    </Router>
  );
}

export default App;
