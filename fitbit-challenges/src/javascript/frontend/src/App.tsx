import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import ChallengesListingView from './views/ChallengesListingView';
import ChallengeView from './views/ChallengeView';
import AuthView from './views/AuthView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/challenges" replace />} />
          <Route path="challenges" element={<ChallengesListingView />} />
          <Route path="challenges/:challengeId" element={<ChallengeView />} />
          <Route path="auth" element={<AuthView />} />
        </Routes>
    </Router>
  );
}

export default App;
