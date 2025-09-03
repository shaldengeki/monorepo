import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import logo192 from './logo192.png';
import ExampleView from './views/ExampleView';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/example" replace />} />
          <Route path="example" element={<ExampleView logo={logo192} />} />
        </Routes>
    </Router>
  );
}

export default App;
