import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

function MyComponent() {
  return (
    <div>Hello world!</div>
  )
}

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<MyComponent />} />
        </Routes>
    </Router>
  );
}

export default App;
