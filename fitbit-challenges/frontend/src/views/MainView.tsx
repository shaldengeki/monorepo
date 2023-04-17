import React from 'react';
import { useQuery, gql } from '@apollo/client';
import WorkweekHustle from '../components/WorkweekHustle';

export const TEST_QUERY = gql`
  query Test {
    test
  }
`;

const MainView = () => {
  const { loading, error, data } = useQuery(TEST_QUERY);

  if (loading) return <p>Loading...</p>;

  if (error) return <p>Error : {error.message}</p>;

  return (
    <div className="container mx-auto">
        <WorkweekHustle />
        <div>{data.test}</div>
    </div>
  )
}

export default MainView;
