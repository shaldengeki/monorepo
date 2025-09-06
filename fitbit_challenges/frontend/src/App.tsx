import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import ChallengesListingView from './views/ChallengesListingView';
import ChallengeView from './views/ChallengeView';
import AuthView from './views/AuthView';
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
          <Route path="/" element={<Navigate to="/challenges" replace />} />
          <Route path="challenges" element={<PageContainer navbar={navbar}><ChallengesListingView /></PageContainer>} />
          <Route path="challenges/:challengeId" element={<PageContainer navbar={navbar}><ChallengeView /></PageContainer>} />
          <Route path="auth" element={<PageContainer navbar={navbar}><AuthView /></PageContainer>} />
        </Routes>
    </Router>
  );
}

export default App;
