import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

import { useQuery, gql } from '@apollo/client';

const TEST_QUERY = gql`
  query Test {
    test
  }
`;

function MyComponent() {
  const { loading, error, data } = useQuery(TEST_QUERY);

  if (loading) return <p>Loading...</p>;

  if (error) return <p>Error : {error.message}</p>;

  return (
    <div>{data.test}</div>
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
