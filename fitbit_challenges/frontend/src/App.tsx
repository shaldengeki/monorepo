import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import { useQuery } from "@apollo/client/react";
import ChallengesListingView from './views/ChallengesListingView';
import ChallengeView from './views/ChallengeView';
import AuthView from './views/AuthView';
import logo192 from './logo192.png';
import fitbit from './fitbit.png';
import NavBar, {NavBarElement} from '../../../react_library/NavBar';
import PageContainer from '../../../react_library/PageContainer';
import { FETCH_CURRENT_USER_QUERY } from "./queries";

function App() {
    const { loading, error, data } = useQuery(
        FETCH_CURRENT_USER_QUERY,
    );

  const navbar = (
    <NavBar logo={logo192}>
      <NavBarElement link={'/challenges'} text={"Challenges"} />
      {
          loading && <p>Loading...</p>
      }
      {
          error && <p>Error loading login state</p>
      }
      {
          // @ts-ignore
          data && data.currentUser === null &&
          <NavBarElement link={'/auth'}>
              <img className="h-5 inline" src={fitbit} alt="Fitbit app icon" />
              <span className="font-bold">Sign in with Fitbit</span>
          </NavBarElement>
      }
      {
          // @ts-ignore
          data && data.currentUser && <p className="ml-auto">{data.currentUser.displayName}</p>
      }
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
